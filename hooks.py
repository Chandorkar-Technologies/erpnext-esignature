doc_events = {
    "Quotation": {
        "before_submit": "esignature.utils.document_handler.handle_internal_signature",
        "on_submit": "esignature.utils.document_handler.create_signature_request"
    },
    "Sales Invoice": {
        "before_submit": "esignature.utils.document_handler.handle_internal_signature",
        "on_submit": "esignature.utils.document_handler.create_signature_request"
    },
    "Salary Slip": {
        "before_submit": "esignature.utils.document_handler.handle_internal_signature"
    },
    "Purchase Order": {
        "before_submit": "esignature.utils.document_handler.handle_internal_signature"
    }
}
