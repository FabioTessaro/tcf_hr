import json
import os
from functools import lru_cache

import frappe


@lru_cache(maxsize=8)
def _read(path: str, mtime: float) -> dict:
	with open(path) as f:
		return json.load(f)


def load_config(name: str) -> dict:
	"""Load `tcf_hr/config/<name>.json`. A missing file means "no config" and returns {}."""
	path = frappe.get_app_path("tcf_hr", "config", f"{name}.json")
	if not os.path.exists(path):
		return {}
	return _read(path, os.path.getmtime(path))
