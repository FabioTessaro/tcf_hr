import { call } from "./client";

export const getProfile = () => call("tcf_hr.api.profile.get_profile", {}, { post: false });
