# Hướng dẫn Deploy Manual

## Vấn đề hiện tại:
- Endpoint `/backend/api/upload-bank-transfer/` trả về HTML thay vì JSON
- Lỗi: `SyntaxError: Unexpected token '<', "<!DOCTYPE "... is not valid JSON`

## Giải pháp:

### 1. Kiểm tra endpoint trên PythonAnywhere Console:

```bash
# Vào PythonAnywhere Console
# Test endpoint
curl -X POST https://buddyskincare.vn/backend/api/upload-bank-transfer/
```

### 2. Kiểm tra Django logs:

```bash
# Vào PythonAnywhere Console
tail -f /var/log/buddyskincare.vn.error.log
```

### 3. Deploy files thủ công:

```bash
# Copy file views.py
cp views.py /home/buddyskincare/websitemypham/views.py

# Copy file urls.py  
cp urls.py /home/buddyskincare/websitemypham/urls.py

# Copy file static/js/main.js
cp static/js/main.js /home/buddyskincare/websitemypham/static/js/main.js
```

### 4. Reload web app:
- Vào PythonAnywhere Web tab
- Click "Reload" button

### 5. Test lại:
- Vào checkout page
- Chọn "Chuyển khoản ngân hàng"
- Upload ảnh
- Đặt hàng

## Debug steps:

1. **Kiểm tra Django URL routing:**
```python
# Trong PythonAnywhere Console
python manage.py show_urls | grep upload-bank-transfer
```

2. **Kiểm tra Django view:**
```python
# Test view function
from views import upload_bank_transfer
print(upload_bank_transfer)
```

3. **Kiểm tra Cloudinary config:**
```python
# Test Cloudinary
import cloudinary
print(cloudinary.config().cloud_name)
```