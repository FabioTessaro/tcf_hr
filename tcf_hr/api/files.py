"""Attachments on the request documents (private files)."""

import os

import frappe
from frappe import _

from tcf_hr.api.gateway import _check as require_op

MAX_BYTES = 10 * 1024 * 1024
MAX_FILENAME = 140
ALLOWED_EXTENSIONS = {
	".pdf", ".png", ".jpg", ".jpeg", ".txt", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".ods",
}  # fmt: skip
_MAGIC = {".pdf": (b"%PDF",), ".png": (b"\x89PNG",), ".jpg": (b"\xff\xd8",), ".jpeg": (b"\xff\xd8",)}


def safe_filename(filename: str | None) -> str:
	"""Base name only, no control characters, bounded length."""
	name = os.path.basename((filename or "").replace("\\", "/"))
	name = "".join(ch for ch in name if ch.isprintable()).strip()
	stem, ext = os.path.splitext(name)
	return (stem[: MAX_FILENAME - len(ext)] or "file") + ext.lower()


def check_upload(filename: str | None, size: int, head: bytes) -> str | None:
	"""Pure validation: returns an error message, or None when the file is acceptable."""
	ext = os.path.splitext(safe_filename(filename))[1]
	if ext not in ALLOWED_EXTENSIONS:
		return _("This file type is not allowed.")
	if size <= 0:
		return _("The file is empty.")
	if size > MAX_BYTES:
		return _("The file is larger than {0} MB.").format(MAX_BYTES // (1024 * 1024))
	signatures = _MAGIC.get(ext)
	if signatures and not head.startswith(signatures):
		return _("The file content does not match its type.")
	return None


def _file_row(file) -> dict:
	return {
		"name": file.name,
		"file_name": file.file_name,
		"file_url": file.file_url,
		"file_size": file.file_size,
	}


@frappe.whitelist(methods=["POST"])
def upload(doctype: str, name: str) -> dict:
	"""Attach the uploaded `file` (multipart) to one of the user's documents."""
	require_op(doctype, "write")
	doc = frappe.get_doc(doctype, name)
	doc.check_permission("write")

	upload_file = frappe.request.files.get("file") if frappe.request else None
	if not upload_file:
		frappe.throw(_("No file was sent."), frappe.ValidationError)
	content = upload_file.stream.read(MAX_BYTES + 1)
	error = check_upload(upload_file.filename, len(content), content[:8])
	if error:
		frappe.throw(error, frappe.ValidationError)

	file = frappe.get_doc(
		{
			"doctype": "File",
			"attached_to_doctype": doctype,
			"attached_to_name": name,
			"folder": "Home",
			"file_name": safe_filename(upload_file.filename),
			"content": content,
			"is_private": 1,
		}
	).insert()
	return _file_row(file)


@frappe.whitelist(methods=["GET"])
def get_attachments(doctype: str, name: str) -> list[dict]:
	require_op(doctype, "read")
	frappe.get_doc(doctype, name).check_permission("read")
	return frappe.get_all(
		"File",
		filters={"attached_to_doctype": doctype, "attached_to_name": name},
		fields=["name", "file_name", "file_url", "file_size"],
		order_by="creation asc",
	)


@frappe.whitelist(methods=["POST"])
def delete_attachment(file: str) -> None:
	doctype, name = frappe.db.get_value("File", file, ["attached_to_doctype", "attached_to_name"]) or (
		None,
		None,
	)
	if not doctype:
		frappe.throw(_("Not permitted"), frappe.PermissionError)
	require_op(doctype, "write")
	frappe.get_doc(doctype, name).check_permission("write")
	frappe.delete_doc("File", file)
