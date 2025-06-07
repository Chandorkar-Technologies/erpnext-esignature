import frappe
from pyhanko import stamp
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import signers, fields
from pyhanko.pdf_utils import generic
from pyhanko.pdf_utils.reader import PdfFileReader
from io import BytesIO
import os
from datetime import datetime

class PDFSignatureHandler:
    def __init__(self):
        self.temp_dir = "/tmp/esignature"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def sign_pdf_internal(self, pdf_content, certificate_name, signature_reason="Document Approval"):
        """Sign PDF with internal certificate"""
        try:
            # Get certificate
            cert_doc = frappe.get_doc("Digital Certificate", certificate_name)
            if not cert_doc.is_active:
                frappe.throw("Certificate is not active")
            
            # Load certificate file
            file_doc = frappe.get_doc("File", {"file_url": cert_doc.certificate_file})
            cert_path = file_doc.get_full_path()
            
            # Create signer
            with open(cert_path, 'rb') as cert_file:
                signer = signers.SimpleSigner.load_pkcs12(
                    pfx_file=cert_file,
                    passphrase=cert_doc.password.encode()
                )
            
            # Prepare PDF for signing
            pdf_stream = BytesIO(pdf_content)
            reader = PdfFileReader(pdf_stream)
            writer = IncrementalPdfFileWriter(pdf_stream)
            
            # Create signature field
            sig_field = fields.SigFieldSpec(
                sig_name='Signature',
                on_page=0,  # First page
                bbox=(100, 100, 300, 150)  # Signature position
            )
            
            fields.append_signature_field(writer, sig_field)
            
            # Sign the document
            meta = signers.PdfSignatureMetadata(
                field_name='Signature',
                reason=signature_reason,
                location=frappe.local.site,
                certify=False,
                subfilter=fields.SigSeedSubFilter.ADOBE_PKCS7_DETACHED
            )
            
            signed_pdf = signers.sign_pdf(
                writer, meta, signer=signer
            )
            
            return signed_pdf.getvalue()
            
        except Exception as e:
            frappe.log_error(f"PDF signing failed: {str(e)}")
            frappe.throw(f"Failed to sign PDF: {str(e)}")
    
    def add_signature_placeholder(self, pdf_content, signature_coords=None):
        """Add signature placeholder for external signing"""
        try:
            pdf_stream = BytesIO(pdf_content)
            reader = PdfFileReader(pdf_stream)
            writer = IncrementalPdfFileWriter(pdf_stream)
            
            # Default signature position (bottom right of first page)
            if not signature_coords:
                page = reader.pages[0]
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)
                signature_coords = (page_width - 200, 50, page_width - 50, 100)
            
            # Add signature field
            sig_field = fields.SigFieldSpec(
                sig_name='CustomerSignature',
                on_page=0,
                bbox=signature_coords
            )
            
            fields.append_signature_field(writer, sig_field)
            
            return writer.write_in_place()
            
        except Exception as e:
            frappe.log_error(f"Adding signature placeholder failed: {str(e)}")
            return pdf_content
