import { call } from "./client";

const n = (name, args, options) => call(`tcf_hr.api.notifications.${name}`, args, options);

export const fetchNotifications = (start = 0, page_length = 20) =>
	n("get_notifications", { start, page_length }, { post: false });
export const fetchUnreadCount = () => n("get_unread_count", {}, { post: false });
export const markRead = (names) => n("mark_read", { names });
export const markAllRead = () => n("mark_all_read");
