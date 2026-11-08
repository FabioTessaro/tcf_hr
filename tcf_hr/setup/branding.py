"""Rebrand the HRMS tile on the apps screen and the app logo on the sidebar rail.

Both read `frappe.boot.app_data`, which frappe builds from HRMS's hooks before `extend_bootinfo`
runs. Patching the boot payload means nothing is written to the database and nothing in HRMS
is touched, so an HRMS update cannot revert the branding.

Config: `config/branding.json`
  target_app  app to rebrand (default "hrms")
  title       display title; empty keeps the app's own
  logo        image URL (e.g. /assets/tcf_hr/images/logo.svg); empty keeps the app's own
"""

from tcf_hr.setup.config import load_config


def extend_bootinfo(bootinfo):
	config = load_config("branding")
	title = config.get("title")
	logo = config.get("logo")
	if not (title or logo):
		return

	target = config.get("target_app") or "hrms"
	for app in bootinfo.get("app_data") or []:
		if app.get("app_name") != target:
			continue
		if title:
			app["app_title"] = title
		if logo:
			app["app_logo_url"] = logo
