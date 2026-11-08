// Minimal Frappe API client: same-origin, session cookie, CSRF header.

function csrfToken() {
	const meta = document.querySelector('meta[name="csrf-token"]')?.content;
	return window.csrf_token || (meta && !meta.includes("{{") ? meta : "");
}

export class ApiError extends Error {
	constructor(message, status, data) {
		super(message);
		this.status = status;
		this.data = data;
	}
}

function errorMessage(data, fallback) {
	try {
		const messages = JSON.parse(data._server_messages || "[]").map(
			(m) => JSON.parse(m).message
		);
		if (messages.length) return messages.join("\n");
	} catch {
		/* fall through */
	}
	return data.exc_type || data.message || fallback;
}

/** POST a multipart form (file upload) to a whitelisted method. */
export async function upload(method, formData) {
	const response = await fetch(`/api/method/${method}`, {
		method: "POST",
		headers: { Accept: "application/json", "X-Frappe-CSRF-Token": csrfToken() },
		credentials: "same-origin",
		body: formData,
	});
	const data = await response.json().catch(() => ({}));
	if (!response.ok)
		throw new ApiError(errorMessage(data, response.statusText), response.status, data);
	return data.message;
}

export async function call(method, args = {}, { post = true } = {}) {
	const url = `/api/method/${method}`;
	const headers = { Accept: "application/json", "X-Frappe-CSRF-Token": csrfToken() };
	let response;
	if (post) {
		headers["Content-Type"] = "application/json";
		response = await fetch(url, {
			method: "POST",
			headers,
			credentials: "same-origin",
			body: JSON.stringify(args),
		});
	} else {
		const query = new URLSearchParams(
			Object.entries(args)
				.filter(([, v]) => v !== undefined && v !== null) // never send the text "undefined"
				.map(([k, v]) => [k, typeof v === "object" ? JSON.stringify(v) : v])
		);
		response = await fetch(`${url}?${query}`, { headers, credentials: "same-origin" });
	}

	const data = await response.json().catch(() => ({}));
	if (
		response.status === 401 ||
		(response.status === 403 && data.exc_type === "AuthenticationError")
	) {
		window.location.assign(`/login?redirect-to=${encodeURIComponent(location.pathname)}`);
	}
	if (!response.ok)
		throw new ApiError(errorMessage(data, response.statusText), response.status, data);
	return data.message;
}
