"""HR entry for the website navbar (see tcf_web.entries). Offered to every user with an active Employee."""

from tcf_hr import policy


def hr_entry(user: str) -> list[dict]:
	if not policy.get_employee(user):
		return []
	return [
		{
			"key": "hr",
			"href": "/hrms",
			"label": "account-buttons:entries.hr",  # label lives in tcf_web's account-buttons i18n
			"icon": "badge",
			"boost": False,  # the HR app is its own SPA: full page load
			"order": 20,
		}
	]
