#!/usr/bin/env python3
"""
Script để kiểm tra trạng thái email trên production
"""

import os
import sys

def check_environment():
    """Kiểm tra environment variables"""
    print("🔍 Checking environment variables on production...")
    
    gmail_password = os.getenv('GMAIL_APP_PASSWORD')
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')
    
    print(f"GMAIL_APP_PASSWORD: {'✅ Set' if gmail_password else '❌ Not set'}")
    print(f"SMTP_USER: {'✅ Set' if smtp_user else '❌ Not set'}")
    print(f"SMTP_PASS: {'✅ Set' if smtp_pass else '❌ Not set'}")
    
    if gmail_password:
        print(f"Gmail App Password length: {len(gmail_password)} characters")
        print(f"Gmail App Password preview: {gmail_password[:4]}...{gmail_password[-4:]}")
    
    return bool(gmail_password or (smtp_user and smtp_pass))

def check_code_version():
    """Kiểm tra version code hiện tại"""
    print("\n🔍 Checking code version...")
    
    try:
        # Kiểm tra xem có function send_email_via_gmail_smtp không
        import app
        if hasattr(app, 'send_email_via_gmail_smtp'):
            print("✅ New email functions found in app.py")
            return True
        else:
            print("❌ Old version of app.py - missing new email functions")
            return False
    except Exception as e:
        print(f"❌ Error importing app.py: {e}")
        return False

def check_gmail_credentials():
    """Kiểm tra Gmail credentials file"""
    print("\n🔍 Checking Gmail credentials...")
    
    credentials_path = os.path.join(os.getcwd(), 'gmail-credentials.json')
    if os.path.exists(credentials_path):
        print("✅ Gmail credentials file found")
        return True
    else:
        print("❌ Gmail credentials file not found")
        return False

def main():
    print("🚀 Production Email Status Check")
    print("=" * 50)
    
    # Check environment
    env_ok = check_environment()
    
    # Check code version
    code_ok = check_code_version()
    
    # Check Gmail credentials
    creds_ok = check_gmail_credentials()
    
    print("\n📊 Summary:")
    print(f"Environment configured: {'✅' if env_ok else '❌'}")
    print(f"Code updated: {'✅' if code_ok else '❌'}")
    print(f"Gmail credentials: {'✅' if creds_ok else '❌'}")
    
    if env_ok and code_ok:
        print("\n🎉 Email should work! Try sending an invoice email.")
    else:
        print("\n⚠️  Email configuration incomplete:")
        if not code_ok:
            print("- Deploy new app.py to production")
        if not env_ok:
            print("- Set GMAIL_APP_PASSWORD environment variable")
        if not creds_ok:
            print("- Upload gmail-credentials.json (optional)")

if __name__ == "__main__":
    main()