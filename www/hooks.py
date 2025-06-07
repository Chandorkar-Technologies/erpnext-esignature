from . import __version__ as app_version

app_name = "esignature"
app_title = "E-Signature"
app_publisher = "Your Company"
app_description = "Digital signature solution for ERPNext with pyHanko integration"
app_icon = "octicon octicon-file-text"
app_color = "blue"
app_email = "admin@yourcompany.com"
app_license = "MIT"
required_apps = ["frappe", "erpnext"]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/esignature/css/esignature.css"
# app_include_js = "/assets/esignature/js/esignature.js"

# include js, css files in header of web template
# web_include_css = "/assets/esignature/css/esignature.css"
# web_include_js = "/assets/esignature/js/esignature.js"

# include js in doctype views
doctype_js = {
    "Quotation": "public/js/quotation.js",
    "Sales Invoice": "public/js/sales_invoice.js",
    "Salary Slip": "public/js/salary_slip.js"
}

# Installation
# ------------
after_install = "esignature.install.after_install"

# Document Events
# ---------------
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

# esignature/modules.txt
E-Signature

# esignature/patches.txt
esignature.patches.v1_0.create_default_certificates
esignature.patches.v1_0.setup_custom_fields
