<script setup>
import dayjs from "dayjs";
import { computed } from "vue";
import { __ } from "@/api/i18n";
import Icon from "@/components/ui/Icon.vue";

// Read-only month grid, weeks start on Monday. `events` is {"YYYY-MM-DD": status}; `statuses` maps a status to
// { label, tone } (tone: accent | muted | success | danger, the same names as Pill and Indicator).
const month = defineModel({ type: Object, required: true }); // a dayjs at the first day of the month
const props = defineProps({
	events: { type: Object, default: () => ({}) },
	statuses: { type: Object, default: () => ({}) },
});

const weekdays = computed(() =>
	[0, 1, 2, 3, 4, 5, 6].map((i) =>
		dayjs()
			.startOf("week")
			.add(i + 1, "day")
			.format("dd")
	)
);
const lead = computed(() => (month.value.day() + 6) % 7); // blank cells before the 1st (Monday first)
const days = computed(() =>
	Array.from({ length: month.value.daysInMonth() }, (_, i) => {
		const date = month.value.add(i, "day");
		const key = date.format("YYYY-MM-DD");
		return {
			number: i + 1,
			key,
			status: props.events[key],
			today: date.isSame(dayjs(), "day"),
		};
	})
);
const label = (day) => {
	const status = props.statuses[day.status]?.label || day.status;
	return status ? `${day.number}, ${status}` : String(day.number);
};
const step = (n) => (month.value = month.value.add(n, "month"));
</script>

<template>
	<div class="calendar">
		<div class="bar">
			<button
				type="button"
				class="step"
				:aria-label="__('Previous month')"
				@click="step(-1)"
			>
				<Icon name="chevron_left" />
			</button>
			<h2 class="tf-app-heading">{{ month.format("MMMM YYYY") }}</h2>
			<button type="button" class="step" :aria-label="__('Next month')" @click="step(1)">
				<Icon name="chevron_right" />
			</button>
		</div>
		<div class="grid" role="grid">
			<span
				v-for="d in weekdays"
				:key="d"
				class="weekday tf-app-label"
				role="columnheader"
				>{{ d }}</span
			>
			<span v-for="n in lead" :key="`b${n}`" aria-hidden="true" />
			<span
				v-for="day in days"
				:key="day.key"
				class="day tf-app-body"
				:class="{ today: day.today }"
				role="gridcell"
				:aria-label="label(day)"
			>
				{{ day.number }}
				<span
					v-if="day.status"
					class="mark"
					:class="`tone-${statuses[day.status]?.tone || 'accent'}`"
				/>
			</span>
		</div>
	</div>
</template>

<style scoped>
.bar {
	display: flex;
	align-items: center;
	justify-content: space-between;
}
h2 {
	margin: 0;
}
.step {
	min-width: 44px;
	min-height: 44px;
	border: 0;
	background: none;
	color: inherit;
	cursor: pointer;
}
.grid {
	display: grid;
	grid-template-columns: repeat(7, 1fr);
	gap: 0.25rem;
	text-align: center;
}
.weekday {
	padding-bottom: 0.25rem;
}
.day {
	position: relative;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: 0.2rem;
	min-height: 2.75rem;
}
.day.today {
	outline: 1px solid var(--tcf-accent-yellow, #f3bb19);
	outline-offset: -1px;
}
/* A slanted mark under the number: colour tells the status (the label is in aria-label and the legend) */
.mark {
	width: 1.1rem;
	height: 0.25rem;
	transform: skewX(calc(-1 * var(--tcf-slant, 10deg)));
}
.tone-accent {
	background: var(--tcf-accent-yellow, #f3bb19);
}
.tone-muted {
	background: var(--tcf-primary-light, #4a4a4a);
	opacity: 0.5;
}
.tone-success {
	background: var(--tcf-accent-green, #018c45);
}
.tone-danger {
	background: var(--tcf-accent-red, #ce202a);
}
</style>
