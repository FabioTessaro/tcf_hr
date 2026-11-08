<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";

// Brand panel, built like tcf_web's slanted card (visual-elements/_slanted-card.scss):
//
// - The box is a plain rectangle and its content is never transformed. Only the background layer (::before)
//   is skewed by --tcf-slant.
// - A skew pushes the background out by (height * tan(slant)) / 2 on each side. The panel pulls its box in by
//   that much (margin) and adds the same to its horizontal padding. Result: every panel, tall or short, spans
//   exactly the same width, lines up with the others, and its content sits in the middle.
// - The height is measured, so the compensation is exact (the website card only has an estimate).
// - Spacing is owned here: one padding, one gap between children; their own margins are reset.
// - On phones it is a flat, full-width section: no slant, no compensation.
defineProps({ tone: { type: String, default: "surface" } }); // surface | background

const root = ref(null);
const height = ref(null);
let observer = null;

// Rounded to 8px steps so a one-line wrap change does not make the layout chase itself
const snap = (px) => Math.round(px / 8) * 8;

onMounted(() => {
	height.value = snap(root.value.offsetHeight);
	observer = new ResizeObserver(() => {
		const next = snap(root.value.offsetHeight);
		if (next !== height.value) height.value = next;
	});
	observer.observe(root.value);
});
onBeforeUnmount(() => observer?.disconnect());
</script>

<template>
	<section
		ref="root"
		class="slanted-panel"
		:class="`tone-${tone}`"
		:style="height ? { '--panel-h': `${height}px` } : null"
	>
		<div class="slanted-panel__content"><slot /></div>
	</section>
</template>

<style scoped>
.slanted-panel {
	/* half of the overhang of a skew of the panel's height (8rem until the height is measured) */
	--half-comp: calc(tan(var(--tcf-slant, 10deg)) * var(--panel-h, 8rem) / 2);

	position: relative;
	isolation: isolate;
	margin-inline: var(--half-comp);
	padding: var(--tcf-space-md, 1.5rem) calc(var(--tcf-space-lg, 2rem) + var(--half-comp));
}
.slanted-panel::before {
	content: "";
	position: absolute;
	inset: 0;
	z-index: -1;
	transform: skewX(calc(-1 * var(--tcf-slant, 10deg)));
	border-radius: var(--tcf-radius, 0);
	box-shadow: 0 0.25rem 0.3rem rgba(0, 0, 0, 0.1);
}
.tone-surface::before {
	background: var(--tcf-surface, #e0e0e0);
}
.tone-background::before {
	background: var(--tcf-background, #f1f2f2);
}
@media screen and (prefers-color-scheme: dark) {
	.slanted-panel::before {
		box-shadow: 0 0.25rem 0.3rem rgba(1, 1, 1, 0.1);
	}
}

.slanted-panel__content {
	display: grid;
	gap: var(--tcf-space-sm, 1rem);
}
/* Slotted children (h1, p, dl...) keep no margins of their own: the grid gap spaces them */
:slotted(*) {
	margin: 0;
}

@media (max-width: 767px) {
	.slanted-panel {
		margin-inline: 0;
		padding: var(--tcf-space-md, 1.5rem);
	}
	.slanted-panel::before {
		transform: none;
		box-shadow: none;
	}
}
</style>
