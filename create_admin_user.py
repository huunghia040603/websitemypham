#!/usr/bin/env python
"""
Script to create admin user
Run this script in Django shell or as a management command
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
django.setup()

from your_app.models import Admin

def create_admin_user():
    """
    Create admin user with phone number 0987789274 and password 123
    """
    phone_number = "0987789274"
    password = "123"
    email = "admin@buddyskincare.com"
    name = "Admin BuddySkincare"
    
    try:
        # Check if admin already exists
        if Admin.objects.filter(phone_number=phone_number).exists():
            print(f"❌ Admin với số điện thoại {phone_number} đã tồn tại!")
            return False
        
        # Create admin user
        admin = Admin.objects.create(
            phone_number=phone_number,
            email=email,
            name=name,
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        
        # Set password
        admin.set_password(password)
        admin.save()
        
        print(f"✅ Tạo tài khoản admin thành công!")
        print(f"📱 Số điện thoại: {phone_number}")
        print(f"📧 Email: {email}")
        print(f"👤 Tên: {name}")
        print(f"🔑 Mật khẩu: {password}")
        print(f"🆔 Admin ID: {admin.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi tạo admin: {e}")
        return False

if __name__ == "__main__":
    create_admin_user()
 
 
 
 