frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1 && frm.doc.requires_signature) {
            frm.add_custom_button(__('View Signature Requests'), function() {
                frappe.set_route('List', 'Signature Request', {
                    'reference_doctype': frm.doc.doctype,
                    'reference_name': frm.doc.name
                });
            });
        }
    }
});