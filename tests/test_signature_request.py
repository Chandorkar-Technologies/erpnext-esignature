import frappe
import unittest
from frappe.utils import now_datetime, add_days
from esignature.utils.document_handler import create_signature_request

class TestSignatureRequest(unittest.TestCase):
    def setUp(self):
        """Set up test data"""
        self.test_customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": "Test Customer",
            "customer_type": "Individual"
        }).insert()
        
        self.test_quotation = frappe.get_doc({
            "doctype": "Quotation",
            "customer": self.test_customer.name,
            "customer_name": self.test_customer.customer_name,
            "transaction_date": now_datetime().date(),
            "valid_till": add_days(now_datetime().date(), 30),
            "items": [{
                "item_code": "Test Item",
                "qty": 1,
                "rate": 100
            }]
        }).insert()
    
    def tearDown(self):
        """Clean up test data"""
        frappe.delete_doc("Quotation", self.test_quotation.name, force=True)
        frappe.delete_doc("Customer", self.test_customer.name, force=True)
    
    def test_signature_request_creation(self):
        """Test signature request creation"""
        signature_request = frappe.get_doc({
            "doctype": "Signature Request",
            "title": "Test Signature Request",
            "reference_doctype": "Quotation",
            "reference_name": self.test_quotation.name,
            "request_type": "External Customer",
            "recipient_email": "test@example.com",
            "recipient_name": "Test Customer"
        })
        signature_request.insert()
        
        self.assertTrue(signature_request.signature_token)
        self.assertEqual(signature_request.status, "Draft")
        
        # Clean up
        frappe.delete_doc("Signature Request", signature_request.name, force=True)
    
    def test_signature_token_generation(self):
        """Test signature token generation"""
        from esignature.utils.security_manager import SecurityManager
        
        token1 = SecurityManager.generate_secure_token()
        token2 = SecurityManager.generate_secure_token()
        
        self.assertNotEqual(token1, token2)
        self.assertEqual(len(token1), 32)
        self.assertEqual(len(token2), 32)
    
    def test_pdf_signing(self):
        """Test PDF signing functionality"""
        # This would require a test certificate
        # Implementation depends on test certificate setup
        pass
