// One socket.io connection, shared. The app only listens on its own per-user room (joined automatically by the
// server); it never subscribes to doctype or document rooms.
import { io } from "socket.io-client";

let socket = null;

function connect() {
	if (socket) return socket;
	const boot = window.boot || {};
	const { protocol, hostname, port } = window.location;
	// Dev servers talk to the socketio port directly; behind nginx the same origin is used (as hrms does)
	const origin = port
		? `http://${hostname}:${boot.socketio_port || 9000}`
		: `${protocol}//${hostname}`;
	socket = io(`${origin}/${boot.site_name}`, { withCredentials: true, reconnectionAttempts: 5 });
	return socket;
}

/** Listen to a server-published event. Returns an unsubscribe function. */
export function onRealtime(event, callback) {
	const s = connect();
	s.on(event, callback);
	return () => s.off(event, callback);
}
