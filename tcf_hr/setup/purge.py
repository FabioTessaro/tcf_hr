"""Remove seed data so the HR app starts from a blank sheet.

Records that other documents still link to are skipped and logged, never force-deleted.
Each purge is guarded by a marker, so it runs once and later records are left alone.
"""

import frappe
from frappe import _
from frappe.utils.nestedset import get_root_of

SEEDS_MARKER = "tcf_hr_hrms_seeds_purged"
ORG_MARKER = "tcf_hr_org_defaults_purged"

# Seeded by hrms.setup.make_fixtures
HRMS_SEEDS = {
	"Expense Claim Type": ["Calls", "Food", "Medical", "Others", "Travel"],
	"Vehicle Service Item": ["Brake Oil", "Brake Pad", "Clutch Plate", "Engine Oil", "Oil Change", "Wheels"],
	"Leave Type": [
		"Casual Leave",
		"Compensatory Off",
		"Sick Leave",
		"Privilege Leave",
		"Leave Without Pay",
	],
	"Employment Type": [
		"Full-time",
		"Part-time",
		"Probation",
		"Contract",
		"Commission",
		"Piecework",
		"Intern",
		"Apprentice",
	],
	"Job Applicant Source": ["Website Listing", "Walk In", "Employee Referral", "Campaign"],
	"Offer Term": [
		"Date of Joining",
		"Annual Salary",
		"Probationary Period",
		"Employee Benefits",
		"Working Hours",
		"Stock Options",
		"Department",
		"Job Description",
		"Responsibilities",
		"Leaves per Year",
		"Notice Period",
		"Incentives",
	],
	"Activity Type": [
		"Planning",
		"Research",
		"Proposal Writing",
		"Execution",
		"Communication",
	],
	"Salary Component": [
		"Leave Encashment",
		"Arrear",
		"Basic",
		"Income Tax",
	],
}

# Created per company by erpnext Company.create_default_departments
STOCK_DEPARTMENTS = [
	"Accounts",
	"Marketing",
	"Sales",
	"Purchase",
	"Operations",
	"Production",
	"Dispatch",
	"Customer Service",
	"Human Resources",
	"Management",
	"Quality Management",
	"Research & Development",
	"Legal",
]


def purge_hrms_seeds():
	if frappe.db.get_default(SEEDS_MARKER):
		return
	for doctype, names in HRMS_SEEDS.items():
		# Seed names are translated at install time, so match the translated form too.
		candidates = {n for name in names for n in (name, _(name))}
		_delete(doctype, [n for n in candidates if frappe.db.exists(doctype, n)])
	frappe.db.set_default(SEEDS_MARKER, "1")


def purge_org_defaults(force: bool = False):
	"""Delete every Department (except the root), Designation and Branch.

	Waits for the setup wizard (that is when ERPNext seeds them) unless `force` is set.
	"""
	if frappe.db.get_default(ORG_MARKER):
		return
	if not (force or frappe.is_setup_complete()):
		return

	root = get_root_of("Department")
	filters = {"name": ["!=", root]} if root else {}
	# Children have a higher `lft` than their parent: delete deepest first.
	departments = frappe.get_all("Department", filters=filters, order_by="lft desc", pluck="name")
	_delete("Department", departments)
	_delete("Designation", frappe.get_all("Designation", pluck="name"))
	_delete("Branch", frappe.get_all("Branch", pluck="name"))
	frappe.db.set_default(ORG_MARKER, "1")


def purge_company_default_departments(doc, method=None):
	"""Company `on_update`: ERPNext recreates the stock departments whenever a company has none.

	If every department of this company is a stock one, remove them again.
	"""
	if not frappe.db.get_default(ORG_MARKER):
		return
	stock = {n for name in STOCK_DEPARTMENTS for n in (name, _(name))}
	rows = frappe.get_all(
		"Department",
		filters={"company": doc.name},
		fields=["name", "department_name"],
		order_by="lft desc",
	)
	if rows and all(r.department_name in stock for r in rows):
		_delete("Department", [r.name for r in rows])


def _delete(doctype: str, names: list[str]):
	logger = frappe.logger("tcf_hr")
	for name in names:
		try:
			frappe.delete_doc(doctype, name, ignore_permissions=True, delete_permanently=True)
		except frappe.LinkExistsError:
			logger.warning(f"Purge skipped {doctype} {name}: still linked from other documents")
		except Exception:
			frappe.log_error(title=f"tcf_hr purge failed: {doctype} {name}")
