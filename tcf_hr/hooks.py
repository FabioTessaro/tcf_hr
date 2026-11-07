app_name = "tcf_hr"
app_title = "TCF HR"
app_publisher = "TCF Group"
app_description = "System layer for Human Resources Management"
app_email = "info@tcf-group.com"
app_license = "agpl-3.0"

# Apps
# ------------------

required_apps = ["tcf_core", "hrms"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "tcf_hr",
# 		"logo": "/assets/tcf_hr/icons/palette-1/app-hr.png",
# 		"title": "HR",
# 		"route": "/tcf_hr_admin"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/tcf_hr/css/tcf_hr.css"
# app_include_js = "/assets/tcf_hr/js/tcf_hr.js"

# include js, css files in header of web template
# web_include_css = "/assets/tcf_hr/css/tcf_hr.css"
# web_include_js = "/assets/tcf_hr/js/tcf_hr.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "tcf_hr/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "tcf_hr/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "tcf_hr.utils.jinja_methods",
# 	"filters": "tcf_hr.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "tcf_hr.install.before_install"
# after_install = "tcf_hr.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "tcf_hr.uninstall.before_uninstall"
# after_uninstall = "tcf_hr.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "tcf_hr.utils.before_app_install"
# after_app_install = "tcf_hr.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "tcf_hr.utils.before_app_uninstall"
# after_app_uninstall = "tcf_hr.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "tcf_hr.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "tcf_hr.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"tcf_hr.tasks.all"
# 	],
# 	"daily": [
# 		"tcf_hr.tasks.daily"
# 	],
# 	"hourly": [
# 		"tcf_hr.tasks.hourly"
# 	],
# 	"weekly": [
# 		"tcf_hr.tasks.weekly"
# 	],
# 	"monthly": [
# 		"tcf_hr.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "tcf_hr.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "tcf_hr.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "tcf_hr.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "tcf_hr.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["tcf_hr.utils.before_request"]
# after_request = ["tcf_hr.utils.after_request"]

# Job Events
# ----------
# before_job = ["tcf_hr.utils.before_job"]
# after_job = ["tcf_hr.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"tcf_hr.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []
