"""Allowlisted generic document API for the HR app.

The HR app must be reachable from outside the company network, where the generic desk APIs
(`frappe.client.*`, `frappe.desk.*`, `/api/resource`) are blocked. This module replaces what the
app needs from them, restricted to the doctypes and operations in `config/gateway.json`.

Rules:
- Every call is permission-checked by Frappe (never `ignore_permissions`); the allowlist only
  narrows what the generic API could do.
- Requested fields are clamped to the fields the user may read/write.
- Doctypes or operations that are not in the config are rejected.
"""

import re

import frappe
from frappe import _
from frappe.model import get_permitted_fields

from tcf_hr.setup.config import load_config

MAX_PAGE_LENGTH = 200
MAX_LINK_PAGE_LENGTH = 20

_FIELDNAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

# Keys a client must never set on a document or child row. `name` and `modified` are writable fields
# as far as Frappe is concerned, so they are stripped here; `save_doc` re-adds `modified` on updates.
_PROTECTED_KEYS = {
	"name",
	"owner",
	"creation",
	"modified",
	"modified_by",
	"docstatus",
	"idx",
	"parent",
	"parenttype",
	"parentfield",
}


# --- pure helpers (unit tested) -------------------------------------------------------------


def allowed_ops(config: dict, doctype: str) -> set[str]:
	return set((config.get("doctypes", {}).get(doctype) or {}).get("ops", []))


def clamp_fields(requested, permitted) -> list[str]:
	"""Keep only plain field names the user may read. Raises on anything else (no SQL, no aliases)."""
	permitted = set(permitted)
	fields = []
	for field in requested or ["name"]:
		if not isinstance(field, str) or not _FIELDNAME.match(field) or field not in permitted:
			raise frappe.PermissionError(_("Field {0} is not available").format(field))
		fields.append(field)
	return fields


def clean_payload(data: dict, writable, table_fields) -> dict:
	"""Drop protected and non-writable keys; clean the rows of child tables."""
	writable, table_fields = set(writable), set(table_fields)
	cleaned = {}
	for key, value in data.items():
		if key in _PROTECTED_KEYS or (key not in writable and key not in table_fields):
			continue
		if key in table_fields:
			rows = value if isinstance(value, list) else []
			value = [
				{k: v for k, v in row.items() if k not in _PROTECTED_KEYS and k != "doctype"}
				for row in rows
				if isinstance(row, dict)
			]
		cleaned[key] = value
	return cleaned


# --- guards ---------------------------------------------------------------------------------


def _check(doctype: str, op: str):
	if op not in allowed_ops(load_config("gateway"), doctype):
		frappe.throw(_("Not permitted"), frappe.PermissionError)


def _check_known(doctype: str):
	config = load_config("gateway")
	if doctype not in config.get("doctypes", {}) and doctype not in config.get("child_doctypes", []):
		frappe.throw(_("Not permitted"), frappe.PermissionError)


def _load(doctype: str, name: str, ptype: str, op: str):
	_check(doctype, op)
	doc = frappe.get_doc(doctype, name)
	doc.check_permission(ptype)
	return doc


def _table_fields(doctype: str) -> list[str]:
	return [df.fieldname for df in frappe.get_meta(doctype).get_table_fields()]


# --- reads ----------------------------------------------------------------------------------


@frappe.whitelist(methods=["GET", "POST"])
def get_list(
	doctype: str,
	fields=None,
	filters=None,
	or_filters=None,
	order_by: str | None = None,
	start: int = 0,
	page_length: int = 20,
):
	_check(doctype, "read")
	fields = clamp_fields(frappe.parse_json(fields) if fields else None, get_permitted_fields(doctype))
	return frappe.get_list(
		doctype,
		fields=fields,
		filters=frappe.parse_json(filters) if filters else None,
		or_filters=frappe.parse_json(or_filters) if or_filters else None,
		order_by=order_by or "modified desc",
		limit_start=max(int(start), 0),
		limit_page_length=min(max(int(page_length), 1), MAX_PAGE_LENGTH),
	)


