import json
from urllib.parse import quote

import frappe
from frappe.boot import load_translations
from frappe.utils.jinja_globals import is_rtl

# Served for every /hrms/<path> (hrms' own route rule maps them to the page named "hrms"; this app is
# installed after hrms, so this page replaces hrms' shell). The built index.html is copied here by
# `yarn build`; it is not committed.
no_cache = 1

LOGIN_ROUTE = "/login"


def get_context(context):
	if frappe.session.user == "Guest":
		path = frappe.local.request.path if getattr(frappe.local, "request", None) else "/hrms"
		if not path.startswith("/hrms"):
			path = "/hrms"
		frappe.flags.redirect_location = f"{LOGIN_ROUTE}?redirect-to={quote(path)}"
		raise frappe.Redirect

	context = frappe._dict()
	context.csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()  # nosempgrep
	context.boot = get_boot()
	return context


def get_boot() -> dict:
	boot = frappe._dict(
		{
			"site_name": frappe.local.site,
			"socketio_port": frappe.conf.get("socketio_port") or 9000,
			"default_route": "/hrms",
		}
	)
	boot.lang = frappe.local.lang
	boot.layout_direction = "rtl" if is_rtl() else "ltr"
	load_translations(boot)
	# frappe.local values (lang, site) are proxy objects that plain `json` cannot serialize, and the template
	# uses Jinja's `tojson` (script-safe escaping). Round-trip through Frappe's own handler to get plain types.
	return json.loads(frappe.as_json(boot))
