<script setup>
import { computed, onMounted, ref } from "vue";
import { __ } from "@/api/i18n";
import { fmtDate, money } from "@/api/format";
import { getList } from "@/api/gateway";
import { getEmployeeAdvanceBalance, getExpenseClaimSummary } from "@/api/hr";
import BaseButton from "@/components/ui/BaseButton.vue";
import Pill from "@/components/ui/Pill.vue";
import Skeleton from "@/components/ui/Skeleton.vue";
import SlantedPanel from "@/components/ui/SlantedPanel.vue";
import { statusOf } from "@/requests/status";
import { useSession } from "@/stores/session";

const session = useSession();
const summary = ref(null);
const advances = ref([]);
const recent = ref([]);
const loading = ref(true);
const error = ref("");

const can = (doctype, ptype) => session.capabilities.requests?.[doctype]?.[ptype];
const stats = computed(() => {
	const s = summary.value || {};
	const c = s.currency;
	return [
		{ label: __("Pending"), tone: "accent", value: money(s.total_pending_amount, c) },
		{ label: __("Approved"), tone: "success", value: money(s.total_approved_amount, c) },
		{ label: __("Rejected"), tone: "danger", value: money(s.total_rejected_amount, c) },
	];
});

onMounted(async () => {
	try {
		const [sum, adv, claims] = await Promise.all([
			getExpenseClaimSummary(),
			getEmployeeAdvanceBalance(),
			session.capabilities.requests?.["Expense Claim"]
				? getList("Expense Claim", {
						fields: [
							"name",
							"posting_date",
							"total_claimed_amount",
							"currency",
							"approval_status",
							"docstatus",
						],
						filters: { employee: session.employee.name },
						order_by: "creation desc",
						page_length: 5,
				  })
				: [],
		]);
		summary.value = sum;
		advances.value = adv;
		recent.value = claims;
	} catch (e) {
		error.value = e.message;
	} finally {
		loading.value = false;
	}
});
</script>

<template>
	<SlantedPanel>
		<div class="head">
			<h1 class="tf-app-title">{{ __("Claims") }}</h1>
			<div class="buttons">
				<BaseButton
					v-if="can('Expense Claim', 'create')"
					to="/requests/expense-claim/new"
					>{{ __("New claim") }}</BaseButton
				>
				<BaseButton
					v-if="can('Employee Advance', 'create')"
					variant="secondary"
					to="/requests/advance/new"
					>{{ __("New advance") }}</BaseButton
				>
			</div>
		</div>
		<Skeleton v-if="loading" :lines="3" />
		<Transition name="fade"
			><p v-if="error" class="error" role="alert">{{ error }}</p></Transition
		>
		<dl v-if="summary" class="stats">
			<div v-for="s in stats" :key="s.label" class="stat">
				<dt>
					<Pill :tone="s.tone">{{ s.label }}</Pill>
				</dt>
				<dd class="tf-app-heading">{{ s.value }}</dd>
			</div>
		</dl>
	</SlantedPanel>

	<SlantedPanel v-if="advances.length">
		<h2 class="tf-app-heading">{{ __("Advances to settle") }}</h2>
		<ul class="rows">
			<li v-for="a in advances" :key="a.name">
				<router-link :to="`/requests/advance/${a.name}`" class="row">
					<span class="tf-app-body"
						>{{ a.purpose }}
						<span class="tf-app-caption">{{ fmtDate(a.posting_date) }}</span></span
					>
					<span class="tf-app-heading">{{ money(a.balance_amount, a.currency) }}</span>
				</router-link>
			</li>
		</ul>
	</SlantedPanel>

	<SlantedPanel v-if="recent.length">
		<div class="head">
			<h2 class="tf-app-heading">{{ __("Recent claims") }}</h2>
			<BaseButton variant="secondary" to="/requests/expense-claim">{{
				__("All")
			}}</BaseButton>
		</div>
		<ul class="rows">
			<li v-for="c in recent" :key="c.name">
				<router-link :to="`/requests/expense-claim/${c.name}`" class="row">
					<span class="tf-app-body"
						>{{ money(c.total_claimed_amount, c.currency) }}
						<span class="tf-app-caption">{{ fmtDate(c.posting_date) }}</span></span
					>
					<Pill :tone="statusOf(c, 'approval_status').tone">{{
						statusOf(c, "approval_status").label
					}}</Pill>
				</router-link>
			</li>
		</ul>
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
.buttons {
	display: flex;
	gap: var(--tcf-space-sm, 1rem);
	flex-wrap: wrap;
}
.stats {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr));
	gap: var(--tcf-space-md, 1.5rem);
	margin: 0;
}
.stat {
	display: grid;
	gap: var(--tcf-space-xs, 0.5rem);
	justify-items: start;
}
dd {
	margin: 0;
}
.rows {
	list-style: none;
	margin: 0;
	padding: 0;
	display: grid;
	gap: var(--tcf-space-xs, 0.5rem);
}
.row {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: var(--tcf-space-sm, 1rem);
	min-height: 44px;
	text-decoration: none;
}
.error {
	margin: 0;
	color: var(--tcf-accent-red, #ce202a);
}
</style>
