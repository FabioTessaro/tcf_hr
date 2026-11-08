<script setup>
import { __ } from "@/api/i18n";
import BaseButton from "@/components/ui/BaseButton.vue";
import SlantedPanel from "@/components/ui/SlantedPanel.vue";
import { useSession } from "@/stores/session";

const session = useSession();
</script>

<template>
	<SlantedPanel>
		<h1 class="tf-app-title">{{ __("Settings") }}</h1>
		<p>{{ __("Language") }}: {{ session.lang }}</p>
		<!-- The password page is served by the website (tcf_web): a normal page load, not a route of this app -->
		<BaseButton variant="secondary" href="/update-password">{{
			__("Change password")
		}}</BaseButton>
	</SlantedPanel>
</template>
