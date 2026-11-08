<script setup>
import { ref } from "vue";

// Tab buttons for a section of a page. Arrow keys move between tabs (Home and End jump). The panel content
// is up to the page: show it with v-if / Transition on the same v-model value.
const active = defineModel({ type: String, required: true });
defineProps({ items: { type: Array, required: true }, label: String }); // items: [{ key, label }]

const buttons = ref([]);

function onKey(event, index, items) {
	const last = items.length - 1;
	const next = {
		ArrowRight: index === last ? 0 : index + 1,
		ArrowLeft: index === 0 ? last : index - 1,
		Home: 0,
		End: last,
	}[event.key];
	if (next === undefined) return;
	event.preventDefault();
	active.value = items[next].key;
	buttons.value[next]?.focus();
}
</script>

<template>
	<div class="tabs" role="tablist" :aria-label="label">
		<button
			v-for="(item, index) in items"
			:key="item.key"
			ref="buttons"
			type="button"
			role="tab"
			class="tab tf-app-nav"
			:class="{ active: active === item.key }"
			:aria-selected="active === item.key"
			:tabindex="active === item.key ? 0 : -1"
			@click="active = item.key"
			@keydown="onKey($event, index, items)"
		>
			{{ item.label }}
		</button>
	</div>
</template>

<style scoped>
.tabs {
	display: flex;
	gap: var(--tcf-space-md, 1.5rem);
	overflow-x: auto;
}
.tab {
	min-height: 44px;
	padding: 0;
	border: 0;
	border-bottom: 2px solid transparent;
	background: none;
	color: inherit;
	cursor: pointer;
	transition: border-color var(--tcf-motion-base, 300ms) var(--tcf-ease-out, ease-out);
}
.tab.active {
	border-bottom-color: var(--tcf-accent-yellow, #f3bb19);
}
</style>
