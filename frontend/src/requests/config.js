// The request types of the HR app. Everything that differs between them lives here; the list and the form are generic.
//
// A type has:
//   slug / doctype / title / icon       identity (the doctype must be in tcf_hr/config/gateway.json)
//   listFields                          fields fetched for the list (plain, readable field names)
//   statusField                         field with the status, or null
//   heading(doc) / subline(doc)         the two lines of a list row
//   fields                              the form, in order: { name, label, type, required?, showIf?, options? }
//   hidden                              fields kept on the document but not shown (employee, company, ...)
//   prepare(ctx)                        async: default values, dropdown options and extra required fields
//   info(values, ctx)                   optional async: read-only figures shown under the form (leave balance)
// Field types: date, select, text, check, currency, expenses (the claim's rows).
import dayjs from "dayjs";
import { __ } from "@/api/i18n";
import {
	getCompanyDefaults,
	getExpenseApprovalDetails,
	getExpenseClaimTypes,
	getLeaveApprovalDetails,
	getLeaveBalanceOn,
	getLeaveTypes,
	getNumberOfLeaveDays,
	getShiftRequestApprovers,
} from "@/api/hr";
import { searchLink } from "@/api/gateway";

const today = () => dayjs().format("YYYY-MM-DD");
const fmt = (date) => (date ? dayjs(date).format("DD MMM YYYY") : "");
const range = (from, to) => (to && to !== from ? `${fmt(from)} – ${fmt(to)}` : fmt(from));
const option = (value, label = value) => ({ value, label });
const approvers = (list = []) => list.map((a) => option(a.name, a.full_name || a.name));
const links = async (doctype, filters) =>
	(await searchLink(doctype, "", filters)).map((r) => option(r.value));
const amount = (value) =>
	Number(value || 0).toLocaleString(undefined, { minimumFractionDigits: 2 });

const halfDay = [
	{ name: "half_day", label: "Half day", type: "check" },
	{
		name: "half_day_date",
		label: "Half day date",
		type: "date",
		showIf: (v) => v.half_day,
		required: true,
	},
];

