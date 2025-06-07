import frappe
from frappe.model.document import Document
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import pkcs12
import base64
import os

class DigitalCertificate(Document):
    def validate(self):
        if self.certificate_file and self.password:
            self.extract_certificate_info()
    
    def extract_certificate_info(self):
        """Extract certificate information using cryptography library"""
        try:
            file_doc = frappe.get_doc("File", {"file_url": self.certificate_file})
            file_path = file_doc.get_full_path()
            
            with open(file_path, 'rb') as f:
                p12_data = f.read()
            
            # Load PKCS#12 certificate
            (private_key, certificate, additional_certificates) = pkcs12.load_key_and_certificates(
                p12_data, self.password.encode()
            )
            
            # Extract certificate details
            self.subject = certificate.subject.rfc4514_string()
            self.issuer = certificate.issuer.rfc4514_string()
            self.valid_from = certificate.not_valid_before.date()
            self.valid_till = certificate.not_valid_after.date()
            
            # Generate fingerprint
            fingerprint = certificate.fingerprint(hashes.SHA256())
            self.fingerprint = fingerprint.hex().upper()
            
        except Exception as e:
            frappe.throw(f"Error processing certificate: {str(e)}")

# doctype/signature_request/signature_request.py
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
        # Generate document URL and send email
        if self.status == "Draft":
            self.generate_document_url()
            self.send_signature_request_email()
    
    def generate_signature_token(self):
        """Generate secure random token for signature URL"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    def generate_document_url(self):
        """Generate URL for document signing"""
        base_url = get_url()
        self.document_url = f"{base_url}/api/method/esignature.api.external_signing.get_document?token={self.signature_token}"
        self.db_update()
    
    def send_signature_request_email(self):
        """Send signature request email to recipient"""
        try:
            # Create signing URL
            signing_url = f"{get_url()}/api/method/esignature.api.external_signing.sign_document?token={self.signature_token}"
            
            # Prepare email content
            subject = self.email_subject or f"Signature Required: {self.title}"
            message = self.email_message or f"""
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