@frappe.whitelist(methods=["GET", "POST"])
def get_count(doctype: str, filters=None) -> int:
	_check(doctype, "read")
	rows = frappe.get_list(
		doctype, fields=["count(name) as count"], filters=frappe.parse_json(filters) if filters else None
	)
	return rows[0].count if rows else 0


@frappe.whitelist(methods=["GET", "POST"])
def get_doc(doctype: str, name: str) -> dict:
	doc = _load(doctype, name, "read", "read")
	doc.apply_fieldlevel_read_permissions()
	return doc.as_dict()


@frappe.whitelist(methods=["GET", "POST"])
def get_doc_permissions(doctype: str, name: str) -> dict:
	doc = _load(doctype, name, "read", "read")
	return {
		ptype: bool(doc.has_permission(ptype)) for ptype in ("read", "write", "submit", "cancel", "delete")
	}


@frappe.whitelist(methods=["GET", "POST"])
def get_meta(doctype: str) -> dict:
	"""Form metadata for an allowlisted doctype (or one of its allowlisted child tables)."""
	from hrms.api import get_doctype_fields, get_doctype_states, get_workflow

	_check_known(doctype)
	return {
		"fields": get_doctype_fields(doctype),
		"states": get_doctype_states(doctype),
		"writable_fields": get_permitted_fields(doctype, permission_type="write"),
		"workflow": get_workflow(doctype),
	}


@frappe.whitelist(methods=["GET", "POST"])
def search_link(doctype: str, txt: str = "", filters=None, page_length: int = 10):
	config = load_config("gateway")
	if doctype not in config.get("link_doctypes", []) and doctype not in config.get("doctypes", {}):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	from frappe.desk.search import search_link as _search_link

	return _search_link(
		doctype, txt or "", filters=filters, page_length=min(max(int(page_length), 1), MAX_LINK_PAGE_LENGTH)
	)


# --- writes ---------------------------------------------------------------------------------


@frappe.whitelist(methods=["POST"])
def save_doc(doc) -> dict:
	"""Insert (no `name`) or update (with `name`) an allowlisted doctype."""
	data = frappe.parse_json(doc)
	doctype, name = data.get("doctype"), data.get("name")
	if not isinstance(doctype, str):
		frappe.throw(_("Invalid document"), frappe.ValidationError)

	_check(doctype, "write" if name else "create")
	payload = clean_payload(
		data, get_permitted_fields(doctype, permission_type="write"), _table_fields(doctype)
	)

	if name:
		current = frappe.get_doc(doctype, name)
		current.check_permission("write")
		if data.get("modified"):
			payload["modified"] = data["modified"]  # enables Frappe's concurrent-edit check
		current.update(payload)
		current.save()
		saved = current
	else:
		saved = frappe.get_doc({"doctype": doctype, **payload}).insert()

	saved.apply_fieldlevel_read_permissions()
	return saved.as_dict()


@frappe.whitelist(methods=["POST"])
def submit(doctype: str, name: str) -> dict:
	doc = _load(doctype, name, "submit", "submit")
	doc.submit()
	return doc.as_dict()


@frappe.whitelist(methods=["POST"])
def cancel(doctype: str, name: str) -> dict:
	doc = _load(doctype, name, "cancel", "cancel")
	doc.cancel()
	return doc.as_dict()


@frappe.whitelist(methods=["POST"])
def delete(doctype: str, name: str) -> dict:
	_load(doctype, name, "delete", "delete")
	frappe.delete_doc(doctype, name)
	return {"name": name}


# --- workflow -------------------------------------------------------------------------------


@frappe.whitelist(methods=["GET", "POST"])
def get_transitions(doctype: str, name: str) -> list[dict]:
	from frappe.model.workflow import get_transitions as _get_transitions

	doc = _load(doctype, name, "read", "read")
	return _get_transitions(doc)


@frappe.whitelist(methods=["POST"])
def apply_workflow(doctype: str, name: str, action: str) -> dict:
	from frappe.model.workflow import apply_workflow as _apply_workflow

	doc = _load(doctype, name, "read", "read")
	return _apply_workflow(doc, action).as_dict()
