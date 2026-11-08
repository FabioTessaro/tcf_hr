import { createRouter, createWebHistory } from "vue-router";
import { requestType } from "@/requests/config";
import { useSession } from "@/stores/session";

// Screens are added phase by phase (see docs in the project plan). Each route can declare
// `meta.capability` to be hidden when the server says the user doesn't have it.
const routes = [
	{ path: "/", redirect: "/home" },
	{ path: "/home", name: "Home", component: () => import("@/views/Home.vue") },
	{ path: "/attendance", name: "Attendance", component: () => import("@/views/Attendance.vue") },
	{ path: "/leaves", name: "Leaves", component: () => import("@/views/Leaves.vue") },
	{ path: "/claims", name: "Claims", component: () => import("@/views/Claims.vue") },
	{
		path: "/payslips",
		name: "Payslips",
		component: () => import("@/views/Payslips.vue"),
		meta: { capability: "payslips" },
	},
	{
		path: "/payslips/:name",
		name: "PayslipDetail",
		component: () => import("@/views/PayslipDetail.vue"),
		meta: { capability: "payslips" },
	},
	{ path: "/requests", name: "Requests", component: () => import("@/views/Requests.vue") },
	{
		path: "/requests/:slug",
		name: "RequestList",
		component: () => import("@/views/RequestList.vue"),
	},
	{
		path: "/requests/:slug/new",
		name: "RequestNew",
		component: () => import("@/views/RequestForm.vue"),
	},
	{
		path: "/requests/:slug/:name",
		name: "RequestDetail",
		component: () => import("@/views/RequestForm.vue"),
	},
	{ path: "/profile", name: "Profile", component: () => import("@/views/Profile.vue") },
	{
		path: "/notifications",
		name: "Notifications",
		component: () => import("@/views/Notifications.vue"),
	},
	{ path: "/settings", name: "Settings", component: () => import("@/views/Settings.vue") },
	{
		path: "/:pathMatch(.*)*",
		name: "NotFound",
		component: () => import("@/views/NotFound.vue"),
	},
];

const router = createRouter({ history: createWebHistory("/hrms"), routes });

router.beforeEach(async (to) => {
	const session = useSession();
	if (!session.loaded) await session.load();
	if (to.meta.capability && !session.can(to.meta.capability)) return { name: "Home" };
	// A request type the user may not read (or an unknown one) goes home; the server enforces it anyway
	if (to.params.slug) {
		const type = requestType(to.params.slug);
		if (!type || !session.capabilities.requests?.[type.doctype]) return { name: "Home" };
		if (to.name === "RequestNew" && !session.capabilities.requests[type.doctype].create)
			return { name: "RequestList", params: { slug: type.slug } };
	}
});

export default router;
