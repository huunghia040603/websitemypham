# 🚨 KHẨN CẤP: DEPLOY FIX NGAY LẬP TỨC

## ❌ VẤN ĐỀ HIỆN TẠI:
- **Flask endpoint `/api/upload-cccd`**: 404 Not Found
- **Django endpoint `/backend/api/upload-cccd/`**: 404 Not Found  
- **Ảnh CTV vẫn lưu dưới dạng base64** thay vì Cloudinary

## 🔥 NGUYÊN NHÂN:
**Files chưa được deploy lên production!** Cả Flask và Django apps đều thiếu endpoints.

## ✅ GIẢI PHÁP KHẨN CẤP:

### Bước 1: Deploy Flask App (app.py)
1. Vào PythonAnywhere: https://www.pythonanywhere.com/user/budduskincarevn/
2. Tab **"Files"** → `/home/buddyskincare/websitemypham/`
3. **Upload file `app.py`** (đã có Flask endpoint `/api/upload-cccd`)
4. Tab **"Web"** → **Reload** Flask app

### Bước 2: Deploy Django Files
1. Tab **"Files"** → `/home/buddyskincare/websitemypham/`
2. **Upload các files:**
   - `views.py` (có function `upload_cccd_image`)
   - `urls.py` (có route `api/upload-cccd/`)
   - `settings.py` (có Cloudinary config)
   - `models.py` (có TextField cho CCCD URLs)
   - `templates/partner.html` (đã sửa JavaScript)

### Bước 3: Cài đặt Cloudinary
1. Tab **"Consoles"** → New console
2. Chạy: `pip3 install cloudinary==1.36.0`

### Bước 4: Chạy Migration
1. Trong console: `cd /home/buddyskincare/websitemypham`
2. Chạy: `python3 manage.py migrate`

### Bước 5: Reload Apps
1. Tab **"Web"**
2. **Reload** cả Flask và Django apps

## 🎯 KẾT QUẢ MONG ĐỢI:
- ✅ Flask endpoint `/api/upload-cccd` hoạt động
- ✅ Django endpoint `/backend/api/upload-cccd/` hoạt động  
- ✅ Ảnh upload lên Cloudinary thay vì base64
- ✅ CTV application hoạt động bình thường

## 🔍 KIỂM TRA SAU KHI DEPLOY:
1. Test Flask: `curl -X POST https://buddyskincare.vn/api/upload-cccd -F "file=@test.png"`
2. Test Django: `curl -X POST https://buddyskincare.vn/backend/api/upload-cccd/ -F "file=@test.png"`
3. Test trên website: https://buddyskincare.vn/partner

---
**⏰ LÀM NGAY ĐI! Ảnh CTV đang bị lưu base64 thay vì Cloudinary!**