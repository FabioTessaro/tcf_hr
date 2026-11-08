<script setup>
import dayjs from "dayjs";
import { computed, onMounted, ref } from "vue";
import { __ } from "@/api/i18n";
import { money } from "@/api/format";
import { getList } from "@/api/gateway";
import BaseButton from "@/components/ui/BaseButton.vue";
import Skeleton from "@/components/ui/Skeleton.vue";
import SlantedPanel from "@/components/ui/SlantedPanel.vue";
import { useSession } from "@/stores/session";

const PAGE = 24;
const session = useSession();
const slips = ref([]);
const loading = ref(true);
const more = ref(false);
const error = ref("");
const year = ref("all");

const years = computed(() => [
	...new Set(slips.value.map((s) => dayjs(s.end_date).format("YYYY"))),
]);
const visible = computed(() =>
	slips.value.filter(
		(s) => year.value === "all" || dayjs(s.end_date).format("YYYY") === year.value
	)
);

async function load(reset = false) {
	loading.value = true;
	error.value = "";
	try {
		// Only submitted slips are offered: drafts are not payslips yet
		const page = await getList("Salary Slip", {
			fields: ["name", "start_date", "end_date", "net_pay", "currency"],
			filters: { employee: session.employee.name, docstatus: 1 },
			order_by: "end_date desc",
			start: reset ? 0 : slips.value.length,
			page_length: PAGE,
		});
		slips.value = reset ? page : [...slips.value, ...page];
		more.value = page.length === PAGE;
	} catch (e) {
		error.value = e.message;
	} finally {
		loading.value = false;
	}
}
onMounted(() => load(true));
</script>

<template>
	<SlantedPanel>
		<h1 class="tf-app-title">{{ __("Payslips") }}</h1>
		<div v-if="years.length > 1" class="tabs" role="tablist">
			<button
				v-for="y in ['all', ...years]"
				:key="y"
				type="button"
				role="tab"
				class="tab tf-app-nav"
				:class="{ active: year === y }"
				:aria-selected="year === y"
				@click="year = y"
			>
				{{ y === "all" ? __("All") : y }}
			</button>
		</div>
		<Skeleton v-if="loading && !slips.length" :lines="4" />
		<Transition name="fade"
			><p v-if="error" class="error" role="alert">{{ error }}</p></Transition
		>
		<p v-if="!loading && !visible.length && !error">{{ __("No payslips yet.") }}</p>
		<TransitionGroup tag="ul" name="stagger" class="rows">
			<li v-for="(s, i) in visible" :key="s.name" :style="{ '--i': i }">
				<router-link :to="`/payslips/${s.name}`" class="indicator-row row">
					<span class="tf-app-heading">{{ dayjs(s.end_date).format("MMMM YYYY") }}</span>
					<span class="tf-app-body">{{ money(s.net_pay, s.currency) }}</span>
				</router-link>
			</li>
		</TransitionGroup>
		<BaseButton v-if="more" variant="secondary" :loading="loading" @click="load()">{{
			__("Load more")
		}}</BaseButton>
	</SlantedPanel>
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
.rows {
	list-style: none;
	margin: 0;
	padding: 0;
}
.row {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: var(--tcf-space-sm, 1rem);
	min-height: 56px;
	text-decoration: none;
}
.error {
	margin: 0;
	color: var(--tcf-accent-red, #ce202a);
}
</style>
