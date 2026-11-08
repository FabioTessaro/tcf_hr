<script setup>
import { computed } from "vue";
import { __ } from "@/api/i18n";
import BaseButton from "@/components/ui/BaseButton.vue";
import FormField from "@/components/FormField.vue";

// The rows of an expense claim. Rows are plain objects; `_key` is only for v-for and is stripped when saving.
const rows = defineModel({ type: Array, default: () => [] });
const props = defineProps({
	typeOptions: { type: Array, default: () => [] },
	readonly: Boolean,
	currency: String,
});

const FIELDS = {
	expense_date: { name: "expense_date", label: "Date", type: "date" },
	expense_type: { name: "expense_type", label: "Type", type: "select" },
	description: { name: "description", label: "Description", type: "text" },
	amount: { name: "amount", label: "Amount", type: "currency" },
};

let counter = 0;
const blank = () => ({
	_key: ++counter,
	expense_date: new Date().toISOString().slice(0, 10),
	expense_type: "",
	description: "",
	amount: "",
});
const total = computed(() => rows.value.reduce((sum, row) => sum + Number(row.amount || 0), 0));

function add() {
	rows.value = [...rows.value, blank()];
}
function remove(index) {
	rows.value = rows.value.filter((_, i) => i !== index);
}
function set(index, name, value) {
	rows.value = rows.value.map((row, i) => (i === index ? { ...row, [name]: value } : row));
}
</script>

<template>
	<div class="rows">
		<TransitionGroup name="stagger">
			<fieldset
				v-for="(row, index) in rows"
				:key="row._key ?? row.name ?? index"
				class="row"
				:style="{ '--i': index }"
			>
				<legend class="tf-app-label">{{ __("Expense {0}", [index + 1]) }}</legend>
				<FormField
					:field="FIELDS.expense_date"
					:model-value="row.expense_date"
					:readonly="readonly"
					@update:model-value="set(index, 'expense_date', $event)"
				/>
				<FormField
					:field="FIELDS.expense_type"
					:model-value="row.expense_type"
					:options="typeOptions"
					:readonly="readonly"
					required
					@update:model-value="set(index, 'expense_type', $event)"
				/>
				<FormField
					:field="FIELDS.description"
					:model-value="row.description"
					:readonly="readonly"
					@update:model-value="set(index, 'description', $event)"
				/>
				<FormField
					:field="FIELDS.amount"
					:model-value="row.amount"
					:readonly="readonly"
					required
					@update:model-value="set(index, 'amount', $event)"
				/>
				<BaseButton v-if="!readonly" variant="secondary" @click="remove(index)">{{
					__("Remove")
				}}</BaseButton>
			</fieldset>
		</TransitionGroup>
		<BaseButton v-if="!readonly" variant="secondary" @click="add">{{
			__("Add expense")
		}}</BaseButton>
		<p class="total tf-app-heading">
			{{ __("Total") }}: {{ total.toLocaleString(undefined, { minimumFractionDigits: 2 }) }}
			{{ props.currency }}
		</p>
	</div>
</template>

<style scoped>
.rows {
	display: grid;
	gap: var(--tcf-space-sm, 1rem);
}
.row {
	display: grid;
	gap: var(--tcf-space-sm, 1rem);
	margin: 0;
	padding: var(--tcf-space-sm, 1rem) 0 0;
	border: 0;
	border-top: 1px solid var(--tcf-primary-light, #4a4a4a);
}
.total {
	margin: 0;
	text-align: right;
}
</style>
