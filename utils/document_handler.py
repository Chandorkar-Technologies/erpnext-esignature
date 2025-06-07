import frappe
from esignature.utils.pdf_handler import PDFSignatureHandler

def handle_internal_signature(doc, method):
    """Handle internal document signing before submit"""
    if not should_sign_document(doc.doctype):
        return
    
    try:
        # Get appropriate certificate for document type
        certificate_name = get_certificate_for_doctype(doc.doctype)
        if not certificate_name:
            return
        
        # Generate PDF
        pdf_content = get_document_pdf(doc)
        if not pdf_content:
            return
        
        # Sign PDF
        pdf_handler = PDFSignatureHandler()
        signed_pdf = pdf_handler.sign_pdf_internal(
            pdf_content, 
            certificate_name, 
            f"Internal signature for {doc.doctype} {doc.name}"
        )
        
        # Save signed PDF
        save_signed_document(doc, signed_pdf, "internal")
        
    except Exception as e:
        frappe.log_error(f"Internal signing failed for {doc.doctype} {doc.name}: {str(e)}")

def create_signature_request(doc, method):
    """Create external signature request after document submit"""
    if not requires_external_signature(doc.doctype):
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

def should_sign_document(doctype):
    """Check if document type requires internal signing"""
    signing_doctypes = ["Quotation", "Sales Invoice", "Salary Slip", "Purchase Order"]
    return doctype in signing_doctypes

def requires_external_signature(doctype):
    """Check if document type requires external signature"""
    external_doctypes = ["Quotation", "Sales Invoice"]
    return doctype in external_doctypes

def get_certificate_for_doctype(doctype):
    """Get appropriate certificate for document type"""
    certificate_mapping = {
        "Quotation": "Sales Certificate",
        "Sales Invoice": "Sales Certificate", 
        "Salary Slip": "HR Certificate",
        "Purchase Order": "Purchase Certificate"
    }
    
    cert_name = certificate_mapping.get(doctype)
    if cert_name and frappe.db.exists("Digital Certificate", cert_name):
        return cert_name
    
    # Fallback to any active internal certificate
    certs = frappe.get_all("Digital Certificate", 
                          filters={"is_active": 1, "certificate_type": "Internal"},
                          limit=1)
    return certs[0].name if certs else None

def get_document_pdf(doc):
    """Generate PDF for document"""
    try:
        pdf = frappe.get_print(
            doctype=doc.doctype,
            name=doc.name,
            format="Standard",
            as_pdf=True
        )
        return pdf
    except Exception as e:
        frappe.log_error(f"PDF generation failed: {str(e)}")
        return None

def save_signed_document(doc, signed_pdf_content, signature_type):
    """Save signed PDF as attachment"""
    try:
        filename = f"{doc.doctype}_{doc.name}_{signature_type}_signed.pdf"
        
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": filename,
            "content": signed_pdf_content,
            "attached_to_doctype": doc.doctype,
            "attached_to_name": doc.name,
            "is_private": 1
        })
        file_doc.insert()
        
        return file_doc.file_url
        
    except Exception as e:
        frappe.log_error(f"Saving signed document failed: {str(e)}")
        return None

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
