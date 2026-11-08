<script setup>
import { computed, ref } from "vue";

// Slanted picture frame. Falls back to initials when there is no picture or it fails to load.
const props = defineProps({
	src: { type: String, default: "" },
	name: { type: String, default: "" },
	size: { type: String, default: "6rem" },
});

const failed = ref(false);
const initials = computed(() =>
	props.name
		.split(/\s+/)
		.filter(Boolean)
		.slice(0, 2)
		.map((part) => part[0].toUpperCase())
		.join("")
);
</script>

<template>
	<span class="avatar" :style="{ '--size': size }">
		<img v-if="src && !failed" :src="src" :alt="name" @error="failed = true" />
		<span v-else class="avatar__initials" aria-hidden="true">{{ initials }}</span>
	</span>
</template>

<style scoped>
.avatar {
	/* tan(10deg) * size: the horizontal offset of a 10deg slant (keep in step with --tcf-slant) */
	--offset: calc(var(--size) * 0.1763);
	display: inline-flex;
	align-items: center;
	justify-content: center;
	flex: none;
	width: calc(var(--size) + var(--offset));
	height: var(--size);
	clip-path: polygon(var(--offset) 0, 100% 0, calc(100% - var(--offset)) 100%, 0 100%);
	background: var(--tcf-accent-yellow, #f3bb19);
	color: var(--tcf-light-primary-deep, #3b3b3b);
}
img {
	width: 100%;
	height: 100%;
	object-fit: cover;
}
.avatar__initials {
	font-size: calc(var(--size) * 0.35);
	letter-spacing: 0.08em;
}
</style>
