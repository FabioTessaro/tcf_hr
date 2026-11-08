<script setup>
// Small status mark (slanted bar). tone: accent (default, yellow) | muted | success (green) | danger (red).
// Always pair with text for accessibility.
defineProps({ tone: { type: String, default: "accent" } });
</script>

<template>
	<span class="indicator" :class="`tone-${tone}`" aria-hidden="true" />
</template>

<style scoped>
.indicator {
	display: inline-block;
	width: 0.35rem;
	height: 1.1rem;
	transform: skewX(calc(-1 * var(--tcf-slant, 10deg)));
	vertical-align: middle;
}
.tone-accent {
	background: var(--tcf-accent-yellow, #f3bb19);
}
.tone-muted {
	background: var(--tcf-primary-light, #4a4a4a);
	opacity: 0.5;
}
.tone-success {
	background: var(--tcf-accent-green, #018c45);
}
.tone-danger {
	background: var(--tcf-accent-red, #ce202a);
}
</style>
