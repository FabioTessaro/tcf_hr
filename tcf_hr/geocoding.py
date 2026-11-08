"""Reverse geocoding (coordinates -> text address) through an external service.

Privacy: the lookup runs on the server, so the service sees the coordinates and our server's address, never the
employee's browser, cookies or IP. Results are cached by position rounded to ~10 m.

Any Nominatim-compatible API works (public OpenStreetMap Nominatim, LocationIQ, a self-hosted Nominatim). Configure it
in the site config, no code change needed:

	"tcf_hr_geocoder": {
		"url": "https://eu1.locationiq.com/v1/reverse",   # default: https://nominatim.openstreetmap.org/reverse
		"api_key": "...",                                  # optional
		"key_param": "key",                                # query parameter carrying the key (default "key")
		"contact": "it@example.com"                        # identifies us to the service (default: app email)
	}

The public Nominatim instance allows light use only (max 1 request/second, identifying User-Agent, caching):
fine for check-in history of a company, not for bulk use. Switch to a paid or self-hosted instance if that changes.
"""

import frappe
import requests

DEFAULT_URL = "https://nominatim.openstreetmap.org/reverse"
FOUND_TTL = 30 * 24 * 60 * 60  # an address for a position does not change often
MISSED_TTL = 10 * 60  # retry sooner after a failure or an empty answer
TIMEOUT = (3, 5)  # connect, read (seconds): a slow service must not stall the app

_STREET_KEYS = ("road", "pedestrian", "footway", "path", "square")
_PLACE_KEYS = ("city", "town", "village", "municipality", "hamlet", "suburb")


def format_address(payload: dict | None) -> str | None:
	"""Short address from a Nominatim-style answer: "Via Roma 12, 20121 Milano, Italia". Falls back to display_name."""
	if not isinstance(payload, dict):
		return None
	parts = payload.get("address")
	if isinstance(parts, dict):
		street = next((parts[k] for k in _STREET_KEYS if parts.get(k)), None)
		if street and parts.get("house_number"):
			street = f"{street} {parts['house_number']}"
		place = next((parts[k] for k in _PLACE_KEYS if parts.get(k)), None)
		locality = " ".join(p for p in (parts.get("postcode"), place) if p)
		pieces = [p for p in (street, locality, parts.get("country")) if p]
		if pieces:
			return ", ".join(pieces)
	name = payload.get("display_name")
	return name if isinstance(name, str) and name else None


def cache_key(latitude: float, longitude: float, lang: str) -> str:
	return f"tcf_hr:address:{latitude:.4f}:{longitude:.4f}:{lang}"


def _settings() -> dict:
	conf = frappe.conf.get("tcf_hr_geocoder") or {}
	return {
		"url": conf.get("url") or DEFAULT_URL,
		"api_key": conf.get("api_key"),
		"key_param": conf.get("key_param") or "key",
		"contact": conf.get("contact") or "info@tcf-group.com",
	}


def reverse_geocode(latitude: float, longitude: float, lang: str = "en") -> str | None:
	"""Address text for a position, or None. Never raises: the check-in history must work without it."""
	key = cache_key(latitude, longitude, lang)
	cached = frappe.cache.get_value(key, expires=True)
	if cached is not None:
		return cached or None

	conf = _settings()
	params = {
		"format": "jsonv2",
		"lat": latitude,
		"lon": longitude,
		"zoom": 18,
		"addressdetails": 1,
		"accept-language": lang,
	}
	if conf["api_key"]:
		params[conf["key_param"]] = conf["api_key"]

	address = None
	try:
		response = requests.get(
			conf["url"],
			params=params,
			headers={"User-Agent": f"TCF-HR/1.0 ({conf['contact']})"},
			timeout=TIMEOUT,
		)
		response.raise_for_status()
		address = format_address(response.json())
	except (requests.RequestException, ValueError):
		frappe.log_error(title="tcf_hr reverse geocoding failed")

	frappe.cache.set_value(key, address or "", expires_in_sec=FOUND_TTL if address else MISSED_TTL)
	return address
