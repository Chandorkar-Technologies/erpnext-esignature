import frappe
from frappe.utils import now_datetime, add_days

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
            fields=["name", "recipient_email", "recipient_name", "title", "expires_on", "reminder_frequency"]
        )
        
        for request in pending_requests:
            if should_send_reminder(request):
                send_reminder_email(request)
                
    except Exception as e:
        frappe.log_error(f"Sending signature reminders failed: {str(e)}")

def should_send_reminder(request):
    """Check if reminder should be sent based on frequency"""
    # Implementation would check last reminder sent date
    # and frequency settings
    return True  # Simplified for example

def send_reminder_email(request):
    """Send reminder email"""
    try:
        signing_url = f"{frappe.utils.get_url()}/api/method/esignature.api.external_signing.sign_document?token={request.get('signature_token', '')}"
        
        frappe.sendmail(
            recipients=[request['recipient_email']],
            subject=f"Reminder: Signature Required - {request['title']}",
            message=f"""
            Dear {request['recipient_name']},
            
            This is a reminder that you have a pending document to sign: {request['title']}
            
            Please click the link below to review and sign:
            {signing_url}
            
            This request expires on: {request['expires_on']}
            
            Thank you.
            """
        )
    except Exception as e:
        frappe.log_error(f"Failed to send reminder email: {str(e)}")

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
