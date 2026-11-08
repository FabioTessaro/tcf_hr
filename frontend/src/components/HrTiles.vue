<script setup>
import { computed } from "vue";
import { __ } from "@/api/i18n";
import Icon from "@/components/ui/Icon.vue";
import SlantedPanel from "@/components/ui/SlantedPanel.vue";
import { useSession } from "@/stores/session";

// Entry points to the dashboards, as a vertical list. Payslips only for users who may read them (the server decides).
const session = useSession();
const entries = computed(() =>
	[
		{ to: "/attendance", label: "Attendance", icon: "calendar_month" },
		{ to: "/leaves", label: "Leaves", icon: "beach_access" },
		{ to: "/claims", label: "Claims", icon: "receipt_long" },
		{ to: "/payslips", label: "Payslips", icon: "request_quote", capability: "payslips" },
	].filter((t) => !t.capability || session.can(t.capability))
);
</script>

<template>
	<SlantedPanel>
		<h2 class="tf-app-heading">{{ __("My HR") }}</h2>
		<TransitionGroup tag="ul" name="stagger" class="entries">
			<li v-for="(t, i) in entries" :key="t.to" :style="{ '--i': i }">
				<router-link :to="t.to" class="indicator-row tf-app-heading">
					<Icon :name="t.icon" />
					<span>{{ __(t.label) }}</span>
				</router-link>
			</li>
		</TransitionGroup>
	</SlantedPanel>
</template>

<style scoped>
h2 {
	margin: 0;
}
.entries {
	list-style: none;
	margin: 0;
	padding: 0;
}
</style>
