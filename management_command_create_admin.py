# Tạo file: your_app/management/commands/create_admin.py

from django.core.management.base import BaseCommand
from your_app.models import Admin

class Command(BaseCommand):
    help = 'Create admin user'

    def add_arguments(self, parser):
        parser.add_argument('--phone', type=str, default='0987789274', help='Phone number')
        parser.add_argument('--password', type=str, default='123', help='Password')
        parser.add_argument('--email', type=str, default='admin@buddyskincare.com', help='Email')
        parser.add_argument('--name', type=str, default='Admin BuddySkincare', help='Name')

    def handle(self, *args, **options):
        phone_number = options['phone']
        password = options['password']
        email = options['email']
        name = options['name']
        
        try:
            # Check if admin already exists
            if Admin.objects.filter(phone_number=phone_number).exists():
                self.stdout.write(
                    self.style.WARNING(f'Admin với số điện thoại {phone_number} đã tồn tại!')
                )
                return
            
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
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Tạo tài khoản admin thành công!')
            )
            self.stdout.write(f'📱 Số điện thoại: {phone_number}')
            self.stdout.write(f'📧 Email: {email}')
            self.stdout.write(f'👤 Tên: {name}')
            self.stdout.write(f'🔑 Mật khẩu: {password}')
            self.stdout.write(f'🆔 Admin ID: {admin.id}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Lỗi khi tạo admin: {e}')
            )
 
 
 
 