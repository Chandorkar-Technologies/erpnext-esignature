import frappe
import hashlib
import hmac
import time
from datetime import datetime, timedelta

class SecurityManager:
    """Handle security aspects of signature requests"""
    
    @staticmethod
    def generate_secure_token(length=32):
        """Generate cryptographically secure token"""
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def validate_signature_token(token, signature_request_name):
        """Validate signature token against database"""
        try:
            doc = frappe.get_doc("Signature Request", {"signature_token": token})
            return doc.name == signature_request_name
        except:
            return False
    
    @staticmethod
    def log_security_event(event_type, details, ip_address=None):
        """Log security-related events"""
        security_log = frappe.get_doc({
            "doctype": "Signature Security Log",
            "event_type": event_type,
            "details": details,
            "ip_address": ip_address or frappe.local.request_ip,
            "timestamp": datetime.now(),
            "user": frappe.session.user
        })
        security_log.insert(ignore_permissions=True)
    
    @staticmethod
    def check_rate_limit(ip_address, action="signature_attempt", limit=5, window_minutes=15):
        """Implement rate limiting for signature attempts"""
        window_start = datetime.now() - timedelta(minutes=window_minutes)
        
        # Count recent attempts from this IP
        recent_attempts = frappe.db.count("Signature Security Log", {
            "ip_address": ip_address,
            "event_type": action,
            "timestamp": [">=", window_start]
        })
        
        if recent_attempts >= limit:
            SecurityManager.log_security_event(
                "rate_limit_exceeded",
                f"IP {ip_address} exceeded rate limit for {action}",
                ip_address
            )
            return False
        
        return True
    
    @staticmethod
    def generate_audit_hash(document_content, signature_data):
        """Generate audit hash for signed document"""
        combined_data = document_content + signature_data.encode()
        return hashlib.sha256(combined_data).hexdigest()

# DocType: Signature Security Log
signature_security_log_doctype = {
    "creation": "2024-01-01 00:00:00",
    "doctype": "DocType",
    "engine": "InnoDB",
    "field_order": [
        "event_type",
        "details",
        "column_break_3",
        "ip_address",
        "timestamp",
        "user"
    ],
    "fields": [
        {
            "fieldname": "event_type",
            "fieldtype": "Select",
            "label": "Event Type",
            "options": "signature_attempt\ntoken_validation\nrate_limit_exceeded\nsignature_completed\nsecurity_violation",
            "reqd": 1
        },
        {
            "fieldname": "details",
            "fieldtype": "Text",
            "label": "Details"
        },
        {
            "fieldname": "column_break_3",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "ip_address",
            "fieldtype": "Data",
            "label": "IP Address"
        },
        {
            "fieldname": "timestamp",
            "fieldtype": "Datetime",
            "label": "Timestamp",
            "reqd": 1
        },
        {
            "fieldname": "user",
            "fieldtype": "Link",
            "label": "User",
            "options": "User"
        }
    ],
    "modified": "2024-01-01 00:00:00",
    "modified_by": "Administrator",
    "module": "E-Signature",
    "name": "Signature Security Log",
    "naming_rule": "Expression (old style)",
    "autoname": "SEC-LOG-.YYYY.-.MM.-.#####",
    "owner": "Administrator",
    "permissions": [
        {
            "create": 1,
            "read": 1,
            "report": 1,
            "role": "System Manager"
        }
    ],
    "sort_field": "creation",
    "sort_order": "DESC",
    "track_changes": 1
}
