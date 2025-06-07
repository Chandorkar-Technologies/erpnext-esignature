from . import __version__ as app_version

app_name = "esignature"
app_title = "E-Signature"
app_publisher = "Your Company"
app_description = "Digital signature solution for ERPNext with pyHanko integration"
app_icon = "octicon octicon-file-text"
app_color = "blue"
app_email = "admin@yourcompany.com"
app_license = "MIT"

# Includes in <head>
# ------------------
# include js, css files in header of desk.html
# app_include_css = "/assets/esignature/css/esignature.css"
# app_include_js = "/assets/esignature/js/esignature.js"

# include js, css files in header of web template
# web_include_css = "/assets/esignature/css/esignature.css"
# web_include_js = "/assets/esignature/js/esignature.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "esignature/public/scss/website"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Quotation": "public/js/quotation.js",
    "Sales Invoice": "public/js/sales_invoice.js",
    "Salary Slip": "public/js/salary_slip.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------
# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------
# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------
after_install = "esignature.install.after_install"

# Uninstallation
# ------------
# before_uninstall = "esignature.uninstall.before_uninstall"
# after_uninstall = "esignature.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "esignature.notifications.get_notification_config"

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

doc_events = {
    "Quotation": {
        "before_submit": "esignature.utils.document_handler.handle_internal_signature",
        "on_submit": "esignature.utils.document_handler.create_signature_request"
    },
    "Sales Invoice": {
        "before_submit": "esignature.utils.document_handler.handle_internal_signature",
        "on_submit": "esignature.utils.document_handler.create_signature_request"
    },
    "Salary Slip": {
        "before_submit": "esignature.utils.document_handler.handle_internal_signature"
    },
    "Purchase Order": {
        "before_submit": "esignature.utils.document_handler.handle_internal_signature"
    }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "hourly": [
        "esignature.tasks.send_signature_reminders"
    ],
    "daily": [
        "esignature.tasks.expire_signature_requests"
    ]
}

# Testing
# -------

# before_tests = "esignature.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "esignature.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "esignature.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Request Events
# ----------------
# before_request = ["esignature.utils.before_request"]
# after_request = ["esignature.utils.after_request"]

# Job Events
# ----------
# before_job = ["esignature.utils.before_job"]
# after_job = ["esignature.utils.after_job"]

# User Data Protection
# --------------------

user_data_fields = [
    {
        "doctype": "Signature Request",
        "filter_by": "recipient_email",
        "redact_fields": ["recipient_name", "recipient_email", "ip_address"],
        "rename": None
    }
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"esignature.auth.validate"
# ]
