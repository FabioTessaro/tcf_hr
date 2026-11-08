<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { __ } from "@/api/i18n";
import {
	applyWorkflow,
	cancelDoc,
	deleteDoc,
	getDoc,
	getDocPermissions,
	getMeta,
	getTransitions,
	saveDoc,
	submitDoc,
} from "@/api/gateway";
import Attachments from "@/components/Attachments.vue";
import ExpenseRows from "@/components/ExpenseRows.vue";
import FormField from "@/components/FormField.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import Pill from "@/components/ui/Pill.vue";
import Skeleton from "@/components/ui/Skeleton.vue";
import SlantedPanel from "@/components/ui/SlantedPanel.vue";
import { requestType } from "@/requests/config";
import { statusOf } from "@/requests/status";
import { useSession } from "@/stores/session";

const route = useRoute();
const router = useRouter();
const session = useSession();

const cfg = computed(() => requestType(route.params.slug));
const name = computed(() => route.params.name);
const isNew = computed(() => !name.value);

const loading = ref(true);
const busy = ref(false);
const error = ref("");
const values = ref({});
const options = ref({});
const extraRequired = ref([]);
const doc = ref(null);
const perms = ref({});
const transitions = ref([]);
const hasWorkflow = ref(false);
const info = ref([]);
const attachments = ref(null);
const confirming = ref("");
let confirmTimer = null;
let infoTimer = null;

const ctx = () => ({ employee: session.employee });
const editable = computed(() => isNew.value || (doc.value?.docstatus === 0 && perms.value.write));
const status = computed(() => doc.value && statusOf(doc.value, cfg.value.statusField));
const visibleFields = computed(() =>
	cfg.value.fields.filter((f) => !f.showIf || f.showIf(values.value))
);
const isRequired = (f) => Boolean(f.required || extraRequired.value.includes(f.name));

const blankValue = (f) => (f.type === "check" ? 0 : f.type === "expenses" ? [] : "");
const toRows = (rows = []) =>
	rows.map((r, i) => ({
		_key: `r${i}`,
		expense_date: r.expense_date,
		expense_type: r.expense_type,
		description: r.description,
		amount: r.amount,
	}));

async function load() {
	if (!cfg.value) return router.replace("/home");
	if (!session.employee) return (loading.value = false);
	loading.value = true;
	error.value = "";
	try {
		const prepared = await cfg.value.prepare(ctx());
		options.value = prepared.options;
		extraRequired.value = prepared.required || [];

		if (isNew.value) {
			const base = {
				employee: session.employee.name,
				company: session.employee.company,
				...prepared.defaults,
			};
			cfg.value.fields.forEach((f) => !(f.name in base) && (base[f.name] = blankValue(f)));
			values.value = base;
			perms.value = { write: true };
			doc.value = null;
			transitions.value = [];
			hasWorkflow.value = false;
		} else {
			const d = await getDoc(cfg.value.doctype, name.value);
			doc.value = d;
			const picked = {};
			[...cfg.value.fields.map((f) => f.name), ...cfg.value.hidden].forEach(
				(key) => (picked[key] = d[key] ?? "")
			);
			if ("expenses" in picked) picked.expenses = toRows(d.expenses);
			values.value = picked;
			perms.value = await getDocPermissions(cfg.value.doctype, name.value);
			const meta = await getMeta(cfg.value.doctype);
			hasWorkflow.value = Boolean(meta.workflow?.name);
			transitions.value = hasWorkflow.value
				? await getTransitions(cfg.value.doctype, name.value)
				: [];
		}
	} catch (e) {
		error.value = e.message;
	} finally {
		loading.value = false;
	}
}

function missing() {
	const gaps = visibleFields.value.filter((f) => {
		if (!isRequired(f)) return false;
		const v = values.value[f.name];
		if (f.type === "expenses")
			return !v.length || v.some((r) => !r.expense_type || !Number(r.amount));
		return v === "" || v === null || v === undefined;
	});
	return gaps.map((f) => __(f.label));
}

function payload() {
	const out = { doctype: cfg.value.doctype };
	for (const [key, value] of Object.entries(values.value)) {
		out[key] = value === "" ? null : value;
	}
	if (out.expenses) {
		out.expenses = out.expenses.map((r) => ({
			expense_date: r.expense_date || null,
			expense_type: r.expense_type,
			description: r.description,
			amount: Number(r.amount),
			sanctioned_amount: Number(r.amount),
		}));
	}
	if (!isNew.value) Object.assign(out, { name: name.value, modified: doc.value.modified });
	return out;
}

async function run(action, after) {
	busy.value = true;
	error.value = "";
	try {
		await action();
		await after?.();
	} catch (e) {
		error.value = e.message;
	} finally {
		busy.value = false;
		confirming.value = "";
	}
}

function save() {
	const gaps = missing();
	if (gaps.length) {
		error.value = __("Please fill in: {0}", [gaps.join(", ")]);
		return;
	}
	return run(async () => {
		const saved = await saveDoc(payload());
		if (isNew.value) {
			await attachments.value?.flush(saved.name);
			router.replace(`/requests/${cfg.value.slug}/${saved.name}`);
		} else {
			await load();
		}
	});
}

