# 🚨 Sửa lỗi danh sách đơn hàng không hiện

## ❌ **Vấn đề hiện tại:**
- Danh sách đơn hàng không tải được (lỗi 500)
- API PythonAnywhere cũng bị lỗi

## 🔍 **Nguyên nhân:**
File `views.py` trên PythonAnywhere chưa được cập nhật hoặc có lỗi syntax

## ✅ **Giải pháp:**

### **Bước 1: Kiểm tra file views.py trên PythonAnywhere**

#### **A. Truy cập PythonAnywhere:**
- Đăng nhập vào PythonAnywhere
- Mở file `views.py` trong Django project

#### **B. Kiểm tra method `get_permissions` trong class `OrderViewSet`:**
Tìm dòng này:
```python
def get_permissions(self):
    if self.action in ['create', 'list', 'retrieve', 'update', 'partial_update', 'destroy']:
        self.permission_classes = [AllowAny]
    else:
        self.permission_classes = [IsAuthenticated]
    return super().get_permissions()
```

#### **C. Nếu chưa có, thay thế toàn bộ method:**
```python
def get_permissions(self):
    """
    Set permissions based on action.
    - allow POST for unauthenticated users (for non-logged-in orders)
    - allow GET for unauthenticated users (for admin access)
    - allow PUT, PATCH, DELETE for unauthenticated users (for admin updates)
    """
    if self.action in ['create', 'list', 'retrieve', 'update', 'partial_update', 'destroy']:
        # Cho phép mọi người tạo đơn hàng, xem danh sách đơn hàng và cập nhật đơn hàng (cho admin)
        self.permission_classes = [AllowAny]
    else:
        # Các hành động khác yêu cầu đăng nhập (ví dụ: xem lịch sử đơn hàng)
        self.permission_classes = [IsAuthenticated]
    return super().get_permissions()
```

### **Bước 2: Kiểm tra import**

Đảm bảo có import này ở đầu file:
```python
from rest_framework.permissions import AllowAny, IsAuthenticated
```

### **Bước 3: Test API**

#### **A. Test PythonAnywhere trực tiếp:**
```bash
curl -s "https://buddyskincare.pythonanywhere.com/orders/" | head -10
```

#### **B. Test Flask integration:**
```bash
curl -s "http://localhost:8000/admin/api/orders" | head -10
```

### **Bước 4: Nếu vẫn lỗi, kiểm tra Django logs**

#### **A. Trên PythonAnywhere:**
- Vào phần "Tasks" → "Always-on task"
- Kiểm tra logs để xem lỗi cụ thể

#### **B. Hoặc restart Django app:**
- Vào phần "Web" → "Reload" để restart Django app

## 🎯 **Kết quả mong đợi:**

- ✅ API PythonAnywhere trả về danh sách orders (JSON)
- ✅ Flask integration hoạt động bình thường
- ✅ Admin panel hiển thị danh sách đơn hàng

## ⏱️ **Thời gian sửa: ~5 phút**

Sau khi cập nhật file `views.py` trên PythonAnywhere, danh sách đơn hàng sẽ hiển thị bình thường! 🎉
 
 
 
 