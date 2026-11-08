import { call } from "./client";

/** End the session, then leave the app for the public website. */
export async function logout() {
	await call("logout");
	window.location.assign("/");
}
