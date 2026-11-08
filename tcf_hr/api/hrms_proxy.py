"""Thin delegates to hrms helpers used by the request forms.

The logic stays in hrms (so updates flow through) and so do its permission checks; this module only makes the
helpers reachable under the `tcf_hr.api` namespace, the one namespace allowed from outside the company network.
Nothing here takes a doctype argument, so there is nothing to allowlist.
"""

import frappe


@frappe.whitelist(methods=["GET", "POST"])
def get_leave_types(employee: str, date: str | None = None) -> list:
	from hrms.api import get_leave_types as _get

	return _get(employee, date)


@frappe.whitelist(methods=["GET", "POST"])
def get_leave_balance_map() -> dict:
	from hrms.api import get_leave_balance_map as _get

	return _get()


@frappe.whitelist(methods=["GET", "POST"])
def get_leave_approval_details(employee: str) -> dict:
	from hrms.api import get_leave_approval_details as _get

	return _get(employee)


@frappe.whitelist(methods=["GET", "POST"])
def get_number_of_leave_days(
	employee: str, leave_type: str, from_date: str, to_date: str, half_day=None, half_day_date=None
) -> float:
	from hrms.hr.doctype.leave_application.leave_application import get_number_of_leave_days as _get

	return _get(employee, leave_type, from_date, to_date, half_day, half_day_date)


@frappe.whitelist(methods=["GET", "POST"])
def get_leave_balance_on(employee: str, leave_type: str, date: str) -> dict:
	from hrms.hr.doctype.leave_application.leave_application import get_leave_balance_on as _get

	return _get(employee, leave_type, date)


@frappe.whitelist(methods=["GET", "POST"])
def get_expense_claim_types() -> list[dict]:
	from hrms.api import get_expense_claim_types as _get

	return _get()


@frappe.whitelist(methods=["GET", "POST"])
def get_expense_approval_details(employee: str) -> dict:
	from hrms.api import get_expense_approval_details as _get

	return _get(employee)


@frappe.whitelist(methods=["GET", "POST"])
def get_shift_request_approvers(employee: str):
	from hrms.api import get_shift_request_approvers as _get

	return _get(employee)


@frappe.whitelist(methods=["GET", "POST"])
def get_company_defaults(company: str) -> dict:
	"""Defaults a new claim or advance needs: currency, cost center and the claim payable account."""
	frappe.has_permission("Company", "read", company, throw=True)
	return frappe.db.get_value(
		"Company",
		company,
		["default_currency", "cost_center", "default_expense_claim_payable_account"],
		as_dict=True,
	)


# --- dashboards -------------------------------------------------------------------------------------------------


@frappe.whitelist(methods=["GET", "POST"])
def get_attendance_calendar_events(from_date: str, to_date: str) -> dict:
	"""{"YYYY-MM-DD": "Present" | "Absent" | "On Leave" | "Half Day" | "Work From Home" | "Holiday"}"""
	from hrms.api import get_attendance_calendar_events as _get

	return _get(from_date, to_date)


@frappe.whitelist(methods=["GET", "POST"])
def get_holidays_for_employee(employee: str) -> list[dict]:
	from hrms.api import get_holidays_for_employee as _get

	return _get(employee)


@frappe.whitelist(methods=["GET", "POST"])
def get_expense_claim_summary() -> dict:
	from hrms.api import get_expense_claim_summary as _get

	return _get()


@frappe.whitelist(methods=["GET", "POST"])
def get_employee_advance_balance() -> list[dict]:
	from hrms.api import get_employee_advance_balance as _get

	return _get()


@frappe.whitelist(methods=["GET", "POST"])
def get_shifts() -> list[dict]:
	"""The employee's active shift assignments with the shift's start and end time."""
	from hrms.api import get_shifts as _get

	return _get()
