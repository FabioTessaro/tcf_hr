// Client for tcf_hr.api.gateway: the only generic document API the app uses.
import { call } from "./client";

const g = (name, args, options) => call(`tcf_hr.api.gateway.${name}`, args, options);

export const getList = (doctype, opts = {}) => g("get_list", { doctype, ...opts });
export const getCount = (doctype, filters) => g("get_count", { doctype, filters });
export const getDoc = (doctype, name) => g("get_doc", { doctype, name });
export const getDocPermissions = (doctype, name) => g("get_doc_permissions", { doctype, name });
export const getMeta = (doctype) => g("get_meta", { doctype });
export const searchLink = (doctype, txt, filters) => g("search_link", { doctype, txt, filters });
export const saveDoc = (doc) => g("save_doc", { doc });
export const submitDoc = (doctype, name) => g("submit", { doctype, name });
export const cancelDoc = (doctype, name) => g("cancel", { doctype, name });
export const deleteDoc = (doctype, name) => g("delete", { doctype, name });
export const getTransitions = (doctype, name) => g("get_transitions", { doctype, name });
export const applyWorkflow = (doctype, name, action) =>
	g("apply_workflow", { doctype, name, action });
