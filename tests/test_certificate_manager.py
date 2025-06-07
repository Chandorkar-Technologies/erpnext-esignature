import frappe
import unittest
from esignature.utils.certificate_manager import CertificateManager

class TestCertificateManager(unittest.TestCase):
    def test_certificate_validation(self):
        """Test certificate validation"""
        # Create test certificate record
        cert_doc = frappe.get_doc({
            "doctype": "Digital Certificate",
            "certificate_name": "Test Certificate",
            "certificate_type": "Internal",
            "is_active": 0  # Not active for test
        })
        cert_doc.insert()
        
        # Test validation
        is_valid, message = CertificateManager.validate_certificate(cert_doc.name)
        self.assertFalse(is_valid)
        self.assertIn("Certificate file not found", message)
        
        # Clean up
        frappe.delete_doc("Digital Certificate", cert_doc.name, force=True)
