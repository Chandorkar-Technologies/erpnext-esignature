frappe.ui.form.on('Digital Certificate', {
    refresh: function(frm) {
        if (frm.doc.certificate_file && frm.doc.password) {
            frm.add_custom_button(__('Test Certificate'), function() {
                test_certificate(frm);
            }, __('Actions'));
            
            frm.add_custom_button(__('Validate Certificate'), function() {
                validate_certificate(frm);
            }, __('Actions'));
        }
        
        if (frm.doc.certificate_file) {
            frm.add_custom_button(__('Extract Info'), function() {
                extract_certificate_info(frm);
            }, __('Actions'));
        }
        
        // Set indicator
        if (frm.doc.is_active) {
            frm.page.set_indicator(__('Active'), 'green');
        } else {
            frm.page.set_indicator(__('Inactive'), 'red');
        }
    },
    
    certificate_file: function(frm) {
        if (frm.doc.certificate_file && frm.doc.password) {
            extract_certificate_info(frm);
        }
    },
    
    password: function(frm) {
        if (frm.doc.certificate_file && frm.doc.password) {
            extract_certificate_info(frm);
        }
    }
});

function test_certificate(frm) {
    frappe.call({
        method: 'esignature.utils.certificate_manager.validate_certificate',
        args: {
            'certificate_name': frm.doc.name
        },
        callback: function(r) {
            if (r.message && r.message[0]) {
                frappe.msgprint(__('Certificate is valid and ready to use'));
            } else {
                frappe.msgprint(__('Certificate validation failed: {0}', [r.message[1]]));
            }
        }
    });
}

function validate_certificate(frm) {
    frappe.call({
        method: 'esignature.utils.certificate_manager.validate_certificate',
        args: {
            'certificate_name': frm.doc.name
        },
        callback: function(r) {
            if (r.message) {
                const [is_valid, message] = r.message;
                if (is_valid) {
                    frappe.msgprint({
                        title: __('Certificate Valid'),
                        message: message,
                        indicator: 'green'
                    });
                } else {
                    frappe.msgprint({
                        title: __('Certificate Invalid'),
                        message: message,
                        indicator: 'red'
                    });
                }
            }
        }
    });
}

function extract_certificate_info(frm) {
    if (!frm.doc.password) {
        frappe.msgprint(__('Please enter certificate password first'));
        return;
    }
    
    frappe.call({
        method: 'extract_certificate_info',
        doc: frm.doc,
        callback: function(r) {
            if (!r.exc) {
                frm.reload_doc();
                frappe.msgprint(__('Certificate information extracted successfully'));
            }
        }
    });
}
