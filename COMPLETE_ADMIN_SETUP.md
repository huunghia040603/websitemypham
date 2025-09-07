# Hướng dẫn tạo tài khoản Admin cho BuddySkincare

## 📋 Tổng quan
Tài khoản admin sẽ được tạo với:
- **Số điện thoại:** 0987789274
- **Mật khẩu:** 123
- **Email:** admin@buddyskincare.com
- **Tên:** Admin BuddySkincare

## 🔧 Các file cần cập nhật

### 1. Cập nhật `serializers.py`
Thêm vào cuối file:

```python
class AdminSerializer(serializers.ModelSerializer):
    """
    Serializer for Admin model
    """
    class Meta:
        model = Admin
        fields = ('id', 'name', 'email', 'phone_number', 'address', 'dob', 'avatar', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
        read_only_fields = ('id', 'date_joined')

    def create(self, validated_data):
        """
        Create a new admin user
        """
        password = validated_data.pop('password', None)
        admin = Admin.objects.create(**validated_data)
        if password:
            admin.set_password(password)
        admin.is_staff = True
        admin.is_superuser = True
        admin.is_active = True
        admin.save()
        return admin

    def update(self, instance, validated_data):
        """
        Update admin user
        """
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
```

### 2. Cập nhật `views.py`
Thêm vào cuối file:

```python
class AdminViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Admin management
    """
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [AllowAny]  # Có thể thay đổi thành IsAuthenticated nếu cần

    def get_queryset(self):
        return Admin.objects.all()

    @action(detail=False, methods=['post'], url_path='create-admin')
    def create_admin(self, request):
        """
        Create a new admin user
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            admin = serializer.save()
            return Response({
                'success': True,
                'message': 'Tạo tài khoản admin thành công',
                'admin_id': admin.id,
                'phone_number': admin.phone_number,
                'email': admin.email
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Lỗi khi tạo tài khoản admin',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='admin-login')
    def admin_login(self, request):
        """
        Admin login with phone number and password
        """
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        
        if not phone_number or not password:
            return Response({
                'success': False,
                'message': 'Vui lòng cung cấp số điện thoại và mật khẩu'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            admin = Admin.objects.get(phone_number=phone_number)
            if admin.check_password(password) and admin.is_active:
                # Generate JWT tokens
                refresh = RefreshToken.for_user(admin)
                return Response({
                    'success': True,
                    'message': 'Đăng nhập admin thành công',
                    'admin': AdminSerializer(admin).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Mật khẩu không đúng hoặc tài khoản bị vô hiệu hóa'
                }, status=status.HTTP_401_UNAUTHORIZED)
        except Admin.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Không tìm thấy tài khoản admin với số điện thoại này'
            }, status=status.HTTP_404_NOT_FOUND)
```

### 3. Cập nhật `urls.py`
Thêm vào phần đăng ký ViewSet:

```python
# Thêm dòng này vào phần đăng ký ViewSet với router:
r.register(r'admin', views.AdminViewSet, basename='admin')
```

### 4. Tạo Management Command
Tạo file `your_app/management/commands/create_admin.py`:

```python
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
```

## 🚀 Cách thực hiện

### Bước 1: Cập nhật các file
Copy và paste các đoạn code trên vào các file tương ứng trên PythonAnywhere.

### Bước 2: Chạy migration (nếu cần)
```bash
python manage.py makemigrations
python manage.py migrate
```

### Bước 3: Tạo admin user
```bash
python manage.py create_admin
```

Hoặc với tham số tùy chỉnh:
```bash
python manage.py create_admin --phone 0987789274 --password 123 --email admin@buddyskincare.com --name "Admin BuddySkincare"
```

### Bước 4: Test API
```bash
# Test tạo admin qua API
curl -X POST "https://buddyskincare.pythonanywhere.com/admin/create-admin/" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "0987789274",
    "password": "123",
    "email": "admin@buddyskincare.com",
    "name": "Admin BuddySkincare"
  }'

# Test đăng nhập admin
curl -X POST "https://buddyskincare.pythonanywhere.com/admin/admin-login/" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "0987789274",
    "password": "123"
  }'
```

## ✅ Kết quả mong đợi
Sau khi hoàn thành, bạn sẽ có:
- Tài khoản admin với số điện thoại 0987789274
- Mật khẩu 123
- Quyền staff và superuser
- API endpoints để quản lý admin
- Có thể đăng nhập qua API

## 🔐 Bảo mật
- Thay đổi mật khẩu mặc định sau khi tạo
- Cập nhật permission_classes thành IsAuthenticated nếu cần
- Thêm validation cho các trường quan trọng
 
 
 
 