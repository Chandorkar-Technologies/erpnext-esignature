import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
    """Setup after app installation"""
    print("Setting up E-Signature App...")
    
    # Create custom fields
    create_custom_fields_for_signature()
    
    # Create default certificates
    create_default_certificates()
    
    # Setup email templates
    setup_email_templates()
    
    # Create workspace
    setup_workspace()
    
    print("E-Signature App setup completed successfully!")

def create_custom_fields_for_signature():
    """Add signature-related custom fields to standard doctypes"""
    custom_fields = {
        "Quotation": [
            {
                "fieldname": "requires_signature",
                "label": "Requires Customer Signature",
                "fieldtype": "Check",
                "default": 1,
                "insert_after": "valid_till"
            },
            {
                "fieldname": "signature_status",
                "label": "Signature Status",
                "fieldtype": "Select",
                "options": "Not Required\nPending\nSigned",
                "default": "Not Required",
                "read_only": 1,
                "insert_after": "requires_signature"
            },
            {
                "fieldname": "signed_document",
                "label": "Signed Document",
                "fieldtype": "Attach",
                "read_only": 1,
                "insert_after": "signature_status"
            }
        ],
        "Sales Invoice": [
            {
                "fieldname": "requires_signature",
                "label": "Requires Customer Signature", 
                "fieldtype": "Check",
                "default": 0,
                "insert_after": "due_date"
            },
            {
                "fieldname": "signature_status",
                "label": "Signature Status",
                "fieldtype": "Select",
                "options": "Not Required\nPending\nSigned",
                "default": "Not Required",
                "read_only": 1,
                "insert_after": "requires_signature"
            }
        ],
        "Salary Slip": [
            {
                "fieldname": "employee_signature_required",
                "label": "Employee Signature Required",
                "fieldtype": "Check",
                "default": 1,
                "insert_after": "letter_head"
            },
            {
                "fieldname": "hr_signed",
                "label": "HR Signed",
                "fieldtype": "Check",
                "default": 0,
                "read_only": 1,
                "insert_after": "employee_signature_required"
            }
        ]
    }
    
    create_custom_fields(custom_fields)

def create_default_certificates():
    """Create default certificate records"""
    default_certs = [
        {
            "certificate_name": "Sales Certificate",
            "certificate_type": "Internal",
            "is_active": 0
        },
        {
            "certificate_name": "HR Certificate",
            "certificate_type": "Internal", 
            "is_active": 0
        },
        {
            "certificate_name": "Purchase Certificate",
            "certificate_type": "Internal",
            "is_active": 0
        }
    ]
    
    for cert_data in default_certs:
        if not frappe.db.exists("Digital Certificate", cert_data["certificate_name"]):
            cert_doc = frappe.get_doc({
                "doctype": "Digital Certificate",
                **cert_data
            })
            cert_doc.insert()

def setup_email_templates():
    """Create email templates for signature requests"""
    templates = [
        {
            "name": "Signature Request - Customer",
            "subject": "Signature Required: {{ title }}",
            "response": """
Dear {{ recipient_name }},

You have been requested to sign the document: {{ title }}

Please click the link below to review and sign the document:
{{ signing_url }}

This request will expire on {{ expires_on }}

If you have any questions, please contact us.

Thank you for your cooperation.

Best regards,
{{ company_name }}
            """
        },
        {
            "name": "Signature Confirmation", 
            "subject": "Document Signed: {{ title }}",
            "response": """
Dear {{ recipient_name }},

Thank you for signing the document: {{ title }}

The document has been successfully signed and processed.

Signed on: {{ signed_at }}

Best regards,
{{ company_name }}
            """
        }
    ]
    
    for template in templates:
        if not frappe.db.exists("Email Template", template["name"]):
            frappe.get_doc({
                "doctype": "Email Template",
                **template
            }).insert()

def setup_workspace():
    """Setup E-Signature workspace"""
    if not frappe.db.exists("Workspace", "E-Signature"):
        workspace_doc = frappe.get_doc({
            "doctype": "Workspace",
            "name": "E-Signature",
            "label": "E-Signature",
            "icon": "signature",
            "module": "E-Signature",
            "is_standard": 1,
            "public": 1
        })
        workspace_doc.insert()
