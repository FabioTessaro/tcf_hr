<script setup>
import { watch } from "vue";
import AppNav from "@/components/AppNav.vue";
import Logo from "@/components/ui/Logo.vue";
import { useNotifications } from "@/stores/notifications";
import { useSession } from "@/stores/session";

const session = useSession();
const notifications = useNotifications();

// Start listening for notifications once the session is known
watch(
	() => session.loaded,
	(loaded) => loaded && notifications.listen(),
	{ immediate: true }
);
</script>

<template>
	<header class="app-header">
		<div class="brand">
			<!-- The logo leaves the app for the main website: a normal page load, not a route -->
			<a href="/" class="brand__logo" aria-label="TCF Group"><Logo /></a>
			<span class="brand__divider" aria-hidden="true" />
			<router-link to="/home" class="brand__title tf-app-heading">HR</router-link>
		</div>
		<AppNav v-if="session.loaded" />
	</header>
	<main class="app-main">
		<router-view v-if="session.loaded" v-slot="{ Component, route }">
			<Transition name="page" mode="out-in">
				<!-- One element per route so the whole page transitions, whatever the view renders -->
				<div :key="route.path" class="page"><component :is="Component" /></div>
			</Transition>
		</router-view>
	</main>
</template>

<style scoped>
.app-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: var(--tcf-space-md, 1.5rem);
	padding: var(--tcf-space-sm, 1rem) var(--tcf-space-md, 1.5rem);
	padding-top: max(var(--tcf-space-sm, 1rem), env(safe-area-inset-top));
	background: var(--tcf-surface, #e0e0e0);
	color: var(--tcf-primary-deep, #3b3b3b);
}
.brand {
	display: flex;
	align-items: center;
	gap: var(--tcf-space-sm, 1rem);
}
.brand__logo {
	display: block;
}
/* Slanted like every brand shape; swap skewX for nothing to get a straight divider */
.brand__divider {
	width: 1px;
	height: 1.6rem;
	background: currentColor;
	opacity: 0.5;
	transform: skewX(calc(-1 * var(--tcf-slant, 10deg)));
}
.brand__title {
	text-decoration: none;
}
.app-main {
	max-width: 48rem;
	margin: 0 auto;
	padding: var(--tcf-space-md, 1.5rem);
	/* room for the bottom tab bar on phones */
	padding-bottom: calc(var(--tcf-space-xl, 3.5rem) + env(safe-area-inset-bottom));
}
.page {
	display: grid;
	gap: var(--tcf-space-md, 1.5rem);
}

/* Phones: sections run edge to edge (the panels drop their slant) */
@media (max-width: 767px) {
	.app-main {
		padding: 0 0 calc(var(--tcf-space-xl, 3.5rem) + env(safe-area-inset-bottom));
	}
	.page {
		gap: var(--tcf-space-xs, 0.5rem);
	}
}
</style>
