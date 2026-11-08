import { call, upload } from "./client";

export const MAX_UPLOAD_BYTES = 10 * 1024 * 1024;
export const ACCEPTED_FILES =
	".pdf,.png,.jpg,.jpeg,.txt,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.odt,.ods";

export function uploadFile(doctype, name, file) {
	const form = new FormData();
	form.append("doctype", doctype);
	form.append("name", name);
	form.append("file", file);
	return upload("tcf_hr.api.files.upload", form);
}
export const getAttachments = (doctype, name) =>
	call("tcf_hr.api.files.get_attachments", { doctype, name }, { post: false });
export const deleteAttachment = (file) => call("tcf_hr.api.files.delete_attachment", { file });
