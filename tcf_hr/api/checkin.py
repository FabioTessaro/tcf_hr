"""Employee check-in / check-out from the HR app."""

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import now_datetime

from tcf_hr import geocoding, policy

HISTORY_FIELDS = ["name", "log_type", "time", "latitude", "longitude"]


def next_action(last_log_type: str | None) -> str:
	"""A check-in follows a check-out (or nothing); a check-out follows a check-in."""
	return "OUT" if last_log_type == "IN" else "IN"


def clean_coordinates(latitude, longitude) -> tuple[float, float] | None:
	"""Valid coordinates rounded to ~10 cm, or None. (0, 0) means "no position" and is dropped."""
	try:
		lat, lon = float(latitude), float(longitude)
	except (TypeError, ValueError):
		return None
	if not (-90 <= lat <= 90 and -180 <= lon <= 180) or (lat == 0 and lon == 0):
		return None
	return round(lat, 6), round(lon, 6)


def _require_employee() -> str:
	employee = policy.get_employee()
	if not employee:
		frappe.throw(_("No active employee is linked to your account."), frappe.PermissionError)
	return employee


def _history(employee: str, limit: int = 20) -> list[dict]:
	return frappe.get_list(
		"Employee Checkin",
		filters={"employee": employee},
		fields=HISTORY_FIELDS,
		order_by="time desc",
		limit_page_length=limit,
	)


def _status(employee: str) -> dict:
	history = _history(employee)
	last = history[0] if history else None
	return {
		"last": last,
		"history": history,
		"next_action": next_action(last["log_type"] if last else None),
		"capabilities": policy.capabilities(employee),
	}


@frappe.whitelist(methods=["GET"])
def get_status() -> dict:
	return _status(_require_employee())


@frappe.whitelist(methods=["POST"])
def submit_checkin(log_type: str, latitude=None, longitude=None) -> dict:
	employee = _require_employee()
	if log_type not in ("IN", "OUT"):
		frappe.throw(_("Invalid log type"), frappe.ValidationError)
	if not policy.capabilities(employee)["check_in"]:
		frappe.throw(_("You are not allowed to check in from the app."), frappe.PermissionError)

	doc = frappe.new_doc("Employee Checkin")
	doc.employee = employee
	doc.log_type = log_type
	doc.time = now_datetime()  # server time: the device clock is not trusted

	if policy.capabilities(employee)["geolocation"]:
		coordinates = clean_coordinates(latitude, longitude)
		if coordinates:
			doc.latitude, doc.longitude = coordinates

	doc.insert()  # permission-checked; policy.validate_employee_checkin runs as a hook too
	return _status(employee)


@frappe.whitelist(methods=["GET"])
@rate_limit(limit=60, seconds=60, ip_based=False, user_based=True)
def get_address(name: str) -> str | None:
	"""Text address of one of the user's own check-ins.

	Takes a record name, not coordinates, so the endpoint cannot be used as a general geocoding proxy.
	"""
	employee = _require_employee()
	doc = frappe.get_doc("Employee Checkin", name)
	doc.check_permission("read")
	if doc.employee != employee:
		frappe.throw(_("Not permitted"), frappe.PermissionError)
	position = clean_coordinates(doc.latitude, doc.longitude)
	if not position:
		return None
	return geocoding.reverse_geocode(*position, lang=str(frappe.local.lang or "en")[:2])
