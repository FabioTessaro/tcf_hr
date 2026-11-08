"""Notifications of the current user (PWA Notification records created by hrms)."""

import html
import re

import frappe

_TAG = re.compile(r"(</?(?:strong|b)\s*>)", re.IGNORECASE)
_OPEN_BOLD = {"<strong>", "<b>"}
_CLOSE_BOLD = {"</strong>", "</b>"}
_ANY_TAG = re.compile(r"<[^>]*>")

MAX_PAGE_LENGTH = 100


def parse_message(message: str | None) -> list[dict]:
	"""Turn the stored HTML into `[{"text": ..., "bold": bool}]`.

	Only bold survives. Every other tag is dropped and entities are decoded, so the frontend renders plain
	text spans and never needs `v-html` (messages embed user-supplied names).
	"""
	parts, bold = [], False
	for token in _TAG.split(message or ""):
		lowered = token.replace(" ", "").lower()
		if lowered in _OPEN_BOLD:
			bold = True
		elif lowered in _CLOSE_BOLD:
			bold = False
		else:
			text = html.unescape(_ANY_TAG.sub("", token))
			if text:
				parts.append({"text": text, "bold": bold})
	return parts


@frappe.whitelist(methods=["GET"])
def get_notifications(start: int = 0, page_length: int = 20) -> list[dict]:
	rows = frappe.get_all(
		"PWA Notification",
		filters={"to_user": frappe.session.user},
		fields=[
			"name",
			"from_user",
			"message",
			"read",
			"creation",
			"reference_document_type",
			"reference_document_name",
		],
		order_by="creation desc",
		start=max(int(start), 0),
		page_length=min(max(int(page_length), 1), MAX_PAGE_LENGTH),
	)
	for row in rows:
		row["message"] = parse_message(row["message"])
	return rows


@frappe.whitelist(methods=["GET"])
def get_unread_count() -> int:
	return frappe.db.count("PWA Notification", {"to_user": frappe.session.user, "read": 0})


@frappe.whitelist(methods=["POST"])
def mark_read(names) -> None:
	names = [n for n in frappe.parse_json(names) if isinstance(n, str)]
	if names:
		frappe.db.set_value(
			"PWA Notification",
			{"to_user": frappe.session.user, "name": ("in", names)},
			"read",
			1,
			update_modified=False,
		)


@frappe.whitelist(methods=["POST"])
def mark_all_read() -> None:
	frappe.db.set_value(
		"PWA Notification",
		{"to_user": frappe.session.user, "read": 0},
		"read",
		1,
		update_modified=False,
	)
