<script setup>
// Material Symbols Sharp, the same icon set as the website (loaded in index.html).
defineProps({ name: { type: String, required: true } });
</script>

<template>
	<span class="material-symbols-sharp icon" aria-hidden="true">{{ name }}</span>
</template>

<style>
/* Not scoped on purpose: the icon font rule is global, as in tcf_web's material-symbols partial */
.material-symbols-sharp {
	font-family: "Material Symbols Sharp";
	font-variation-settings: var(--icon-font-variation-settings, inherit);
	font-weight: normal;
	font-style: normal;
	font-size: 24px;
	line-height: 1;
	letter-spacing: normal;
	text-transform: none;
	display: inline-block;
	white-space: nowrap;
	word-wrap: normal;
	direction: ltr;
	-webkit-font-feature-settings: "liga";
	-webkit-font-smoothing: antialiased;
}
.icon {
	font-weight: 200; /* thin strokes, as on the website */
	user-select: none;
}
</style>
