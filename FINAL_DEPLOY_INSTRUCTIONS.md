# 🚀 HƯỚNG DẪN DEPLOY CUỐI CÙNG

## ❌ Vấn đề hiện tại:
- Django endpoint `/backend/api/upload-cccd/` không tồn tại trên production (404)
- Ảnh CTV vẫn lưu dưới dạng base64 thay vì Cloudinary
- Các files đã sửa đúng nhưng chưa deploy

## ✅ Files cần deploy:

### 1. **views.py** (Django CCCD upload endpoint)
- Function: `upload_cccd_image()` (dòng 2097-2174)
- Upload ảnh lên Cloudinary folder `ctv_cccd`

### 2. **urls.py** (Django route)
- Route: `path('api/upload-cccd/', views.upload_cccd_image, name='upload-cccd')` (dòng 58)

### 3. **settings.py** (Cloudinary config)
- Cloudinary config (dòng 17-26)
- CSRF exempt paths (dòng 41-45)

### 4. **models.py** (TextField cho CCCD URLs)
- CTVApplication: `cccd_front_url = models.TextField()` (dòng 762)
- CTV: `cccd_front_url = models.TextField()` (dòng 788)

### 5. **templates/partner.html** (JavaScript)
- Gọi `/backend/api/upload-cccd/` (dòng 250)
- Debug logging chi tiết

### 6. **migrations/0007_update_cccd_url_fields.py**
- Migration để cập nhật database schema

## 📋 Các bước deploy:

### Bước 1: Upload files qua PythonAnywhere
1. Vào: https://www.pythonanywhere.com/user/budduskincarevn/
2. Tab **"Files"** → `/home/buddyskincare/websitemypham/`
3. Upload từng file:
   - `views.py`
   - `urls.py` 
   - `settings.py`
   - `models.py`
   - `templates/partner.html`
   - `migrations/0007_update_cccd_url_fields.py`

### Bước 2: Cài đặt package
1. Tab **"Consoles"** → New console
2. Chạy: `pip3 install cloudinary==1.36.0`

### Bước 3: Chạy migration
1. Trong console: `cd /home/buddyskincare/websitemypham`
2. Chạy: `python3 manage.py migrate`

### Bước 4: Reload Django app
1. Tab **"Web"**
2. Click **"Reload"** cho Django web app

### Bước 5: Test
1. Vào: https://buddyskincare.vn/partner
2. Upload ảnh CCCD
3. Check browser console (F12) để xem logs
4. Kiểm tra xem ảnh có upload lên Cloudinary không

## 🎯 Kết quả mong đợi:
- ✅ Django endpoint `/backend/api/upload-cccd/` hoạt động
- ✅ Ảnh upload lên Cloudinary folder `ctv_cccd`
- ✅ URL Cloudinary có thể xem được ảnh
- ✅ Không còn base64 storage trong database

## 🔍 Debug nếu vẫn lỗi:
1. Check browser console (F12) → Console tab
2. SSH vào server: `ssh budduskincarevn@gmail.com@budduskincare.pythonanywhere.com`
3. Check Django logs: `tail -f /var/log/budduskincare.pythonanywhere.com.error.log`

---
**Lưu ý:** Sau khi deploy xong, hãy test ngay để đảm bảo endpoint hoạt động!