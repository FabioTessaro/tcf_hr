<script setup>
defineProps({
	variant: { type: String, default: "primary" }, // primary (yellow) | secondary | danger (red, destructive only)
	disabled: Boolean,
	loading: Boolean,
	type: { type: String, default: "button" },
	to: { type: [String, Object], default: null }, // in-app route: renders a router-link
	href: { type: String, default: null }, // full page load (e.g. pages served by the website): renders an <a>
});
</script>

<template>
	<component
		:is="to ? 'router-link' : href ? 'a' : 'button'"
		class="base-button tf-app-button"
		:class="`variant-${variant}`"
		v-bind="to ? { to } : href ? { href } : { type, disabled: disabled || loading }"
	>
		<span class="base-button__label"><slot /></span>
	</component>
</template>

<style scoped>
.base-button {
	display: inline-flex;
	align-items: center;
	text-decoration: none;
	appearance: none;
	border: 0;
	cursor: pointer;
	min-height: 44px; /* touch target */
	padding: 0 var(--tcf-space-md, 1.5rem);
	transform: skewX(calc(-1 * var(--tcf-slant, 10deg)));
	border-radius: var(--tcf-radius, 0);
	transition: filter var(--tcf-motion-fast, 150ms),
		transform var(--tcf-motion-fast, 150ms) var(--tcf-ease-out, ease-out);
}
.base-button__label {
	display: inline-block;
	transform: skewX(var(--tcf-slant, 10deg));
}
.base-button:hover:not(:disabled) {
	filter: brightness(1.1);
}
.base-button:active:not(:disabled) {
	transform: skewX(calc(-1 * var(--tcf-slant, 10deg))) scale(0.97);
}
.base-button:disabled {
	opacity: 0.5;
	cursor: not-allowed;
}
/* Yellow is the neutral accent; red only for destructive actions (never green by default) */
.variant-primary {
	background: var(--tcf-accent-yellow, #f3bb19);
	color: var(--tcf-light-primary-deep, #3b3b3b); /* dark in both themes: contrast on yellow */
}
.variant-secondary {
	background: var(--tcf-surface, #e0e0e0);
	color: var(--tcf-primary-deep, #3b3b3b);
}
.variant-danger {
	background: var(--tcf-accent-red, #ce202a);
	color: var(--tcf-accent-white, #f4f5f0);
}
</style>
