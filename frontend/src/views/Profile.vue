<script setup>
import dayjs from "dayjs";
import { computed, onMounted, ref } from "vue";
import { __ } from "@/api/i18n";
import { logout } from "@/api/auth";
import { getProfile } from "@/api/profile";
import Avatar from "@/components/ui/Avatar.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import SlantedPanel from "@/components/ui/SlantedPanel.vue";
import { useSession } from "@/stores/session";

const session = useSession();
const profile = ref(null);
const busy = ref(false);

// Shown from the session first, so the page is useful before the full profile arrives
const name = computed(
	() =>
		profile.value?.employee_name || session.employee?.employee_name || session.user?.full_name
);
const picture = computed(
	() => profile.value?.image || session.employee?.image || session.user?.image || ""
);

const rows = computed(() => {
	const p = profile.value || {};
	return [
		[__("Employee ID"), p.name || session.employee?.name],
		[__("Designation"), p.designation || session.employee?.designation],
		[__("Department"), p.department || session.employee?.department],
		[__("Branch"), p.branch],
		[__("Employment type"), p.employment_type],
		[__("Company"), p.company || session.employee?.company],
		[__("Joined"), p.date_of_joining && dayjs(p.date_of_joining).format("DD MMM YYYY")],
		[__("Reports to"), p.reports_to_name || p.reports_to],
		[__("Phone"), p.cell_number],
		[__("Work email"), p.company_email],
		[__("Login"), p.email || session.user?.name],
	].filter(([, value]) => value);
});

onMounted(async () => {
	try {
		profile.value = await getProfile();
	} catch {
		/* the session data above is shown on its own */
	}
});

async function signOut() {
	busy.value = true;
	try {
		await logout();
	} finally {
		busy.value = false;
	}
}
</script>

<template>
	<SlantedPanel>
		<div class="identity">
			<Avatar :src="picture" :name="name" />
			<h1 class="tf-app-title">{{ name }}</h1>
		</div>
		<dl class="profile">
			<template v-for="[term, value] in rows" :key="term">
				<dt class="tf-app-label">{{ term }}</dt>
				<dd>{{ value }}</dd>
			</template>
		</dl>
	</SlantedPanel>
	<div class="actions">
		<BaseButton variant="secondary" to="/settings">{{ __("Settings") }}</BaseButton>
		<BaseButton variant="danger" :loading="busy" @click="signOut">{{
			__("Log out")
		}}</BaseButton>
	</div>
</template>

<style scoped>
.identity {
	display: flex;
	align-items: center;
	gap: var(--tcf-space-md, 1.5rem);
}
.profile {
	display: grid;
	grid-template-columns: max-content 1fr;
	gap: var(--tcf-space-xs, 0.5rem) var(--tcf-space-md, 1.5rem);
	margin: 0;
}
dd {
	margin: 0;
	overflow-wrap: anywhere;
}
.actions {
	display: flex;
	gap: var(--tcf-space-sm, 1rem);
	flex-wrap: wrap;
}

@media (max-width: 767px) {
	.actions {
		padding: var(--tcf-space-sm, 1rem) var(--tcf-space-md, 1.5rem);
	}
	.profile {
		grid-template-columns: 1fr;
		gap: 0;
	}
	dd {
		margin-bottom: var(--tcf-space-xs, 0.5rem);
	}
}
</style>
