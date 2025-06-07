import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, add_days, get_url
import secrets
import string

class SignatureRequest(Document):
    def before_insert(self):
        # Generate unique signature token
        self.signature_token = self.generate_signature_token()
        
        # Set default expiry (7 days from now)
        if not self.expires_on:
            self.expires_on = add_days(now_datetime(), 7)
    
    def after_insert(self):
        # Send email if status is Draft
        if self.status == "Draft":
            self.send_signature_request_email()
    
    def generate_signature_token(self):
        """Generate secure random token for signature URL"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    def send_signature_request_email(self):
        """Send signature request email to recipient"""
        try:
            # Create signing URL (placeholder - implement web page later)
            signing_url = f"{get_url()}/sign_document?token={self.signature_token}"
            
            # Prepare email content
            subject = f"Signature Required: {self.title}"
            message = f"""
            Dear {self.recipient_name},
            
            You have been requested to sign the document: {self.title}
            
            Please click the link below to review and sign the document:
            {signing_url}
            
            This request will expire on {self.expires_on}
            
            Thank you.
            """
            
            # Send email
            frappe.sendmail(
                recipients=[self.recipient_email],
                subject=subject,
                message=message,
                reference_doctype=self.doctype,
                reference_name=self.name
            )
            
            # Update status
            self.status = "Sent"
            self.db_update()
            
        except Exception as e:
            frappe.log_error(f"Failed to send signature request email: {str(e)}")
