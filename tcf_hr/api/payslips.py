"""Salary slip PDF for the HR app."""

import frappe
from frappe import _

from tcf_hr.api.gateway import _check as require_op

DOCTYPE = "Salary Slip"


@frappe.whitelist(methods=["GET"])
def download(name: str):
	"""Stream the PDF of one of the user's submitted salary slips (the browser downloads it).

	Same checks as the document API: the doctype must be allowlisted for reading and the user must have read
	permission on this slip. Drafts are never offered.
	"""
	from frappe.utils.print_format import download_pdf

	require_op(DOCTYPE, "read")
	doc = frappe.get_doc(DOCTYPE, name)
	doc.check_permission("read")
	if doc.docstatus != 1:
		frappe.throw(_("This salary slip is not available."), frappe.PermissionError)

	default_format = frappe.get_meta(DOCTYPE).default_print_format or "Standard"
	download_pdf(DOCTYPE, name, format=default_format, doc=doc)  # sets the file response
