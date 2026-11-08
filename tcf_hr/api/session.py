import frappe
from frappe.sessions import get_csrf_token
from frappe.utils import get_fullname

from tcf_hr import policy


@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_bootstrap() -> dict:
	"""Everything the HR app needs to start: user, employee, capabilities, CSRF token.

	Guests get `is_guest` only; the shell page already redirects them to the login.
	"""
	user = frappe.session.user
	if user == "Guest":
		return {"is_guest": True, "lang": str(frappe.local.lang)}

	employee = policy.get_employee(user)
	employee_info = None
	if employee:
		employee_info = frappe.db.get_value(
			"Employee",
			employee,
			[
				"name",
				"first_name",
				"employee_name",
				"designation",
				"department",
				"company",
				"reports_to",
				"image",
			],
			as_dict=True,
		)

	return {
		"is_guest": False,
		"user": {
			"name": user,
			"full_name": get_fullname(user),
			"image": frappe.db.get_value("User", user, "user_image"),
		},
		"employee": employee_info,
		"capabilities": policy.capabilities(employee),
		"lang": str(frappe.local.lang),
		"csrf_token": get_csrf_token(),
	}
