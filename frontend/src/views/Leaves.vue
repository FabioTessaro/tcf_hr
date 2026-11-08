<script setup>
import dayjs from "dayjs";
import { computed, onMounted, ref } from "vue";
import { __ } from "@/api/i18n";
import { fmtDate } from "@/api/format";
import { getList } from "@/api/gateway";
import { getHolidaysForEmployee, getLeaveBalanceMap } from "@/api/hr";
import BaseButton from "@/components/ui/BaseButton.vue";
import Pill from "@/components/ui/Pill.vue";
import Skeleton from "@/components/ui/Skeleton.vue";
import SlantedPanel from "@/components/ui/SlantedPanel.vue";
import { statusOf } from "@/requests/status";
import { useSession } from "@/stores/session";

const session = useSession();
const balances = ref({});
const holidays = ref([]);
const recent = ref([]);
const loading = ref(true);
const error = ref("");

const canApply = computed(() => session.capabilities.requests?.["Leave Application"]?.create);
const types = computed(() =>
	Object.entries(balances.value).map(([name, d]) => {
		const total = Number(d.allocated_leaves || 0);
		const left = Number(d.balance_leaves || 0);
		return { name, total, left, share: total ? Math.max(0, Math.min(1, left / total)) : 0 };
	})
);

onMounted(async () => {
	try {
		const today = dayjs().format("YYYY-MM-DD");
		const [map, days, applications] = await Promise.all([
			getLeaveBalanceMap(),
			getHolidaysForEmployee(session.employee.name),
			session.capabilities.requests?.["Leave Application"]
				? getList("Leave Application", {
						fields: [
							"name",
							"leave_type",
							"from_date",
							"to_date",
							"status",
							"docstatus",
						],
						filters: { employee: session.employee.name },
						order_by: "creation desc",
						page_length: 5,
				  })
				: [],
		]);
		balances.value = map;
		holidays.value = days.filter((h) => h.holiday_date >= today).slice(0, 8);
		recent.value = applications;
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
			<h1 class="tf-app-title">{{ __("Leaves") }}</h1>
			<BaseButton v-if="canApply" to="/requests/leave/new">{{
				__("Apply for leave")
			}}</BaseButton>
		</div>
		<Skeleton v-if="loading" :lines="3" />
		<Transition name="fade"
			><p v-if="error" class="error" role="alert">{{ error }}</p></Transition
		>
		<p v-if="!loading && !types.length && !error">
			{{ __("No leave has been allocated to you.") }}
		</p>
		<TransitionGroup tag="ul" name="stagger" class="balances">
			<li v-for="(t, i) in types" :key="t.name" :style="{ '--i': i }">
				<div class="balance">
					<span class="tf-app-heading">{{ t.name }}</span>
					<span class="tf-app-body">{{
						__("{0} of {1} days left", [t.left, t.total])
					}}</span>
				</div>
				<div
					class="bar"
					role="img"
					:aria-label="__('{0} of {1} days left', [t.left, t.total])"
				>
					<span class="bar__fill" :style="{ width: `${t.share * 100}%` }" />
				</div>
			</li>
		</TransitionGroup>
	</SlantedPanel>

	<SlantedPanel v-if="holidays.length">
		<h2 class="tf-app-heading">{{ __("Upcoming holidays") }}</h2>
		<ul class="rows">
			<li v-for="h in holidays" :key="h.name" class="row">
				<span class="tf-app-body">{{ h.description || __("Holiday") }}</span>
				<span class="tf-app-caption">{{ fmtDate(h.holiday_date) }}</span>
			</li>
		</ul>
	</SlantedPanel>

	<SlantedPanel v-if="recent.length">
		<div class="head">
			<h2 class="tf-app-heading">{{ __("Recent applications") }}</h2>
			<BaseButton variant="secondary" to="/requests/leave">{{ __("All") }}</BaseButton>
		</div>
		<ul class="rows">
			<li v-for="d in recent" :key="d.name">
				<router-link :to="`/requests/leave/${d.name}`" class="row">
					<span class="tf-app-body"
						>{{ d.leave_type }}
						<span class="tf-app-caption"
							>{{ fmtDate(d.from_date)
							}}{{
								d.to_date !== d.from_date ? ` – ${fmtDate(d.to_date)}` : ""
							}}</span
						></span
					>
					<Pill :tone="statusOf(d, 'status').tone">{{
						statusOf(d, "status").label
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
.balances,
.rows {
	list-style: none;
	margin: 0;
	padding: 0;
	display: grid;
	gap: var(--tcf-space-sm, 1rem);
}
.balance {
	display: flex;
	justify-content: space-between;
	align-items: baseline;
	gap: var(--tcf-space-sm, 1rem);
	flex-wrap: wrap;
}
/* Slanted progress bar: the yellow part is what is left */
.bar {
	height: 0.4rem;
	margin-top: 0.4rem;
	background: color-mix(in srgb, currentColor 15%, transparent);
	transform: skewX(calc(-1 * var(--tcf-slant, 10deg)));
}
.bar__fill {
	display: block;
	height: 100%;
	background: var(--tcf-accent-yellow, #f3bb19);
	transition: width var(--tcf-motion-slow, 500ms) var(--tcf-ease-out, ease-out);
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
