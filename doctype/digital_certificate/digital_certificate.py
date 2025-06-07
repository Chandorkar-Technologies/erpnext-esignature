import frappe
from frappe.model.document import Document

class DigitalCertificate(Document):
    def validate(self):
        if self.certificate_file and self.password:
            try:
                self.extract_certificate_info()
            except Exception as e:
                frappe.msgprint(f"Warning: Could not extract certificate info: {str(e)}")
    
    def extract_certificate_info(self):
        """Extract certificate information using cryptography library"""
        try:
            # Try to import and use cryptography if available
            from cryptography.hazmat.primitives.serialization import pkcs12
            from cryptography.hazmat.primitives import hashes
            
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
            
        except ImportError:
            frappe.msgprint("Cryptography library not installed. Please install it to use certificate extraction.")
        except Exception as e:
            frappe.throw(f"Error processing certificate: {str(e)}")
