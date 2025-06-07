frappe.ui.form.on('Signature Request', {
    refresh: function(frm) {
        // Add custom buttons
        if (frm.doc.status === 'Draft') {
            frm.add_custom_button(__('Send Request'), function() {
                send_signature_request(frm);
            }, __('Actions'));
        }
        
        if (frm.doc.status === 'Sent' || frm.doc.status === 'Viewed') {
            frm.add_custom_button(__('Send Reminder'), function() {
                send_reminder(frm);
            }, __('Actions'));
            
            frm.add_custom_button(__('Cancel Request'), function() {
                cancel_signature_request(frm);
            }, __('Actions'));
        }
        
        if (frm.doc.status === 'Expired') {
            frm.add_custom_button(__('Resend Request'), function() {
                resend_signature_request(frm);
            }, __('Actions'));
        }
        
        if (frm.doc.status === 'Signed' && frm.doc.signed_document_url) {
            frm.add_custom_button(__('Download Signed Document'), function() {
                window.open(frm.doc.signed_document_url, '_blank');
            }, __('View'));
        }
        
        // Add signature link button if active
        if (frm.doc.signature_token && ['Sent', 'Viewed'].includes(frm.doc.status)) {
            frm.add_custom_button(__('Copy Signature Link'), function() {
                copy_signature_link(frm);
            }, __('View'));
        }
        
        // Set indicator colors
        set_status_indicator(frm);
    },
    
    reference_doctype: function(frm) {
        if (frm.doc.reference_doctype && frm.doc.reference_name) {
            // Auto-populate recipient details from reference document
            populate_recipient_details(frm);
        }
    },
    
    reference_name: function(frm) {
        if (frm.doc.reference_doctype && frm.doc.reference_name) {
            populate_recipient_details(frm);
        }
    }
});

function send_signature_request(frm) {
    frappe.confirm(__('Send signature request to {0}?', [frm.doc.recipient_email]), function() {
        frappe.call({
            method: 'esignature.api.signature_request.send_request',
            args: {
                'signature_request': frm.doc.name
            },
            callback: function(r) {
                if (r.message && r.message.success) {
                    frappe.msgprint(__('Signature request sent successfully'));
                    frm.reload_doc();
                } else {
                    frappe.msgprint(__('Failed to send signature request'));
                }
            }
        });
    });
}

function send_reminder(frm) {
    frappe.call({
        method: 'esignature.api.signature_request.send_reminder',
        args: {
            'signature_request': frm.doc.name
        },
        callback: function(r) {
            if (r.message && r.message.success) {
                frappe.msgprint(__('Reminder sent successfully'));
            } else {
                frappe.msgprint(__('Failed to send reminder'));
            }
        }
    });
}

function cancel_signature_request(frm) {
    frappe.confirm(__('Cancel this signature request?'), function() {
        frappe.call({
            method: 'esignature.api.signature_request.cancel_request',
            args: {
                'signature_request': frm.doc.name
            },
            callback: function(r) {
                if (r.message && r.message.success) {
                    frappe.msgprint(__('Signature request cancelled'));
                    frm.reload_doc();
                }
            }
        });
    });
}

function resend_signature_request(frm) {
    frappe.confirm(__('Resend signature request?'), function() {
        frappe.call({
            method: 'esignature.api.signature_request.resend_request',
            args: {
                'signature_request': frm.doc.name
            },
            callback: function(r) {
                if (r.message && r.message.success) {
                    frappe.msgprint(__('Signature request resent successfully'));
                    frm.reload_doc();
                }
            }
        });
    });
}

function copy_signature_link(frm) {
    const signing_url = `${window.location.origin}/sign_document?token=${frm.doc.signature_token}`;
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(signing_url).then(function() {
            frappe.msgprint(__('Signature link copied to clipboard'));
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = signing_url;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        frappe.msgprint(__('Signature link copied to clipboard'));
    }
}

function populate_recipient_details(frm) {
    frappe.call({
        method: 'esignature.utils.document_handler.get_recipient_details',
        args: {
            'doctype': frm.doc.reference_doctype,
            'name': frm.doc.reference_name
        },
        callback: function(r) {
            if (r.message) {
                frm.set_value('recipient_email', r.message.email);
                frm.set_value('recipient_name', r.message.name);
                frm.set_value('title', `${frm.doc.reference_doctype} ${frm.doc.reference_name} - Signature Required`);
            }
        }
    });
}

function set_status_indicator(frm) {
    const status_colors = {
        'Draft': 'gray',
        'Sent': 'blue',
        'Viewed': 'orange', 
        'Signed': 'green',
        'Expired': 'red',
        'Cancelled': 'red'
    };
    
    frm.page.set_indicator(frm.doc.status, status_colors[frm.doc.status] || 'gray');
}
