<script setup>
import dayjs from "dayjs";
import { computed, useId } from "vue";
import { __ } from "@/api/i18n";

// One labelled form control. `field` comes from requests/config.js. In read-only mode it shows the value as text.
const props = defineProps({
	field: { type: Object, required: true },
	modelValue: { default: "" },
	options: { type: Array, default: () => [] },
	readonly: Boolean,
	required: Boolean,
});
const emit = defineEmits(["update:modelValue"]);

const id = useId();
const update = (value) => emit("update:modelValue", value);

const display = computed(() => {
	const value = props.modelValue;
	if (props.field.type === "check") return value ? __("Yes") : __("No");
	if (props.field.type === "date") return value ? dayjs(value).format("DD MMM YYYY") : "";
	if (props.field.type === "select")
		return props.options.find((o) => o.value === value)?.label || value;
	return value;
});
</script>

<template>
	<div class="field" :class="{ 'field--check': field.type === 'check' }">
		<!-- Check boxes carry their label on the right; everything else has it on top -->
		<template v-if="field.type === 'check' && !readonly">
			<input
				:id="id"
				type="checkbox"
				:checked="Boolean(modelValue)"
				@change="update($event.target.checked ? 1 : 0)"
			/>
			<label :for="id" class="tf-app-body">{{ __(field.label) }}</label>
		</template>
		<template v-else>
			<label :for="id" class="tf-app-label"
				>{{ __(field.label)
				}}<span v-if="required && !readonly" aria-hidden="true"> *</span></label
			>
			<p v-if="readonly" class="value">{{ display || "–" }}</p>
			<select
				v-else-if="field.type === 'select'"
				:id="id"
				:value="modelValue"
				:required="required"
				@change="update($event.target.value)"
			>
				<option v-if="!required" value="" />
				<option v-for="o in options" :key="o.value" :value="o.value">{{ o.label }}</option>
			</select>
			<textarea
				v-else-if="field.type === 'text'"
				:id="id"
				rows="3"
				:value="modelValue"
				:required="required"
				@input="update($event.target.value)"
			/>
			<input
				v-else-if="field.type === 'date'"
				:id="id"
				type="date"
				:value="modelValue"
				:required="required"
				@input="update($event.target.value)"
			/>
			<input
				v-else-if="field.type === 'currency'"
				:id="id"
				type="number"
				min="0"
				step="0.01"
				inputmode="decimal"
				:value="modelValue"
				:required="required"
				@input="update($event.target.value)"
			/>
			<input
				v-else
				:id="id"
				type="text"
				:value="modelValue"
				:required="required"
				@input="update($event.target.value)"
			/>
		</template>
	</div>
</template>

<style scoped>
.field {
	display: grid;
	gap: var(--tcf-space-xs, 0.5rem);
}
.field--check {
	display: flex;
	align-items: center;
	gap: var(--tcf-space-xs, 0.5rem);
	min-height: 44px;
}
input[type="checkbox"] {
	width: 1.25rem;
	height: 1.25rem;
	accent-color: var(--tcf-accent-yellow, #f3bb19);
}
input:not([type="checkbox"]),
select,
textarea {
	font: inherit;
	color: inherit;
	min-height: 44px;
	padding: 0.5rem 0;
	border: 0;
	border-bottom: 1px solid var(--tcf-primary-light, #4a4a4a);
	border-radius: 0;
	background: transparent;
	transition: border-color var(--tcf-motion-base, 300ms) var(--tcf-ease-out, ease-out);
}
select {
	/* options inherit the page colours instead of the browser's light popup in dark mode */
	background: var(--tcf-surface, #e0e0e0);
}
input:not([type="checkbox"]):focus,
select:focus,
textarea:focus {
	outline: none;
	border-bottom: 2px solid var(--tcf-accent-yellow, #f3bb19);
	padding-bottom: calc(0.5rem - 1px);
}
.value {
	margin: 0;
	min-height: 44px;
	display: flex;
	align-items: center;
	overflow-wrap: anywhere;
}
</style>
