// Translations come from Frappe (boot.__messages, filled from tcf_hr/translations). Untranslated text falls back to English.
export function __(message, args = []) {
	const translated = window.boot?.__messages?.[message] || message;
	return translated.replace(/\{(\d+)\}/g, (_, i) => args[i] ?? "");
}