export const REQUEST_TYPES = [
	{
		slug: "leave",
		doctype: "Leave Application",
		title: "Leave",
		singular: "Leave application",
		icon: "beach_access",
		statusField: "status",
		listFields: [
			"leave_type",
			"from_date",
			"to_date",
			"total_leave_days",
			"status",
			"docstatus",
		],
		heading: (d) => d.leave_type,
		subline: (d) =>
			`${range(d.from_date, d.to_date)}${
				d.total_leave_days ? ` · ${d.total_leave_days} ${__("days")}` : ""
			}`,
		hidden: ["employee", "company", "posting_date", "status"],
		fields: [
			{ name: "leave_type", label: "Leave type", type: "select", required: true },
			{ name: "from_date", label: "From", type: "date", required: true },
			{ name: "to_date", label: "To", type: "date", required: true },
			...halfDay,
			{ name: "leave_approver", label: "Approver", type: "select" },
			{ name: "description", label: "Reason", type: "text" },
		],
		async prepare({ employee }) {
			const [types, approval] = await Promise.all([
				getLeaveTypes(employee.name, today()),
				getLeaveApprovalDetails(employee.name),
			]);
			return {
				defaults: {
					posting_date: today(),
					status: "Open",
					leave_approver: approval.leave_approver || "",
				},
				options: {
					leave_type: types.map((t) => option(t)),
					leave_approver: approvers(approval.department_approvers),
				},
				required: approval.is_mandatory ? ["leave_approver"] : [],
			};
		},
		async info(v, { employee }) {
			if (!v.leave_type || !v.from_date || !v.to_date) return [];
			const [days, balance] = await Promise.all([
				getNumberOfLeaveDays({
					employee: employee.name,
					leave_type: v.leave_type,
					from_date: v.from_date,
					to_date: v.to_date,
					half_day: v.half_day ? 1 : 0,
					half_day_date: v.half_day_date || undefined,
				}),
				getLeaveBalanceOn(employee.name, v.leave_type, v.from_date),
			]);
			const available =
				balance?.leave_balance ??
				balance?.balance ??
				(typeof balance === "number" ? balance : null);
			return [
				[__("Leave days"), days],
				...(available === null ? [] : [[__("Balance on start date"), available]]),
			];
		},
	},
	{
		slug: "compensatory-leave",
		doctype: "Compensatory Leave Request",
		title: "Compensatory leave",
		singular: "Compensatory leave request",
		icon: "update",
		statusField: null,
		listFields: ["leave_type", "work_from_date", "work_end_date", "docstatus"],
		heading: (d) => d.leave_type || __("Compensatory leave"),
		subline: (d) => range(d.work_from_date, d.work_end_date),
		hidden: ["employee"],
		fields: [
			{ name: "leave_type", label: "Leave type", type: "select" },
			{ name: "work_from_date", label: "Worked from", type: "date", required: true },
			{ name: "work_end_date", label: "Worked until", type: "date", required: true },
			...halfDay,
			{ name: "reason", label: "Reason", type: "text", required: true },
		],
		async prepare() {
			return {
				defaults: {},
				options: { leave_type: await links("Leave Type", { is_compensatory: 1 }) },
				required: [],
			};
		},
	},
	{
		slug: "expense-claim",
		doctype: "Expense Claim",
		title: "Expense claims",
		singular: "Expense claim",
		icon: "receipt_long",
		statusField: "approval_status",
		listFields: [
			"posting_date",
			"total_claimed_amount",
			"currency",
			"approval_status",
			"docstatus",
		],
		heading: (d) => `${amount(d.total_claimed_amount)} ${d.currency || ""}`.trim(),
		subline: (d) => fmt(d.posting_date),
		hidden: [
			"employee",
			"company",
			"currency",
			"exchange_rate",
			"cost_center",
			"payable_account",
		],
		fields: [
			{ name: "posting_date", label: "Date", type: "date", required: true },
			{ name: "expense_approver", label: "Approver", type: "select" },
			{ name: "expenses", label: "Expenses", type: "expenses", required: true },
			{ name: "remark", label: "Remarks", type: "text" },
		],
		async prepare({ employee }) {
			const [types, approval, company] = await Promise.all([
				getExpenseClaimTypes(),
				getExpenseApprovalDetails(employee.name),
				getCompanyDefaults(employee.company),
			]);
			return {
				defaults: {
					posting_date: today(),
					expense_approver: approval.expense_approver || "",
					currency: company.default_currency,
					exchange_rate: 1,
					cost_center: company.cost_center,
					payable_account: company.default_expense_claim_payable_account,
					expenses: [],
				},
				options: {
					expense_approver: approvers(approval.department_approvers),
					expense_type: types.map((t) => option(t.name)),
				},
				required: approval.is_mandatory ? ["expense_approver"] : [],
			};
		},
	},
	{
		slug: "advance",
		doctype: "Employee Advance",
		title: "Advances",
		singular: "Employee advance",
		icon: "payments",
		statusField: "status",
		listFields: [
			"posting_date",
			"advance_amount",
			"currency",
			"purpose",
			"status",
			"docstatus",
		],
		heading: (d) => `${amount(d.advance_amount)} ${d.currency || ""}`.trim(),
		subline: (d) => [fmt(d.posting_date), d.purpose].filter(Boolean).join(" · "),
		hidden: ["employee", "company", "currency"],
		fields: [
			{ name: "posting_date", label: "Date", type: "date", required: true },
			{ name: "purpose", label: "Purpose", type: "text", required: true },
			{ name: "advance_amount", label: "Amount", type: "currency", required: true },
			{
				name: "repay_unclaimed_amount_from_salary",
				label: "Repay unclaimed amount from salary",
				type: "check",
			},
		],
		async prepare({ employee }) {
			const company = await getCompanyDefaults(employee.company);
			return {
				defaults: { posting_date: today(), currency: company.default_currency },
				options: {},
				required: [],
			};
		},
	},
	{
		slug: "attendance-request",
		doctype: "Attendance Request",
		title: "Attendance requests",
		singular: "Attendance request",
		icon: "how_to_reg",
		statusField: null,
		listFields: ["reason", "from_date", "to_date", "docstatus"],
		heading: (d) => d.reason,
		subline: (d) => range(d.from_date, d.to_date),
		hidden: ["employee", "company"],
		fields: [
			{ name: "reason", label: "Reason", type: "select", required: true },
			{ name: "from_date", label: "From", type: "date", required: true },
			{ name: "to_date", label: "To", type: "date", required: true },
			...halfDay,
			{ name: "include_holidays", label: "Include holidays", type: "check" },
			{ name: "explanation", label: "Explanation", type: "text" },
		],
		async prepare() {
			return {
				defaults: {},
				options: {
					reason: [
						option("Work From Home", __("Work from home")),
						option("On Duty", __("On duty")),
					],
				},
				required: [],
			};
		},
	},
	{
		slug: "shift-request",
		doctype: "Shift Request",
		title: "Shift requests",
		singular: "Shift request",
		icon: "schedule",
		statusField: "status",
		listFields: ["shift_type", "from_date", "to_date", "status", "docstatus"],
		heading: (d) => d.shift_type,
		subline: (d) => range(d.from_date, d.to_date),
		hidden: ["employee", "company", "status"],
		fields: [
			{ name: "shift_type", label: "Shift", type: "select", required: true },
			{ name: "from_date", label: "From", type: "date", required: true },
			{ name: "to_date", label: "To", type: "date" },
			{ name: "approver", label: "Approver", type: "select", required: true },
		],
		async prepare({ employee }) {
			const [shifts, list] = await Promise.all([
				links("Shift Type"),
				getShiftRequestApprovers(employee.name),
			]);
			return {
				defaults: { status: "Draft", approver: list?.[0]?.name || "" },
				options: { shift_type: shifts, approver: approvers(list) },
				required: [],
			};
		},
	},
];

export const requestType = (slug) => REQUEST_TYPES.find((t) => t.slug === slug);
export const requestTypeOf = (doctype) => REQUEST_TYPES.find((t) => t.doctype === doctype);
