<script setup>
import { __ } from "@/api/i18n";
import CheckInPanel from "@/components/CheckInPanel.vue";
import HrTiles from "@/components/HrTiles.vue";
import SlantedPanel from "@/components/ui/SlantedPanel.vue";
import { useSession } from "@/stores/session";

const session = useSession();
</script>

<template>
	<SlantedPanel>
		<h1 class="tf-app-title">
			{{ __("Hello, {0}", [session.employee?.first_name || session.user?.full_name]) }}
		</h1>
		<p v-if="!session.employee">
			{{ __("No active employee record is linked to this account.") }}
		</p>
	</SlantedPanel>
	<CheckInPanel v-if="session.employee" />
	<HrTiles v-if="session.employee" />
</template>
