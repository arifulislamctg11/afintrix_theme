app_name = "afintrix_theme"
app_title = "Afintrix Theme"
app_publisher = "Ariful Islam"
app_description = "A Frappe Theme"
app_email = "arifulislamctg11@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "afintrix_theme",
# 		"logo": "/assets/afintrix_theme/logo.png",
# 		"title": "Afintrix Theme",
# 		"route": "/afintrix_theme",
# 		"has_permission": "afintrix_theme.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = [
    "/assets/afintrix_theme/vendor/simplebar/simplebar.css",
    "/assets/afintrix_theme/css/ki_style.css",
    "/assets/afintrix_theme/css/ki_responsive.css",
    # content-hashed by esbuild, so a rebuild always reaches the browser
    "afintrix.bundle.css"
]
app_include_js = [
    "/assets/afintrix_theme/vendor/simplebar/simplebar.js",
    "/assets/afintrix_theme/vendor/animated_icon/iconify-icon.min.js",
    "afintrix.bundle.js"
]

# include js, css files in header of web template (portal/customer pages)
web_include_css = [
    "/assets/afintrix_theme/css/afintrix_portal.css"
]
web_include_js = [
    "/assets/afintrix_theme/vendor/animated_icon/iconify-icon.min.js",
    "/assets/afintrix_theme/js/afintrix_portal.js"
]

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "afintrix_theme/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Workspace" : "public/js/workspace_icon_picker.js"}


# Website route rewrites
website_route_rules = [
    {"from_route": "/dashboard", "to_route": "portal_dashboard"},
]

# Portal menu items
portal_menu_items = [
    {"title": "Dashboard", "route": "/dashboard", "role": "Customer"},
]

# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "afintrix_theme/public/icons.svg"

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

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "afintrix_theme.utils.jinja_methods",
# 	"filters": "afintrix_theme.utils.jinja_filters"
# }

# Installation
# ------------

extend_bootinfo = "afintrix_theme.events.sidebar.boot_session"

# before_install = "afintrix_theme.install.before_install"
after_install = "afintrix_theme.install.after_install"
after_migrate = "afintrix_theme.install.after_migrate"

# Uninstallation
# ------------

# before_uninstall = "afintrix_theme.uninstall.before_uninstall"
# after_uninstall = "afintrix_theme.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "afintrix_theme.utils.before_app_install"
# after_app_install = "afintrix_theme.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "afintrix_theme.utils.before_app_uninstall"
# after_app_uninstall = "afintrix_theme.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "afintrix_theme.notifications.get_notification_config"

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

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
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
# 		"afintrix_theme.tasks.all"
# 	],
# 	"daily": [
# 		"afintrix_theme.tasks.daily"
# 	],
# 	"hourly": [
# 		"afintrix_theme.tasks.hourly"
# 	],
# 	"weekly": [
# 		"afintrix_theme.tasks.weekly"
# 	],
# 	"monthly": [
# 		"afintrix_theme.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "afintrix_theme.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "afintrix_theme.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "afintrix_theme.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["afintrix_theme.utils.before_request"]
# after_request = ["afintrix_theme.utils.after_request"]

# Job Events
# ----------
# before_job = ["afintrix_theme.utils.before_job"]
# after_job = ["afintrix_theme.utils.after_job"]

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
# 	"afintrix_theme.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

