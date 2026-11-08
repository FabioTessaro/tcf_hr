import { defineStore } from "pinia";
import { call } from "@/api/client";

export const useSession = defineStore("session", {
	state: () => ({ loaded: false, user: null, employee: null, capabilities: {}, lang: "en" }),
	actions: {
		async load() {
			const data = await call("tcf_hr.api.session.get_bootstrap", {}, { post: false });
			if (data.is_guest) {
				window.location.assign(
					`/login?redirect-to=${encodeURIComponent(location.pathname)}`
				);
				return;
			}
			if (data.csrf_token) window.csrf_token = data.csrf_token;
			Object.assign(this, {
				loaded: true,
				user: data.user,
				employee: data.employee,
				capabilities: data.capabilities,
				lang: data.lang,
			});
		},
		can(capability) {
			return Boolean(this.capabilities[capability]);
		},
	},
});
