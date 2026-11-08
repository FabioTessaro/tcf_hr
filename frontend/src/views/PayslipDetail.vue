<script setup>
import dayjs from "dayjs";
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { __ } from "@/api/i18n";
import { fmtDate, money } from "@/api/format";
import { getDoc } from "@/api/gateway";
import BaseButton from "@/components/ui/BaseButton.vue";
import Skeleton from "@/components/ui/Skeleton.vue";
import SlantedPanel from "@/components/ui/SlantedPanel.vue";

const route = useRoute();
const slip = ref(null);
const error = ref("");

// Statistical components are informational (they are not part of the pay): leave them out of the tables
const lines = (rows) => (rows || []).filter((r) => !r.statistical_component && Number(r.amount));
const earnings = computed(() => lines(slip.value?.earnings));
const deductions = computed(() => lines(slip.value?.deductions));
const c = computed(() => slip.value?.currency);
const pdf = computed(
	() => `/api/method/tcf_hr.api.payslips.download?name=${encodeURIComponent(route.params.name)}`
);

onMounted(async () => {
	try {
		slip.value = await getDoc("Salary Slip", route.params.name);
	} catch (e) {
		error.value = e.message;
	}
});
</script>

<template>
	<SlantedPanel>
		<div class="head">
			<h1 class="tf-app-title">
				{{ slip ? dayjs(slip.end_date).format("MMMM YYYY") : __("Payslip") }}
			</h1>
			<BaseButton v-if="slip" :href="pdf" download>{{ __("Download PDF") }}</BaseButton>
		</div>
		<Skeleton v-if="!slip && !error" :lines="5" />
		<Transition name="fade"
			><p v-if="error" class="error" role="alert">{{ error }}</p></Transition
		>

		<template v-if="slip">
			<p class="tf-app-caption">
				{{ fmtDate(slip.start_date) }} – {{ fmtDate(slip.end_date) }} · {{ slip.name }}
			</p>

			<section v-if="earnings.length">
				<h2 class="tf-app-heading">{{ __("Earnings") }}</h2>
				<dl class="lines">
					<template v-for="r in earnings" :key="r.name || r.salary_component">
						<dt class="tf-app-body">{{ r.salary_component }}</dt>
						<dd class="tf-app-body">{{ money(r.amount, c) }}</dd>
					</template>
					<dt class="tf-app-label">{{ __("Gross pay") }}</dt>
					<dd class="tf-app-heading">{{ money(slip.gross_pay, c) }}</dd>
				</dl>
			</section>

			<section v-if="deductions.length">
				<h2 class="tf-app-heading">{{ __("Deductions") }}</h2>
				<dl class="lines">
					<template v-for="r in deductions" :key="r.name || r.salary_component">
						<dt class="tf-app-body">{{ r.salary_component }}</dt>
						<dd class="tf-app-body">{{ money(r.amount, c) }}</dd>
					</template>
					<dt class="tf-app-label">{{ __("Total deductions") }}</dt>
					<dd class="tf-app-heading">{{ money(slip.total_deduction, c) }}</dd>
				</dl>
			</section>

			<dl class="lines net">
				<dt class="tf-app-label">{{ __("Net pay") }}</dt>
				<dd class="tf-app-title">{{ money(slip.net_pay, c) }}</dd>
			</dl>

			<dl class="lines">
				<template v-if="slip.payment_days">
					<dt class="tf-app-label">{{ __("Payment days") }}</dt>
					<dd class="tf-app-body">
						{{ slip.payment_days }} / {{ slip.total_working_days }}
					</dd>
				</template>
				<template v-if="slip.leave_without_pay">
					<dt class="tf-app-label">{{ __("Leave without pay") }}</dt>
					<dd class="tf-app-body">{{ slip.leave_without_pay }}</dd>
				</template>
			</dl>
		</template>
		<BaseButton variant="secondary" to="/payslips">{{ __("Back") }}</BaseButton>
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
section {
	display: grid;
	gap: var(--tcf-space-xs, 0.5rem);
}
h2 {
	margin: 0;
}
.lines {
	display: grid;
	grid-template-columns: 1fr auto;
	gap: var(--tcf-space-xs, 0.5rem) var(--tcf-space-md, 1.5rem);
	margin: 0;
}
.lines dd {
	margin: 0;
	text-align: right;
}
.net {
	align-items: baseline;
	padding-top: var(--tcf-space-sm, 1rem);
	border-top: 1px solid color-mix(in srgb, currentColor 30%, transparent);
}
.error {
	margin: 0;
	color: var(--tcf-accent-red, #ce202a);
}
</style>
