<script setup>
import dayjs from "dayjs";
import { onMounted } from "vue";
import { __ } from "@/api/i18n";
import BaseButton from "@/components/ui/BaseButton.vue";
import Skeleton from "@/components/ui/Skeleton.vue";
import Indicator from "@/components/ui/Indicator.vue";
import SlantedPanel from "@/components/ui/SlantedPanel.vue";
import { useNotifications } from "@/stores/notifications";

const notifications = useNotifications();
onMounted(() => notifications.load());
</script>

<template>
	<SlantedPanel>
		<div class="head">
			<h1 class="tf-app-title">{{ __("Notifications") }}</h1>
			<BaseButton
				v-if="notifications.unread"
				variant="secondary"
				@click="notifications.readAll()"
			>
				{{ __("Mark all as read") }}
			</BaseButton>
		</div>
		<p v-if="notifications.loaded && !notifications.items.length">
			{{ __("No notifications.") }}
		</p>
		<Skeleton v-if="!notifications.loaded" />
		<TransitionGroup tag="ul" name="stagger" class="list">
			<li v-for="(item, i) in notifications.items" :key="item.name" :style="{ '--i': i }">
				<button
					class="item"
					type="button"
					@click="!item.read && notifications.read([item.name])"
				>
					<Indicator :tone="item.read ? 'muted' : 'accent'" />
					<span class="text">
						<!-- Parts are plain text spans: server-provided messages are never rendered as HTML -->
						<span
							v-for="(part, i) in item.message"
							:key="i"
							:class="{ bold: part.bold }"
							>{{ part.text }}</span
						>
						<small class="tf-app-caption">{{
							dayjs(item.creation).format("DD MMM YYYY, HH:mm")
						}}</small>
					</span>
					<span v-if="!item.read" class="visually-hidden">{{ __("Unread") }}</span>
				</button>
			</li>
		</TransitionGroup>
	</SlantedPanel>
</template>

<style scoped>
.head {
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: var(--tcf-space-sm, 1rem);
	flex-wrap: wrap;
}
.list {
	list-style: none;
	margin: 0;
	padding: 0;
}
.item {
	display: flex;
	gap: var(--tcf-space-sm, 1rem);
	align-items: flex-start;
	width: 100%;
	padding: var(--tcf-space-sm, 1rem) 0;
	border: 0;
	background: none;
	color: inherit;
	font: inherit;
	text-align: left;
	cursor: pointer;
}
.text {
	display: grid;
}
.bold {
	font-weight: 600;
}
small {
	opacity: 0.7;
}
.visually-hidden {
	position: absolute;
	width: 1px;
	height: 1px;
	overflow: hidden;
	clip: rect(0 0 0 0);
}
</style>