// Destructive actions ask for a second click
function ask(key, action, after) {
	if (confirming.value !== key) {
		confirming.value = key;
		clearTimeout(confirmTimer);
		confirmTimer = setTimeout(() => (confirming.value = ""), 4000);
		return;
	}
	run(action, after);
}

const submit = () => run(() => submitDoc(cfg.value.doctype, name.value), load);
const cancel = () => ask("cancel", () => cancelDoc(cfg.value.doctype, name.value), load);
const remove = () =>
	ask(
		"delete",
		() => deleteDoc(cfg.value.doctype, name.value),
		() => router.replace(`/requests/${cfg.value.slug}`)
	);
const transition = (t) => run(() => applyWorkflow(cfg.value.doctype, name.value, t.action), load);

// Figures such as the leave balance follow the form, a moment after the last change
watch(
	values,
	() => {
		if (!cfg.value?.info || !editable.value) return;
		clearTimeout(infoTimer);
		infoTimer = setTimeout(async () => {
			try {
				info.value = await cfg.value.info(values.value, ctx());
			} catch {
				info.value = [];
			}
		}, 400);
	},
	{ deep: true }
);

onMounted(load);
onBeforeUnmount(() => {
	clearTimeout(confirmTimer);
	clearTimeout(infoTimer);
});
</script>

<template>
	<SlantedPanel v-if="cfg">
		<div class="head">
			<h1 class="tf-app-title">{{ isNew ? __("New request") : name }}</h1>
			<Pill v-if="status" :tone="status.tone">{{ status.label }}</Pill>
		</div>
		<p class="tf-app-caption">{{ __(cfg.singular) }}</p>

		<p v-if="!session.employee">
			{{ __("No active employee record is linked to this account.") }}
		</p>
		<Skeleton v-else-if="loading" :lines="5" />
		<form v-else class="form" novalidate @submit.prevent="save">
			<template v-for="f in visibleFields" :key="f.name">
				<ExpenseRows
					v-if="f.type === 'expenses'"
					v-model="values.expenses"
					:type-options="options.expense_type"
					:currency="values.currency"
					:readonly="!editable"
				/>
				<FormField
					v-else
					v-model="values[f.name]"
					:field="f"
					:options="options[f.name]"
					:readonly="!editable"
					:required="isRequired(f)"
				/>
			</template>

			<dl v-if="info.length && editable" class="info">
				<template v-for="[term, value] in info" :key="term">
					<dt class="tf-app-label">{{ term }}</dt>
					<dd>{{ value }}</dd>
				</template>
			</dl>

			<Attachments
				ref="attachments"
				:doctype="cfg.doctype"
				:name="name"
				:editable="Boolean(editable)"
			/>

			<Transition name="fade"
				><p v-if="error" class="error" role="alert">{{ error }}</p></Transition
			>

			<div class="actions">
				<BaseButton v-if="editable" type="submit" :loading="busy">{{
					__("Save")
				}}</BaseButton>
				<BaseButton
					v-if="!isNew && !hasWorkflow && doc?.docstatus === 0 && perms.submit"
					variant="secondary"
					:loading="busy"
					@click="submit"
					>{{ __("Submit") }}</BaseButton
				>
				<BaseButton
					v-for="t in transitions"
					:key="t.action"
					variant="secondary"
					:loading="busy"
					@click="transition(t)"
					>{{ __(t.action) }}</BaseButton
				>
				<BaseButton
					v-if="!isNew && !hasWorkflow && doc?.docstatus === 1 && perms.cancel"
					variant="danger"
					:loading="busy"
					@click="cancel"
				>
					{{ confirming === "cancel" ? __("Confirm cancel") : __("Cancel request") }}
				</BaseButton>
				<BaseButton
					v-if="!isNew && doc?.docstatus === 0 && perms.delete"
					variant="danger"
					:loading="busy"
					@click="remove"
				>
					{{ confirming === "delete" ? __("Confirm delete") : __("Delete") }}
				</BaseButton>
				<BaseButton variant="secondary" :to="`/requests/${cfg.slug}`">{{
					__("Back")
				}}</BaseButton>
			</div>
		</form>
	</SlantedPanel>
</template>

<style scoped>
.head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: var(--tcf-space-sm, 1rem);
	flex-wrap: wrap;
}
.form {
	display: grid;
	gap: var(--tcf-space-md, 1.5rem);
}
.info {
	display: grid;
	grid-template-columns: max-content 1fr;
	gap: var(--tcf-space-xs, 0.5rem) var(--tcf-space-md, 1.5rem);
	margin: 0;
}
.info dd {
	margin: 0;
}
.actions {
	display: flex;
	flex-wrap: wrap;
	gap: var(--tcf-space-sm, 1rem);
}
.error {
	margin: 0;
	color: var(--tcf-accent-red, #ce202a);
}
</style>
