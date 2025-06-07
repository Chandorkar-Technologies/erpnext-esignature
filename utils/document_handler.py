import frappe

def handle_internal_signature(doc, method):
    """Handle internal document signing before submit"""
    # Placeholder for internal signing logic
    frappe.msgprint(f"Internal signature applied to {doc.doctype} {doc.name}")

def create_signature_request(doc, method):
    """Create external signature request after document submit"""
    if not should_create_signature_request(doc):
        return
    
    try:
        # Get recipient details
        recipient_email, recipient_name = get_recipient_details(doc)
        if not recipient_email:
            return
        
        # Create signature request
        signature_request = frappe.get_doc({
            "doctype": "Signature Request",
            "title": f"{doc.doctype} {doc.name} - Customer Signature",
            "reference_doctype": doc.doctype,
            "reference_name": doc.name,
            "request_type": "External Customer",
            "recipient_email": recipient_email,
            "recipient_name": recipient_name,
            "status": "Draft"
        })
        
        signature_request.insert()
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Creating signature request failed for {doc.doctype} {doc.name}: {str(e)}")

def should_create_signature_request(doc):
    """Check if signature request should be created"""
    return (
        doc.doctype in ["Quotation", "Sales Invoice"] and 
        getattr(doc, 'requires_signature', False)
    )

def get_recipient_details(doc):
    """Get recipient email and name for external signature"""
    recipient_email = None
    recipient_name = None
    
    if hasattr(doc, 'customer_email') and doc.customer_email:
        recipient_email = doc.customer_email
        recipient_name = doc.customer_name or doc.customer
    elif hasattr(doc, 'contact_email') and doc.contact_email:
        recipient_email = doc.contact_email
        recipient_name = doc.contact_person
    
    return recipient_email, recipient_name
