// Helpers delegated to hrms (tcf_hr.api.hrms_proxy): leave balances, approvers, claim types, company defaults.
import { call } from "./client";

const h = (name, args, options) => call(`tcf_hr.api.hrms_proxy.${name}`, args, options);

export const getLeaveTypes = (employee, date) =>
	h("get_leave_types", { employee, date }, { post: false });
export const getLeaveApprovalDetails = (employee) =>
	h("get_leave_approval_details", { employee }, { post: false });
export const getNumberOfLeaveDays = (args) => h("get_number_of_leave_days", args, { post: false });
export const getLeaveBalanceOn = (employee, leave_type, date) =>
	h("get_leave_balance_on", { employee, leave_type, date }, { post: false });
export const getExpenseClaimTypes = () => h("get_expense_claim_types", {}, { post: false });
export const getExpenseApprovalDetails = (employee) =>
	h("get_expense_approval_details", { employee }, { post: false });
export const getShiftRequestApprovers = (employee) =>
	h("get_shift_request_approvers", { employee }, { post: false });
export const getCompanyDefaults = (company) =>
	h("get_company_defaults", { company }, { post: false });

export const getAttendanceCalendarEvents = (from_date, to_date) =>
	h("get_attendance_calendar_events", { from_date, to_date }, { post: false });
export const getLeaveBalanceMap = () => h("get_leave_balance_map", {}, { post: false });
export const getHolidaysForEmployee = (employee) =>
	h("get_holidays_for_employee", { employee }, { post: false });
export const getExpenseClaimSummary = () => h("get_expense_claim_summary", {}, { post: false });
export const getEmployeeAdvanceBalance = () =>
	h("get_employee_advance_balance", {}, { post: false });
export const getShifts = () => h("get_shifts", {}, { post: false });
