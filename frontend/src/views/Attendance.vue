<script setup>
import dayjs from "dayjs";
import { computed, onMounted, ref, watch } from "vue";
import { __ } from "@/api/i18n";
import { fmtDate } from "@/api/format";
import { getCheckinStatus } from "@/api/checkin";
import { getAttendanceCalendarEvents, getShifts } from "@/api/hr";
import MonthCalendar from "@/components/MonthCalendar.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import Pill from "@/components/ui/Pill.vue";
import Skeleton from "@/components/ui/Skeleton.vue";
import SlantedPanel from "@/components/ui/SlantedPanel.vue";
import Tabs from "@/components/ui/Tabs.vue";

// One panel for the whole page: a "Today" strip, then three tabs that share one fixed-height area, so switching
// tabs never changes the shape of the panel.
const tab = ref("calendar");
const month = ref(dayjs().startOf("month"));
const events = ref({});
const shifts = ref([]);
const history = ref([]);
const loading = ref(true);
const error = ref("");

const TABS = [
	{ key: "calendar", label: __("Calendar") },
	{ key: "checkins", label: __("Check-ins") },
	{ key: "shifts", label: __("Shifts") },
];

// Colour rule: green present, red absent, yellow for the in-between states, grey for holidays
const STATUSES = {
	Present: { label: __("Present"), tone: "success" },
	Absent: { label: __("Absent"), tone: "danger" },
	"On Leave": { label: __("On leave"), tone: "accent" },
	"Half Day": { label: __("Half day"), tone: "accent" },
	"Work From Home": { label: __("Work from home"), tone: "accent" },
	Holiday: { label: __("Holiday"), tone: "muted" },
};
const counts = computed(() => {
	const tally = {};
	Object.values(events.value).forEach((s) => (tally[s] = (tally[s] || 0) + 1));
	return Object.entries(tally).map(([status, n]) => ({
		status,
		n,
		...(STATUSES[status] || { label: status, tone: "accent" }),
	}));
});

const hhmm = (time) => {
	const [h, m] = String(time || "").split(":");
	return m === undefined ? "" : `${h.padStart(2, "0")}:${m}`;
};
const shiftTimes = (s) => `${hhmm(s.start_time)} – ${hhmm(s.end_time)}`;
const today = dayjs().format("YYYY-MM-DD");
const currentShift = computed(() =>
	shifts.value.find((s) => s.start_date <= today && (!s.end_date || s.end_date >= today))
);
const last = computed(() => history.value[0]);

async function loadMonth() {
	try {
		events.value = await getAttendanceCalendarEvents(
			month.value.format("YYYY-MM-DD"),
			month.value.endOf("month").format("YYYY-MM-DD")
		);
	} catch (e) {
		error.value = e.message;
	}
}

onMounted(async () => {
	try {
		const [, status, assigned] = await Promise.all([
			loadMonth(),
			getCheckinStatus(),
			getShifts(),
		]);
		history.value = status.history.slice(0, 10);
		shifts.value = assigned;
	} catch (e) {
		error.value = e.message;
	} finally {
		loading.value = false;
	}
});
watch(month, loadMonth);
</script>

<template>
	<SlantedPanel>
		<h1 class="tf-app-title">{{ __("Attendance") }}</h1>

		<!-- Today: the current shift and the last check-in -->
		<dl class="today">
			<div>
				<dt class="tf-app-label">{{ __("Today's shift") }}</dt>
				<dd class="tf-app-body">
					{{
						currentShift
							? `${currentShift.shift_type} · ${shiftTimes(currentShift)}`
							: __("No shift assigned")
					}}
				</dd>
			</div>
			<div>
				<dt class="tf-app-label">{{ __("Last check-in") }}</dt>
				<dd class="tf-app-body">
					<template v-if="last">
						<Pill :tone="last.log_type === 'IN' ? 'success' : 'muted'">{{
							last.log_type === "IN" ? __("In") : __("Out")
						}}</Pill>
						{{ dayjs(last.time).format("DD MMM, HH:mm") }}
					</template>
					<template v-else>{{ loading ? "…" : __("None yet") }}</template>
				</dd>
			</div>
		</dl>

		<Tabs v-model="tab" :items="TABS" :label="__('Attendance')" />

		<Transition name="fade" mode="out-in">
			<div :key="tab" class="area">
				<template v-if="tab === 'calendar'">
					<MonthCalendar v-model="month" :events="events" :statuses="STATUSES" />
					<ul class="legend">
						<li v-for="c in counts" :key="c.status">
							<Pill :tone="c.tone">{{ c.label }}</Pill>
							<span class="tf-app-caption">{{ c.n }}</span>
						</li>
					</ul>
					<div class="actions">
						<BaseButton variant="secondary" to="/requests/attendance-request/new">{{
							__("Attendance request")
						}}</BaseButton>
						<BaseButton variant="secondary" to="/requests/shift-request/new">{{
							__("Shift request")
						}}</BaseButton>
					</div>
				</template>

				<template v-else-if="tab === 'checkins'">
					<Skeleton v-if="loading" :lines="4" />
					<p v-else-if="!history.length">{{ __("No check-ins yet.") }}</p>
					<ul class="rows">
						<li v-for="c in history" :key="c.name" class="row">
							<Pill :tone="c.log_type === 'IN' ? 'success' : 'muted'">{{
								c.log_type === "IN" ? __("In") : __("Out")
							}}</Pill>
							<span class="tf-app-body">{{
								dayjs(c.time).format("DD MMM YYYY, HH:mm")
							}}</span>
						</li>
					</ul>
				</template>

				<template v-else>
					<Skeleton v-if="loading" :lines="3" />
					<p v-else-if="!shifts.length">{{ __("No active shift assignments.") }}</p>
					<ul class="rows">
						<li v-for="s in shifts" :key="s.name" class="row">
							<span class="tf-app-body"
								>{{ s.shift_type }}
								<span class="tf-app-caption">{{ shiftTimes(s) }}</span></span
							>
							<span class="tf-app-caption"
								>{{ fmtDate(s.start_date)
								}}{{ s.end_date ? ` – ${fmtDate(s.end_date)}` : "" }}</span
							>
						</li>
					</ul>
				</template>
			</div>
		</Transition>

		<Transition name="fade"
			><p v-if="error" class="error" role="alert">{{ error }}</p></Transition
		>
	</SlantedPanel>
</template>

<style scoped>
.today {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr));
	gap: var(--tcf-space-md, 1.5rem);
	margin: 0;
	padding-bottom: var(--tcf-space-sm, 1rem);
	border-bottom: 1px solid color-mix(in srgb, currentColor 20%, transparent); /* the one divider: header from tabs */
}
.today dd {
	margin: 0.4rem 0 0;
}
/* Every tab has the same minimum height (about a calendar), so the panel keeps its shape */
.area {
	display: grid;
	align-content: start;
	gap: var(--tcf-space-sm, 1rem);
	min-height: 26rem;
}
.legend {
	list-style: none;
	margin: 0;
	padding: 0;
	display: flex;
	flex-wrap: wrap;
	gap: var(--tcf-space-sm, 1rem);
}
.actions {
	display: flex;
	flex-wrap: wrap;
	gap: var(--tcf-space-sm, 1rem);
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
}
.error {
	margin: 0;
	color: var(--tcf-accent-red, #ce202a);
}
</style>
