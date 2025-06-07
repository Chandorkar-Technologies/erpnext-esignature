import frappe
from frappe.utils import now_datetime, get_datetime
import json
from esignature.utils.pdf_handler import PDFSignatureHandler

@frappe.whitelist(allow_guest=True)
def get_document(token):
    """Get document for signing by token"""
    try:
        # Validate token
        signature_request = frappe.get_doc("Signature Request", {"signature_token": token})
        
        if not signature_request:
            return {"error": "Invalid token"}
        
        if signature_request.status in ["Signed", "Expired", "Cancelled"]:
            return {"error": "Signature request is no longer valid"}
        
        if get_datetime(signature_request.expires_on) < now_datetime():
            signature_request.status = "Expired"
            signature_request.save()
            return {"error": "Signature request has expired"}
        
        # Update status to viewed
        if signature_request.status == "Sent":
            signature_request.status = "Viewed"
            signature_request.save()
        
        # Get document PDF
        ref_doc = frappe.get_doc(signature_request.reference_doctype, signature_request.reference_name)
        pdf_content = get_document_pdf(ref_doc)
        
        if not pdf_content:
            return {"error": "Could not generate document"}
        
        # Add signature placeholder
        pdf_handler = PDFSignatureHandler()
        pdf_with_placeholder = pdf_handler.add_signature_placeholder(pdf_content)
        
        # Return document info
        return {
            "success": True,
            "document_title": signature_request.title,
            "recipient_name": signature_request.recipient_name,
            "pdf_data": frappe.utils.get_base64_string(pdf_with_placeholder),
            "expires_on": signature_request.expires_on
        }
        
    except Exception as e:
        frappe.log_error(f"Get document failed: {str(e)}")
        return {"error": "Failed to retrieve document"}

@frappe.whitelist(allow_guest=True)
def sign_document():
    """Handle document signing"""
    try:
        # Get form data
        token = frappe.form_dict.get('token')
        signature_data = frappe.form_dict.get('signature_data')  # Base64 signature image
        ip_address = frappe.local.request_ip
        
        if not token or not signature_data:
            return {"error": "Missing required data"}
        
        # Validate token
        signature_request = frappe.get_doc("Signature Request", {"signature_token": token})
        
        if not signature_request or signature_request.status == "Signed":
            return {"error": "Invalid or already signed request"}
        
        if get_datetime(signature_request.expires_on) < now_datetime():
            return {"error": "Signature request has expired"}
        
        # Apply signature to document
        ref_doc = frappe.get_doc(signature_request.reference_doctype, signature_request.reference_name)
        pdf_content = get_document_pdf(ref_doc)
        
        # Here you would implement the actual signature application
        # For now, we'll simulate by saving the signature data
        signed_pdf_url = save_signed_document(ref_doc, pdf_content, "external")
        
        # Update signature request
        signature_request.status = "Signed"
        signature_request.signed_at = now_datetime()
        signature_request.ip_address = ip_address
        signature_request.signed_document_url = signed_pdf_url
        signature_request.save()
        
        # Send confirmation email
        send_signature_confirmation_email(signature_request)
        
        return {
            "success": True,
            "message": "Document signed successfully"
        }
        
    except Exception as e:
        frappe.log_error(f"Document signing failed: {str(e)}")
        return {"error": "Failed to sign document"}

def send_signature_confirmation_email(signature_request):
    """Send confirmation email after successful signing"""
    try:
        frappe.sendmail(
            recipients=[signature_request.recipient_email],
            subject=f"Document Signed: {signature_request.title}",
            message=f"""
            Dear {signature_request.recipient_name},
            
            Thank you for signing the document: {signature_request.title}
            
            The document has been successfully signed and processed.
            
            Signed on: {signature_request.signed_at}
            
            Best regards
            """,
            reference_doctype=signature_request.doctype,
            reference_name=signature_request.name
        )
    except Exception as e:
        frappe.log_error(f"Failed to send confirmation email: {str(e)}")
