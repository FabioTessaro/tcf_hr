def patch_app_title(bootinfo):
	new_title = "TCF HR"

	for entry in bootinfo.get("app_data") or []:
		if entry.get("app_name") == "hrms":
			entry["app_title"] = new_title
