# 🔐 Hướng dẫn sửa lỗi xác thực PythonAnywhere API

## ❌ Vấn đề hiện tại:
- **Stock quantity** được cập nhật thành công ✅
- **Order status** (`is_confirmed`, `status`) không được cập nhật ❌
- **Lý do**: API PythonAnywhere yêu cầu xác thực cho việc cập nhật orders

## 🔍 Chi tiết lỗi:
```
❌ Failed to update order: 401
🔐 API requires authentication for order update
```

## ✅ Giải pháp:

### 1. **Cập nhật Django Backend (PythonAnywhere)**

#### A. Sửa `views.py`:
```python
from rest_framework.permissions import AllowAny

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]  # Cho phép truy cập không cần xác thực
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            return [AllowAny()]
        return super().get_permissions()
```

#### B. Sửa `urls.py`:
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    # ... other patterns
]
```

#### C. Chạy migration:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. **Cập nhật Flask Backend (Local)**

#### A. Thêm authentication headers:
```python
# Trong app.py, function admin_api_confirm_order và admin_api_cancel_order
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_API_TOKEN',  # Nếu có token
    'Accept': 'application/json'
}
```

#### B. Hoặc sử dụng API key:
```python
headers = {
    'Content-Type': 'application/json',
    'X-API-Key': 'YOUR_API_KEY',  # Nếu có API key
    'Accept': 'application/json'
}
```

### 3. **Kiểm tra Django Settings**

#### A. Trong `settings.py`:
```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Cho phép truy cập công khai
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # Bỏ comment nếu muốn yêu cầu xác thực
        # 'rest_framework.authentication.TokenAuthentication',
    ],
}
```

### 4. **Test API trực tiếp**

#### A. Test với curl:
```bash
# Test cập nhật order
curl -X PATCH "https://buddyskincare.pythonanywhere.com/orders/17/" \
  -H "Content-Type: application/json" \
  -d '{"is_confirmed": true, "status": "processing"}'
```

#### B. Test với Python:
```python
import requests

url = "https://buddyskincare.pythonanywhere.com/orders/17/"
data = {"is_confirmed": True, "status": "processing"}
response = requests.patch(url, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
```

## 🎯 Kết quả mong đợi:

### Trước khi sửa:
- ✅ Stock quantity: Cập nhật thành công
- ❌ Order status: Không cập nhật (401 Unauthorized)
- ⚠️ Thông báo: "Cần cập nhật thủ công"

### Sau khi sửa:
- ✅ Stock quantity: Cập nhật thành công
- ✅ Order status: Cập nhật thành công
- ✅ Thông báo: "Đã xác nhận đơn hàng thành công"

## 📋 Checklist:

- [ ] Cập nhật Django `views.py` với `AllowAny` permission
- [ ] Cập nhật Django `settings.py` với `AllowAny` permission
- [ ] Chạy migration trên PythonAnywhere
- [ ] Test API trực tiếp với curl
- [ ] Test từ Flask admin panel
- [ ] Kiểm tra order status trên PythonAnywhere admin

## 🔧 Alternative Solution:

Nếu không thể sửa Django backend, có thể:

1. **Tạo API endpoint riêng** cho admin operations
2. **Sử dụng Django admin API** thay vì REST API
3. **Tạo webhook** để đồng bộ dữ liệu

## 📞 Support:

Nếu cần hỗ trợ thêm, hãy:
1. Kiểm tra logs trên PythonAnywhere
2. Test API trực tiếp
3. Cung cấp thông tin lỗi chi tiết
 
 
 
 