<script setup>
// Status label. tone: accent (default, yellow) | muted | success (green) | danger (red)
defineProps({ tone: { type: String, default: "accent" } });
</script>

<template>
	<span class="pill tf-app-pill" :class="`tone-${tone}`"
		><span class="pill__label"><slot /></span
	></span>
</template>

<style scoped>
.pill {
	display: inline-block;
	padding: 0.15rem 0.7rem;
	transform: skewX(calc(-1 * var(--tcf-slant, 10deg)));
	white-space: nowrap;
}
.pill__label {
	display: inline-block;
	transform: skewX(var(--tcf-slant, 10deg));
}
.tone-accent {
	background: var(--tcf-accent-yellow, #f3bb19);
	color: var(--tcf-light-primary-deep, #3b3b3b);
}
.tone-muted {
	background: var(--tcf-surface, #e0e0e0);
	color: var(--tcf-primary-deep, #3b3b3b);
}
.tone-success {
	background: var(--tcf-accent-green, #018c45);
	color: var(--tcf-accent-white, #f4f5f0);
}
.tone-danger {
	background: var(--tcf-accent-red, #ce202a);
	color: var(--tcf-accent-white, #f4f5f0);
}
</style>
