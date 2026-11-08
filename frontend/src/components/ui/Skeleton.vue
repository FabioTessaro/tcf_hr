<script setup>
// Loading placeholder. `lines` bars of varying width; the shimmer stops under reduced motion (see base.css).
defineProps({ lines: { type: Number, default: 3 } });
</script>

<template>
	<div class="skeleton" role="status" aria-busy="true">
		<span
			v-for="n in lines"
			:key="n"
			class="skeleton__bar"
			:style="{ width: `${100 - ((n * 17) % 40)}%` }"
		/>
	</div>
</template>

<style scoped>
.skeleton {
	display: grid;
	gap: var(--tcf-space-xs, 0.5rem);
}
.skeleton__bar {
	height: 1rem;
	background: linear-gradient(
		90deg,
		var(--tcf-surface, #e0e0e0) 25%,
		var(--tcf-background, #f1f2f2) 50%,
		var(--tcf-surface, #e0e0e0) 75%
	);
	background-size: 200% 100%;
	animation: shimmer 1.4s linear infinite;
	transform: skewX(calc(-1 * var(--tcf-slant, 10deg)));
}
</style>
