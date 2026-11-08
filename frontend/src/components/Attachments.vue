<script setup>
import { onMounted, ref, watch } from "vue";
import { __ } from "@/api/i18n";
import {
	ACCEPTED_FILES,
	MAX_UPLOAD_BYTES,
	deleteAttachment,
	getAttachments,
	uploadFile,
} from "@/api/files";
import BaseButton from "@/components/ui/BaseButton.vue";
import Icon from "@/components/ui/Icon.vue";

// Attachments of a document. On a new document (no `name` yet) files wait in a queue; the form calls
// `flush(name)` after it has saved the document. On an existing one they upload at once.
const props = defineProps({ doctype: String, name: String, editable: Boolean });
const files = ref([]);
const queue = ref([]);
const error = ref("");
const busy = ref(false);
const input = ref(null);

async function load() {
	if (props.name) files.value = await getAttachments(props.doctype, props.name);
}

async function pick(event) {
	error.value = "";
	for (const file of event.target.files) {
		if (file.size > MAX_UPLOAD_BYTES) {
			error.value = __("{0} is larger than 10 MB.", [file.name]);
			continue;
		}
		if (props.name) await send(props.name, file);
		else queue.value.push(file);
	}
	event.target.value = "";
}

async function send(name, file) {
	busy.value = true;
	try {
		files.value.push(await uploadFile(props.doctype, name, file));
	} catch (e) {
		error.value = `${file.name}: ${e.message}`;
	} finally {
		busy.value = false;
	}
}

/** Upload everything that was queued while the document did not exist yet. */
async function flush(name) {
	const pending = queue.value.splice(0);
	for (const file of pending) await send(name, file);
	return !error.value;
}

async function remove(file) {
	try {
		await deleteAttachment(file.name);
		files.value = files.value.filter((f) => f.name !== file.name);
	} catch (e) {
		error.value = e.message;
	}
}

onMounted(load);
watch(() => props.name, load);
defineExpose({ flush });
</script>

<template>
	<div class="attachments">
		<h3 class="tf-app-label">{{ __("Attachments") }}</h3>
		<ul v-if="files.length || queue.length" class="list">
			<li v-for="f in files" :key="f.name">
				<Icon name="attach_file" />
				<a :href="f.file_url" target="_blank" rel="noopener">{{ f.file_name }}</a>
				<button
					v-if="editable"
					type="button"
					class="remove"
					:aria-label="__('Remove')"
					@click="remove(f)"
				>
					<Icon name="close" />
				</button>
			</li>
			<li v-for="(f, i) in queue" :key="`q${i}`" class="queued">
				<Icon name="schedule" />
				<span
					>{{ f.name }} <small>({{ __("uploads when saved") }})</small></span
				>
				<button
					type="button"
					class="remove"
					:aria-label="__('Remove')"
					@click="queue.splice(i, 1)"
				>
					<Icon name="close" />
				</button>
			</li>
		</ul>
		<p v-else class="empty">{{ __("No attachments.") }}</p>
		<template v-if="editable">
			<input
				ref="input"
				type="file"
				multiple
				hidden
				:accept="ACCEPTED_FILES"
				@change="pick"
			/>
			<BaseButton variant="secondary" :loading="busy" @click="input.click()">{{
				__("Add file")
			}}</BaseButton>
		</template>
		<Transition name="fade"
			><p v-if="error" class="error" role="alert">{{ error }}</p></Transition
		>
	</div>
</template>

<style scoped>
.attachments {
	display: grid;
	gap: var(--tcf-space-xs, 0.5rem);
	justify-items: start;
}
h3,
.empty {
	margin: 0;
}
.list {
	list-style: none;
	margin: 0;
	padding: 0;
	display: grid;
	gap: var(--tcf-space-xs, 0.5rem);
	width: 100%;
}
.list li {
	display: flex;
	align-items: center;
	gap: var(--tcf-space-xs, 0.5rem);
	min-height: 44px;
}
.queued {
	opacity: 0.7;
}
.remove {
	margin-left: auto;
	min-width: 44px;
	min-height: 44px;
	border: 0;
	background: none;
	color: inherit;
	cursor: pointer;
}
.error {
	margin: 0;
	color: var(--tcf-accent-red, #ce202a);
}
</style>
