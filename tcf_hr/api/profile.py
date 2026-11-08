"""Profile of the current employee: a fixed, readable subset of the Employee record."""

import frappe

from tcf_hr import policy

# Add a field here to show it on the profile page. Field-level permissions still apply.
PROFILE_FIELDS = [
	"employee_name",
	"image",
	"designation",
	"department",
	"branch",
	"employment_type",
	"company",
	"date_of_joining",
	"cell_number",
	"company_email",
]


def compact(values: dict) -> dict:
	"""Drop empty values so the page only shows what exists."""
	return {key: value for key, value in values.items() if value not in (None, "", 0)}


@frappe.whitelist(methods=["GET"])
def get_profile() -> dict:
	user = frappe.session.user
	employee = policy.get_employee(user)
	if not employee:
		frappe.throw(frappe._("No active employee is linked to your account."), frappe.PermissionError)

	doc = frappe.get_doc("Employee", employee)
	doc.check_permission("read")
	doc.apply_fieldlevel_read_permissions()  # blanks what this user may not read

	profile = compact({field: doc.get(field) for field in PROFILE_FIELDS})
	profile["name"] = employee
	profile["email"] = user
	# Fall back to the user's own picture when the employee record has none
	if "image" not in profile:
		image = frappe.db.get_value("User", user, "user_image")
		if image:
			profile["image"] = image
	if doc.reports_to:
		profile["reports_to"] = doc.reports_to
		profile["reports_to_name"] = frappe.db.get_value("Employee", doc.reports_to, "employee_name")
	return profile
