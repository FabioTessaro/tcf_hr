from tcf_hr.setup.organization import apply_organization
from tcf_hr.setup.purge import purge_hrms_seeds, purge_org_defaults


def after_install():
	run_setup()


def after_migrate():
	# Also covers sites that already exist: every step is guarded and idempotent.
	run_setup()


def after_setup_wizard(args=None):
	# The wizard has just seeded ERPNext's defaults and created the company.
	run_setup(force=True)


def run_setup(force: bool = False):
	purge_hrms_seeds()
	purge_org_defaults(force=force)
	apply_organization()
