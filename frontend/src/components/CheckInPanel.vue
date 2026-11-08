<script setup>
import dayjs from "dayjs";
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { __ } from "@/api/i18n";
import { getCheckinAddress, getCheckinStatus, submitCheckin } from "@/api/checkin";
import { onRealtime } from "@/api/realtime";
import BaseButton from "@/components/ui/BaseButton.vue";
import Pill from "@/components/ui/Pill.vue";
import SlantedPanel from "@/components/ui/SlantedPanel.vue";

const status = ref(null);
const addresses = ref({}); // check-in name -> text address (looked up on the server, may stay empty)
const busy = ref(false);
const message = ref("");
let stop = null;

const last = computed(() => status.value?.last);
const geolocation = computed(() => status.value?.capabilities?.geolocation);
const action = computed(() => status.value?.next_action || "IN");
const label = computed(() => (action.value === "IN" ? __("Check In") : __("Check Out")));

const coords = (log) =>
	log?.latitude || log?.longitude
		? `${Number(log.latitude).toFixed(5)}°, ${Number(log.longitude).toFixed(5)}°`
		: "";

const hasPosition = (log) => Boolean(log?.latitude || log?.longitude);

// The address is a nicety: a slow or failing service must never get in the way of the check-in
async function loadAddress(log) {
	if (!hasPosition(log) || log.name in addresses.value) return;
	addresses.value[log.name] = "";
	try {
		addresses.value[log.name] = (await getCheckinAddress(log.name)) || "";
	} catch {
		/* coordinates are shown anyway */
	}
}

async function load() {
	status.value = await getCheckinStatus();
	loadAddress(status.value.last);
}

function position() {
	// Resolves with the device position, or null if unavailable or refused; never blocks the check-in
	return new Promise((resolve) => {
		if (!navigator.geolocation) return resolve(null);
		navigator.geolocation.getCurrentPosition(
			(p) => resolve({ latitude: p.coords.latitude, longitude: p.coords.longitude }),
			() => resolve(null),
			{ timeout: 10000, maximumAge: 30000 }
		);
	});
}

async function submit() {
	busy.value = true;
	message.value = "";
	try {
		let where = null;
		if (geolocation.value) {
			message.value = __("Locating...");
			where = await position();
			if (!where) message.value = __("Location unavailable, checking in without it.");
		}
		status.value = await submitCheckin(action.value, where?.latitude, where?.longitude);
		loadAddress(status.value.last);
		message.value = "";
	} catch (error) {
		message.value = error.message || __("Check-in failed");
	} finally {
		busy.value = false;
	}
}

onMounted(() => {
	load();
	stop = onRealtime("tcf_hr:checkin", load);
});
onBeforeUnmount(() => stop?.());
</script>

<template>
	<SlantedPanel v-if="status">
		<h2 class="tf-app-heading">{{ __("Attendance") }}</h2>
		<p v-if="last">
			<Pill :tone="last.log_type === 'IN' ? 'success' : 'muted'">
				{{ last.log_type === "IN" ? __("Checked in") : __("Checked out") }}
			</Pill>
			{{ dayjs(last.time).format("DD MMM YYYY, HH:mm") }}
			<span v-if="coords(last)"> · {{ coords(last) }}</span>
		</p>
		<p v-if="addresses[last?.name]" class="tf-app-caption">{{ addresses[last.name] }}</p>
		<p v-else>{{ __("No check-ins yet.") }}</p>

		<BaseButton v-if="status.capabilities.check_in" :loading="busy" @click="submit">{{
			label
		}}</BaseButton>
		<p v-if="message" role="status">{{ message }}</p>
	</SlantedPanel>
</template>
