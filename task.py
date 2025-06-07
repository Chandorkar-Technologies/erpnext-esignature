import frappe
from frappe.utils import now_datetime

def send_signature_reminders():
    """Send reminder emails for pending signature requests"""
    try:
        # Get pending signature requests
        pending_requests = frappe.get_all("Signature Request",
            filters={
                "status": ["in", ["Sent", "Viewed"]],
                "expires_on": [">", now_datetime()],
                "reminder_frequency": ["!=", "No Reminders"]
            },
            fields=["name", "recipient_email", "recipient_name", "title", "expires_on"]
        )
        
        for request in pending_requests:
            # Send reminder logic here
            pass
                
    except Exception as e:
        frappe.log_error(f"Sending signature reminders failed: {str(e)}")

def expire_signature_requests():
    """Mark expired signature requests"""
    try:
        expired_requests = frappe.get_all("Signature Request",
            filters={
                "status": ["in", ["Sent", "Viewed"]],
                "expires_on": ["<", now_datetime()]
            }
        )
        
        for request in expired_requests:
            doc = frappe.get_doc("Signature Request", request.name)
            doc.status = "Expired"
            doc.save()
            
    except Exception as e:
        frappe.log_error(f"Expiring signature requests failed: {str(e)}")
