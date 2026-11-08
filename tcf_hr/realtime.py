"""Events published to the per-user realtime room, so the HR app never subscribes to doctype rooms.

The browser listens on its own `user:<email>` room (joined automatically) for these events and refetches.
"""

import frappe


def _publish(event: str, user: str | None, message: dict):
	if user:
		frappe.publish_realtime(event, message, user=user, after_commit=True)


def notification_created(doc, method=None):
	_publish("tcf_hr:notification", doc.to_user, {"name": doc.name})


def checkin_created(doc, method=None):
	user = frappe.db.get_value("Employee", doc.employee, "user_id")
	_publish("tcf_hr:checkin", user, {"name": doc.name})
