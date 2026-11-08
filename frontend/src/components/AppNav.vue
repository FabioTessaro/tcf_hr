<script setup>
import { computed } from "vue";
import Icon from "@/components/ui/Icon.vue";
import { __ } from "@/api/i18n";
import { useNotifications } from "@/stores/notifications";

const notifications = useNotifications();
const links = [
	{ to: "/home", label: "Home" },
	{ to: "/requests", label: "Requests" },
	{ to: "/profile", label: "Profile" },
];
const badge = computed(() => (notifications.unread > 9 ? "9+" : String(notifications.unread)));
const notificationsLabel = computed(() =>
	notifications.unread
		? __("Notifications ({0} unread)", [notifications.unread])
		: __("Notifications")
);
</script>

<template>
	<nav class="app-nav" :aria-label="__('Main')">
		<router-link
			v-for="link in links"
			:key="link.to"
			:to="link.to"
			class="app-nav__link nav-button tf-app-nav"
		>
			<span class="nav-button__label">{{ __(link.label) }}</span>
		</router-link>
		<!-- Icon only, always last. The dot carries the unread count. -->
		<router-link
			to="/notifications"
			class="app-nav__link app-nav__bell nav-button nav-button--indicator"
			:aria-label="notificationsLabel"
		>
			<span class="nav-button__label">
				<Icon name="notifications" />
				<!-- Unread count, inline to the right of the icon -->
				<Transition name="pop">
					<span
						v-if="notifications.unread"
						:key="badge"
						class="app-nav__dot tf-app-pill"
						aria-hidden="true"
						>{{ badge }}</span
					>
				</Transition>
			</span>
		</router-link>
	</nav>
</template>

<style scoped>
.app-nav {
	display: flex;
	align-items: center;
	gap: var(--tcf-space-md, 1.5rem);
}
.app-nav__link {
	display: inline-flex;
	align-items: center;
	min-height: 44px;
}
/* Small slanted count mark next to the bell */
.app-nav__dot {
	min-width: 1.1rem;
	height: 1.1rem;
	padding: 0 0.25rem;
	display: inline-flex;
	align-items: center;
	justify-content: center;
	font-size: 0.65rem;
	letter-spacing: 0;
	background: var(--tcf-accent-yellow, #f3bb19);
	color: var(--tcf-light-primary-deep, #3b3b3b);
	transform: skewX(calc(-1 * var(--tcf-slant, 10deg)));
}

/* Phones: tab bar at the bottom, above the safe area */
@media (max-width: 767px) {
	.app-nav {
		position: fixed;
		inset: auto 0 0 0;
		justify-content: space-around;
		gap: 0;
		padding: 0 var(--tcf-space-xs, 0.5rem) env(safe-area-inset-bottom);
		background: var(--tcf-surface, #e0e0e0);
		z-index: 10;
	}
}
</style>
