# ERPNext E-Signature App

A comprehensive digital signature solution for ERPNext using pyHanko library.

## Features

### Internal Signatures
- Automatic signing of quotations, invoices, salary slips with digital certificates
- Support for PKCS#12 certificates (.p12, .pfx files)
- Role-based certificate assignment
- Audit trail for all signature activities

### External Signatures
- Send signature requests to customers/vendors via email
- Web-based signature interface with drawing pad
- Mobile-responsive design
- Token-based secure signing URLs
- Automatic reminders and expiration handling

### Security & Compliance
- PKI-based digital signatures using pyHanko
- PDF/A compliance for long-term archival
- IP address tracking and timestamp logging
- Certificate validation and revocation checking

## Installation

1. Install the app:
```bash
bench get-app https://github.com/yourusername/erpnext-esignature
bench install-app esignature
```

2. Install Python dependencies:
```bash
pip install pyhanko cryptography qrcode reportlab
```

3. Restart ERPNext:
```bash
bench restart
```

## Configuration

### 1. Digital Certificates Setup

1. Go to **E-Signature > Digital Certificate**
2. Create new certificate records for different departments (Sales, HR, Purchase)
3. Upload your .p12/.pfx certificate files
4. Enter certificate passwords
5. Activate certificates

### 2. Document Configuration

- **Quotations**: Automatically signed before submission, external signature request sent to customer
- **Sales Invoices**: Internal signing optional, external signature available
- **Salary Slips**: HR signature applied automatically
- **Purchase Orders**: Internal signing for approval workflow

### 3. Email Templates

Customize email templates in **E-Signature > Email Template**:
- Signature Request - Customer
- Signature Confirmation

## Usage

### Internal Signatures
Internal signatures are applied automatically when documents are submitted, based on:
- Document type (Quotation, Invoice, etc.)
- Available active certificates
- User roles and permissions

### External Signatures
1. Document is submitted with "Requires Signature" checked
2. Signature request is automatically created
3. Email with secure signing link is sent to recipient
4. Recipient clicks link, reviews document, and signs
5. Signed document is stored and linked to original record

### Signature Request Management
- View all signature requests in **E-Signature > Signature Request**
- Track status: Draft, Sent, Viewed, Signed, Expired
- Send manual reminders
- Cancel or resend expired requests

## API Endpoints

### External Signing API
- `GET /api/method/esignature.api.external_signing.get_document?token=<token>`
- `POST /api/method/esignature.api.external_signing.sign_document`

### Internal Signing API  
- Certificate management
- PDF signing operations
- Signature validation

## Scheduled Tasks

- **Hourly**: Send signature reminders based on frequency settings
- **Daily**: Mark expired signature requests

## Security Considerations

1. **Certificate Storage**: Store certificates securely with proper access controls
2. **Token Security**: Signature tokens are cryptographically secure and expire automatically  
3. **Network Security**: Use HTTPS for all signature operations
4. **Audit Trail**: All signature activities are logged with timestamps and IP addresses

## Troubleshooting

### Common Issues

1. **Certificate Loading Errors**
   - Verify certificate file format (.p12/.pfx)
   - Check certificate password
   - Ensure certificate is not expired

2. **PDF Signing Failures**
   - Check pyHanko installation
   - Verify certificate validity
   - Review error logs in ERPNext

3. **Email Delivery Issues**
   - Configure SMTP settings in ERPNext
   - Check email templates
   - Verify recipient email addresses

### Logs and Debugging

Check ERPNext error logs for detailed error messages:
```bash
tail -f sites/[site-name]/logs/web.log
```

## License

MIT License - see LICENSE file for details.

## Support

For support and customization:
- Create issues on GitHub repository
- Contact: admin@yourcompany.com

## Contributing

1. Fork the repository
2. Create feature branch
3. Submit pull request with tests
4. Update documentation
