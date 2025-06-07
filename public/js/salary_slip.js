frappe.ui.form.on('Salary Slip', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1 && frm.doc.employee_signature_required) {
            frm.add_custom_button(__('Send for Signature'), function() {
                // Logic to send salary slip for employee signature
                frappe.msgprint('Signature request functionality will be implemented here');
            });
        }
    }
});