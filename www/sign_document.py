import frappe
from frappe import _

def get_context(context):
    """Context for signature page"""
    token = frappe.form_dict.get('token')
    
    if not token:
        frappe.throw(_("Invalid signature link"))
    
    # Get signature request
    try:
        signature_request = frappe.get_doc("Signature Request", {"signature_token": token})
        context.signature_request = signature_request
        context.token = token
        
        # Check if already signed or expired
        if signature_request.status == "Signed":
            context.already_signed = True
        elif signature_request.status == "Expired":
            context.expired = True
        else:
            context.can_sign = True
            
    except Exception:
        frappe.throw(_("Invalid signature request"))
    
    return context
