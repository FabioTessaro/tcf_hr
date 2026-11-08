import { defineStore } from "pinia";
import { fetchNotifications, fetchUnreadCount, markAllRead, markRead } from "@/api/notifications";
import { onRealtime } from "@/api/realtime";

export const useNotifications = defineStore("notifications", {
	state: () => ({ unread: 0, items: [], loaded: false, loading: false, _stop: null }),
	actions: {
		async refreshCount() {
			this.unread = await fetchUnreadCount();
		},
		async load() {
			this.loading = true;
			try {
				this.items = await fetchNotifications();
				this.loaded = true;
				await this.refreshCount();
			} finally {
				this.loading = false;
			}
		},
		async read(names) {
			await markRead(names);
			this.items.forEach((item) => names.includes(item.name) && (item.read = 1));
			await this.refreshCount();
		},
		async readAll() {
			await markAllRead();
			this.items.forEach((item) => (item.read = 1));
			this.unread = 0;
		},
		/** Start once after login: a new notification refreshes the badge (and the list, if it was opened). */
		listen() {
			if (this._stop) return;
			this.refreshCount();
			this._stop = onRealtime("tcf_hr:notification", () => {
				this.refreshCount();
				if (this.loaded) this.load();
			});
		},
	},
});
