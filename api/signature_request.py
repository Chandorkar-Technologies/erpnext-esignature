import frappe
from frappe.utils import now_datetime, add_days
from esignature.utils.document_handler import get_document_pdf, save_signed_document

@frappe.whitelist()
def send_request(signature_request):
    """Send signature request manually"""
    try:
        doc = frappe.get_doc("Signature Request", signature_request)
        
        if doc.status != "Draft":
            return {"error": "Request is not in draft status"}
        
        doc.send_signature_request_email()
        return {"success": True}
        
    except Exception as e:
        frappe.log_error(f"Manual send request failed: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist()
def send_reminder(signature_request):
    """Send reminder email for pending signature"""
    try:
        doc = frappe.get_doc("Signature Request", signature_request)
        
        if doc.status not in ["Sent", "Viewed"]:
            return {"error": "Cannot send reminder for this status"}
        
        # Check if not expired
        if get_datetime(doc.expires_on) < now_datetime():
            return {"error": "Request has expired"}
        
        # Send reminder email
        signing_url = f"{frappe.utils.get_url()}/sign_document?token={doc.signature_token}"
        
        frappe.sendmail(
            recipients=[doc.recipient_email],
            subject=f"Reminder: {doc.title}",
            message=f"""
            Dear {doc.recipient_name},
            
            This is a reminder that you have a pending document to sign: {doc.title}
            
            Please click the link below to review and sign:
            {signing_url}
            
            This request expires on: {doc.expires_on}
            
            Thank you.
            """,
            reference_doctype=doc.doctype,
            reference_name=doc.name
        )
        
        return {"success": True}
        
    except Exception as e:
        frappe.log_error(f"Send reminder failed: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist()
def cancel_request(signature_request):
    """Cancel signature request"""
    try:
        doc = frappe.get_doc("Signature Request", signature_request)
        
        if doc.status in ["Signed", "Cancelled"]:
            return {"error": "Cannot cancel this request"}
        
        doc.status = "Cancelled"
        doc.save()
        
        # Send cancellation email
        frappe.sendmail(
            recipients=[doc.recipient_email],
            subject=f"Cancelled: {doc.title}",
            message=f"""
            Dear {doc.recipient_name},
            
            The signature request for "{doc.title}" has been cancelled.
            
            No further action is required from your side.
            
            Thank you.
            """,
            reference_doctype=doc.doctype,
            reference_name=doc.name
        )
        
        return {"success": True}
        
    except Exception as e:
        frappe.log_error(f"Cancel request failed: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist()
def resend_request(signature_request):
    """Resend expired signature request"""
    try:
        doc = frappe.get_doc("Signature Request", signature_request)
        
        if doc.status != "Expired":
            return {"error": "Can only resend expired requests"}
        
        # Reset status and extend expiry
        doc.status = "Draft"
        doc.expires_on = add_days(now_datetime(), 7)
        doc.save()
        
        # Send new request
        doc.send_signature_request_email()
        
        return {"success": True}
        
    except Exception as e:
        frappe.log_error(f"Resend request failed: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist()
def get_signature_status(reference_doctype, reference_name):
    """Get signature status for a document"""
    try:
        signature_requests = frappe.get_all("Signature Request",
            filters={
                "reference_doctype": reference_doctype,
                "reference_name": reference_name
            },
            fields=["name", "status", "signed_at", "recipient_name"],
            order_by="creation desc"
        )
        
        return {"requests": signature_requests}
        
    except Exception as e:
        frappe.log_error(f"Get signature status failed: {str(e)}")
        return {"error": str(e)}
