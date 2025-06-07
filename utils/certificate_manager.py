import frappe
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography import x509
import base64

class CertificateManager:
    """Manage digital certificates for signing operations"""
    
    @staticmethod
    def load_certificate(certificate_name):
        """Load certificate from database"""
        cert_doc = frappe.get_doc("Digital Certificate", certificate_name)
        
        if not cert_doc.is_active:
            raise Exception("Certificate is not active")
        
        if not cert_doc.certificate_file:
            raise Exception("Certificate file not found")
        
        # Get file content
        file_doc = frappe.get_doc("File", {"file_url": cert_doc.certificate_file})
        file_path = file_doc.get_full_path()
        
        with open(file_path, 'rb') as f:
            cert_data = f.read()
        
        # Load PKCS#12
        try:
            (private_key, certificate, additional_certificates) = pkcs12.load_key_and_certificates(
                cert_data, cert_doc.password.encode()
            )
            return private_key, certificate, additional_certificates
        except Exception as e:
            raise Exception(f"Failed to load certificate: {str(e)}")
    
    @staticmethod
    def validate_certificate(certificate_name):
        """Validate certificate before use"""
        try:
            private_key, certificate, _ = CertificateManager.load_certificate(certificate_name)
            
            # Check expiry
            from datetime import datetime
            if certificate.not_valid_after < datetime.now():
                return False, "Certificate has expired"
            
            if certificate.not_valid_before > datetime.now():
                return False, "Certificate is not yet valid"
            
            return True, "Certificate is valid"
            
        except Exception as e:
            return False, str(e)
