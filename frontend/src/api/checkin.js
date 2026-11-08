import { call } from "./client";

export const getCheckinStatus = () => call("tcf_hr.api.checkin.get_status", {}, { post: false });
export const getCheckinAddress = (name) =>
	call("tcf_hr.api.checkin.get_address", { name }, { post: false });
export const submitCheckin = (log_type, latitude, longitude) =>
	call("tcf_hr.api.checkin.submit_checkin", { log_type, latitude, longitude });
