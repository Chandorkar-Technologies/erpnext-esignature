import frappe

def execute():
    """Create default digital certificates"""
    try:
        from esignature.install import create_default_certificates
        create_default_certificates()
        print("Default certificates created successfully")
    except Exception as e:
        print(f"Error in create_default_certificates patch: {str(e)}")

# esignature/patches/v1_0/setup_custom_fields.py
import frappe

def execute():
    """Setup custom fields for signature functionality"""
    try:
        from esignature.install import create_custom_fields_for_signature
        create_custom_fields_for_signature()
        print("Custom fields created successfully")
    except Exception as e:
        print(f"Error in setup_custom_fields patch: {str(e)}")
