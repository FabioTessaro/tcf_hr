<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { __ } from "@/api/i18n";
import { getList } from "@/api/gateway";
import BaseButton from "@/components/ui/BaseButton.vue";
import Pill from "@/components/ui/Pill.vue";
import SlantedPanel from "@/components/ui/SlantedPanel.vue";
import Skeleton from "@/components/ui/Skeleton.vue";
import { requestType } from "@/requests/config";
import { statusOf } from "@/requests/status";
import { useSession } from "@/stores/session";

const PAGE = 20;
const route = useRoute();
const router = useRouter();
const session = useSession();

const cfg = computed(() => requestType(route.params.slug));
const rows = ref([]);
const loading = ref(true);
const more = ref(false);
const error = ref("");
const tab = ref("all");
const TABS = [
	["all", "All"],
	["pending", "Pending"],
	["approved", "Approved"],
	["closed", "Closed"],
];

const canCreate = computed(() => session.capabilities.requests?.[cfg.value?.doctype]?.create);
const items = computed(() =>
	rows.value
		.map((doc) => ({ doc, status: statusOf(doc, cfg.value.statusField) }))
		.filter((item) => tab.value === "all" || item.status.group === tab.value)
);

async function load(reset = false) {
	if (!cfg.value) return router.replace("/home");
	loading.value = true;
	error.value = "";
	try {
		const page = await getList(cfg.value.doctype, {
			fields: [...new Set(["name", "docstatus", ...cfg.value.listFields])],
			filters: { employee: session.employee?.name },
			order_by: "creation desc",
			start: reset ? 0 : rows.value.length,
			page_length: PAGE,
		});
		rows.value = reset ? page : [...rows.value, ...page];
		more.value = page.length === PAGE;
	} catch (e) {
		error.value = e.message;
	} finally {
		loading.value = false;
	}
}

onMounted(() => load(true));
watch(
	() => route.params.slug,
	() => {
		rows.value = [];
		tab.value = "all";
		load(true);
	}
);
</script>

<template>
	<SlantedPanel v-if="cfg">
		<div class="head">
			<h1 class="tf-app-title">{{ __(cfg.title) }}</h1>
			<BaseButton v-if="canCreate" :to="`/requests/${cfg.slug}/new`">{{
				__("New")
			}}</BaseButton>
		</div>
		<div class="tabs" role="tablist">
			<button
				v-for="[key, label] in TABS"
				:key="key"
				type="button"
				role="tab"
				class="tab tf-app-nav"
				:class="{ active: tab === key }"
				:aria-selected="tab === key"
				@click="tab = key"
			>
				{{ __(label) }}
			</button>
		</div>
		<Skeleton v-if="loading && !rows.length" :lines="4" />
		<Transition name="fade"
			><p v-if="error" class="error" role="alert">{{ error }}</p></Transition
		>
		<p v-if="!loading && !items.length && !error">{{ __("Nothing here yet.") }}</p>
		<TransitionGroup tag="ul" name="stagger" class="rows">
			<li v-for="({ doc, status }, i) in items" :key="doc.name" :style="{ '--i': i }">
				<router-link :to="`/requests/${cfg.slug}/${doc.name}`" class="indicator-row row">
					<span class="row__text">
						<span class="tf-app-heading">{{ cfg.heading(doc) }}</span>
						<span class="tf-app-caption">{{ cfg.subline(doc) }}</span>
					</span>
					<Pill :tone="status.tone">{{ status.label }}</Pill>
				</router-link>
			</li>
		</TransitionGroup>
		<BaseButton v-if="more" variant="secondary" :loading="loading" @click="load()">{{
			__("Load more")
		}}</BaseButton>
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
	min-height: 64px;
	padding: var(--tcf-space-xs, 0.5rem) 0 var(--tcf-space-xs, 0.5rem) 0.6rem; /* left: room for the indicator */
	text-decoration: none;
}
.row__text {
	display: grid;
	gap: 0.25rem;
}
.error {
	color: var(--tcf-accent-red, #ce202a);
}
</style>
