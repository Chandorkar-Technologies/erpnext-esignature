import frappe
import requests
import json

class WebhookHandler:
    """Handle webhooks for signature events"""
    
    @staticmethod
    def send_webhook(event_type, data, webhook_url=None):
        """Send webhook notification"""
        if not webhook_url:
            webhook_url = frappe.get_single("E-Signature Settings").webhook_url
        
        if not webhook_url:
            return
        
        try:
            payload = {
                "event": event_type,
                "timestamp": frappe.utils.now(),
                "data": data,
                "site": frappe.local.site
            }
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": f"ERPNext-ESignature/{frappe.__version__}"
            }
            
            response = requests.post(
                webhook_url,
                data=json.dumps(payload),
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                frappe.log_error(f"Webhook sent successfully: {event_type}")
            else:
                frappe.log_error(f"Webhook failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            frappe.log_error(f"Webhook error: {str(e)}")
