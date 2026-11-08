"""Per-employee policy for the HR app.

Everything the app may hide or disable is decided here and exposed to the frontend through
`capabilities()`. The frontend only reads flags; the server enforces them.
"""

import frappe
from frappe import _

# Doctypes of the "Requests" section of the HR app (all must be in config/gateway.json)
REQUEST_DOCTYPES = [
	"Leave Application",
	"Compensatory Leave Request",
	"Expense Claim",
	"Employee Advance",
	"Attendance Request",
	"Shift Request",
]


def get_employee(user: str | None = None) -> str | None:
	"""Active Employee linked to `user` (default: the session user)."""
	return frappe.db.get_value(
		"Employee", {"user_id": user or frappe.session.user, "status": "Active"}, "name"
	)


def can_check_in(employee: str | None) -> bool:
	"""Whether `employee` may check in from the app.

	Everyone can for now. A future rule (e.g. a work-from-home flag on Employee) only
	changes this function: the API, the validate hook and the capabilities all call it.
	"""
	return True


def is_approver(user: str, employee: str | None) -> bool:
	"""True if the user can see "Team Requests" (manager or department approver)."""
	if employee and frappe.db.exists("Employee", {"reports_to": employee, "status": "Active"}):
		return True
	return bool(frappe.db.exists("Department Approver", {"approver": user}))


def capabilities(employee: str | None) -> dict:
	"""Feature flags for the current user. Never trusted by the server, only used to shape the UI."""
	settings = frappe.db.get_singles_dict("HR Settings", cast=True)
	return {
		"check_in": bool(
			employee and settings.allow_employee_checkin_from_mobile_app and can_check_in(employee)
		),
		"geolocation": bool(settings.allow_geolocation_tracking),
		"multi_currency_claims": bool(settings.enable_multi_currency_expense_claim),
		"team_requests": is_approver(frappe.session.user, employee),
		# Request types this user may read, with whether they may also create one
		"requests": {
			doctype: {"create": bool(frappe.has_permission(doctype, "create"))}
			for doctype in REQUEST_DOCTYPES
			if frappe.has_permission(doctype, "read")
		},
		"payslips": bool(frappe.has_permission("Salary Slip", "read")),
		"roster": bool(frappe.has_permission("Shift Schedule Assignment", "read")),
		"roster_edit": bool(frappe.has_permission("Shift Schedule Assignment", "create")),
	}


def validate_employee_checkin(doc, method=None):
	"""Employee Checkin validate hook: enforce `can_check_in` on self check-ins.

	Only new records created by the employee for themselves are checked, so device/biometric
	imports and HR users working on other employees are unaffected.
	"""
	if not doc.is_new() or frappe.session.user in ("Administrator",):
		return
	employee = get_employee()
	if employee and doc.employee == employee and not can_check_in(employee):
		frappe.throw(_("You are not allowed to check in from the app."), frappe.PermissionError)
