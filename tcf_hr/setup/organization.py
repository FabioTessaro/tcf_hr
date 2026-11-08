"""Create the Branches, Departments and Designations listed in `config/organization.json`.

Create-if-missing only: existing records are never edited or deleted, so anything changed in
the desk afterwards is preserved. Departments are created without a company, so their names
carry no abbreviation suffix.
"""

import frappe
from frappe.utils.nestedset import get_root_of

from tcf_hr.setup.config import load_config


def apply_organization():
	config = load_config("organization")
	_create_simple("Branch", "branch", config.get("branches") or [])
	_create_simple("Designation", "designation_name", config.get("designations") or [])
	_create_departments(config.get("departments") or [])


def _create_simple(doctype: str, field: str, names: list[str]):
	for name in names:
		if not frappe.db.exists(doctype, name):
			frappe.get_doc({"doctype": doctype, field: name}).insert(ignore_permissions=True)


def _create_departments(departments: list[dict]):
	root = get_root_of("Department")
	if not root:
		# Root is created with the first Company; apply_organization runs again afterwards.
		return

	pending = [{"name": d, "parent": root} if isinstance(d, str) else d for d in departments]
	pending = [{**d, "parent": d.get("parent") or root} for d in pending]

	# Multi-pass so a child can be listed before its parent.
	while pending:
		remaining = []
		for dept in pending:
			parent = dept["parent"]
			if parent != root and not frappe.db.exists("Department", parent):
				remaining.append(dept)
				continue
			if not frappe.db.exists("Department", dept["name"]):
				if not frappe.db.get_value("Department", parent, "is_group"):
					frappe.db.set_value("Department", parent, "is_group", 1)
				frappe.get_doc(
					{
						"doctype": "Department",
						"department_name": dept["name"],
						"parent_department": parent,
					}
				).insert(ignore_permissions=True)
		if len(remaining) == len(pending):
			frappe.log_error(
				f"Unknown parent department(s): {[d['parent'] for d in remaining]}",
				"tcf_hr organization.json",
			)
			return
		pending = remaining
