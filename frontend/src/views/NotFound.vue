<script setup>
import { __ } from "@/api/i18n";
import SlantedPanel from "@/components/ui/SlantedPanel.vue";
</script>

<template>
	<SlantedPanel>
		<h1 class="tf-app-title">{{ __("Page not found") }}</h1>
		<router-link to="/home">{{ __("Home") }}</router-link>
	</SlantedPanel>
</template>
