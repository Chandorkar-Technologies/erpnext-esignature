import frappe
from frappe.email.doctype.email_template.email_template import get_email_template

class EmailProvider:
    """Enhanced email provider for signature notifications"""
    
    @staticmethod
    def send_signature_request_email(signature_request, template_name="Signature Request - Customer"):
        """Send signature request with enhanced template"""
        try:
            template = get_email_template(template_name)
            
            # Prepare template variables
            context = {
                "recipient_name": signature_request.recipient_name,
                "title": signature_request.title,
                "signing_url": f"{frappe.utils.get_url()}/sign_document?token={signature_request.signature_token}",
                "expires_on": frappe.utils.formatdate(signature_request.expires_on),
                "company_name": frappe.defaults.get_global_default("company"),
                "sender_name": frappe.get_value("User", frappe.session.user, "full_name")
            }
            
            # Render template
            subject = frappe.render_template(template.subject, context)
            message = frappe.render_template(template.response, context)
            
            # Send email with tracking
            frappe.sendmail(
                recipients=[signature_request.recipient_email],
                subject=subject,
                message=message,
                reference_doctype=signature_request.doctype,
                reference_name=signature_request.name,
                send_priority=1,
                retry=3
            )
            
            # Log email event
            from esignature.utils.security_manager import SecurityManager
            SecurityManager.log_security_event(
                "signature_request_sent",
                f"Email sent to {signature_request.recipient_email}",
                frappe.local.request_ip
            )
            
            return True
            
        except Exception as e:
            frappe.log_error(f"Enhanced email sending failed: {str(e)}")
            return False