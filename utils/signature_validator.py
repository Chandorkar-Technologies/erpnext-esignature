import frappe
from pyhanko.sign import validation
from pyhanko.pdf_utils.reader import PdfFileReader
from io import BytesIO

class SignatureValidator:
    """Validate PDF signatures"""
    
    @staticmethod
    def validate_pdf_signatures(pdf_content):
        """Validate all signatures in PDF"""
        try:
            pdf_stream = BytesIO(pdf_content)
            reader = PdfFileReader(pdf_stream)
            
            # Get signature fields
            sig_fields = validation.collect_validation_info(reader)
            
            validation_results = []
            for field_name, sig_obj in sig_fields:
                try:
                    status = validation.validate_pdf_signature(sig_obj)
                    validation_results.append({
                        "field_name": field_name,
                        "valid": status.intact and status.valid,
                        "signer": status.signer_info.signer_cert.subject.rfc4514_string() if status.signer_info else None,
                        "signing_time": status.signer_info.signing_time if status.signer_info else None,
                        "details": str(status)
                    })
                except Exception as e:
                    validation_results.append({
                        "field_name": field_name,
                        "valid": False,
                        "error": str(e)
                    })
            
            return validation_results
            
        except Exception as e:
            frappe.log_error(f"Signature validation failed: {str(e)}")
            return []