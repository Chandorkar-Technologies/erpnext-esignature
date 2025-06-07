import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
    """Setup custom fields and default data after app installation"""
    create_custom_fields_for_signature()
    create_default_certificates()
    setup_email_templates()
    create_signature_workflow()

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
            "is_active": 0  # User needs to upload actual certificate
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
            "subject": "Signature Required: {title}",
            "response": """
Dear {recipient_name},

You have been requested to sign the document: {title}

Please click the link below to review and sign the document:
{signing_url}

This request will expire on {expires_on}

If you have any questions, please contact us.

Thank you for your cooperation.

Best regards,
{company_name}
            """
        },
        {
            "name": "Signature Confirmation",
            "subject": "Document Signed: {title}",
            "response": """
Dear {recipient_name},

Thank you for signing the document: {title}

The document has been successfully signed and processed.

Signed on: {signed_at}
IP Address: {ip_address}

A copy of the signed document is attached for your records.

Best regards,
{company_name}
            """
        }
    ]
    
    for template in templates:
        if not frappe.db.exists("Email Template", template["name"]):
            frappe.get_doc({
                "doctype": "Email Template",
                **template
            }).insert()

def create_signature_workflow():
    """Create workflow for signature approval process"""
    if frappe.db.exists("Workflow", "Signature Request Workflow"):
        return
        
    # Create workflow states
    states = [
        {"state": "Draft", "doc_status": "0", "allow_edit": "All"},
        {"state": "Sent", "doc_status": "0", "allow_edit": "System Manager"},
        {"state": "Viewed", "doc_status": "0", "allow_edit": "System Manager"},
        {"state": "Signed", "doc_status": "1", "allow_edit": "System Manager"},
        {"state": "Expired", "doc_status": "2", "allow_edit": "System Manager"},
        {"state": "Cancelled", "doc_status": "2", "allow_edit": "System Manager"}
    ]
    
    # Create workflow actions
    actions = [
        {"action": "Send", "allowed": "System Manager", "condition": "doc.status == 'Draft'"},
        {"action": "Cancel", "allowed": "System Manager", "condition": "doc.status in ['Draft', 'Sent', 'Viewed']"},
        {"action": "Resend", "allowed": "System Manager", "condition": "doc.status == 'Expired'"}
    ]
    
    workflow = frappe.get_doc({
        "doctype": "Workflow",
        "workflow_name": "Signature Request Workflow",
        "document_type": "Signature Request",
        "workflow_state_field": "status",
        "is_active": 1,
        "states": [{"state": state["state"], "doc_status": state["doc_status"], "allow_edit": state["allow_edit"]} for state in states],
        "transitions": [
            {"state": "Draft", "action": "Send", "next_state": "Sent", "allowed": "System Manager"},
            {"state": "Draft", "action": "Cancel", "next_state": "Cancelled", "allowed": "System Manager"},
            {"state": "Sent", "action": "Cancel", "next_state": "Cancelled", "allowed": "System Manager"},
            {"state": "Expired", "action": "Resend", "next_state": "Draft", "allowed": "System Manager"}
        ]
    })
    workflow.insert()
