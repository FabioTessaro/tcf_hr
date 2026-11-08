<script setup>
import { computed } from "vue";
import { __ } from "@/api/i18n";
import Icon from "@/components/ui/Icon.vue";
import SlantedPanel from "@/components/ui/SlantedPanel.vue";
import { REQUEST_TYPES } from "@/requests/config";
import { useSession } from "@/stores/session";

const session = useSession();
// Only the request types this user may read (the server decides, see policy.capabilities)
const types = computed(() =>
	REQUEST_TYPES.filter((t) => session.capabilities.requests?.[t.doctype])
);
</script>

<template>
	<SlantedPanel>
		<h1 class="tf-app-title">{{ __("Requests") }}</h1>
		<p v-if="!types.length">{{ __("There are no request types available to you.") }}</p>
		<TransitionGroup tag="ul" name="stagger" class="types">
			<li v-for="(t, i) in types" :key="t.slug" :style="{ '--i': i }">
				<router-link :to="`/requests/${t.slug}`" class="indicator-row tf-app-heading">
					<Icon :name="t.icon" />
					<span>{{ __(t.title) }}</span>
				</router-link>
			</li>
		</TransitionGroup>
	</SlantedPanel>
</template>

<style scoped>
.types {
	list-style: none;
	margin: 0;
	padding: 0;
}
</style>
