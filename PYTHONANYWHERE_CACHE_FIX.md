# 🔄 FIX PYTHONANYWHERE CACHE - CODE KHÔNG CẬP NHẬT

## ❌ VẤN ĐỀ:
- Code đã thay đổi nhưng website không cập nhật
- Reload nhiều lần vẫn không có tác dụng
- PythonAnywhere có cache mạnh

## ✅ GIẢI PHÁP TỪNG BƯỚC:

### Bước 1: Kiểm tra Files đã upload đúng chưa
1. Vào PythonAnywhere: https://www.pythonanywhere.com/user/budduskincarevn/
2. Tab **"Files"** → `/home/buddyskincare/websitemypham/`
3. **Kiểm tra timestamp** của files:
   - `app.py` - phải có timestamp mới nhất
   - `views.py` - phải có timestamp mới nhất
   - `urls.py` - phải có timestamp mới nhất
   - `settings.py` - phải có timestamp mới nhất
   - `models.py` - phải có timestamp mới nhất
   - `templates/partner.html` - phải có timestamp mới nhất

### Bước 2: Force Reload Django App
1. Tab **"Web"**
2. Tìm section **"Django"** (không phải Flask)
3. Click **"Reload"** button
4. **Đợi 30 giây** cho Django reload hoàn tất

### Bước 3: Force Reload Flask App  
1. Tab **"Web"**
2. Tìm section **"Flask"** 
3. Click **"Reload"** button
4. **Đợi 30 giây** cho Flask reload hoàn tất

### Bước 4: Clear Browser Cache
1. **Ctrl + F5** (Windows) hoặc **Cmd + Shift + R** (Mac)
2. Hoặc mở **Incognito/Private window**
3. Test lại website

### Bước 5: Restart Console (nếu cần)
1. Tab **"Consoles"**
2. **Kill** tất cả consoles đang chạy
3. Tạo **new console**
4. Chạy: `cd /home/buddyskincare/websitemypham && python3 manage.py migrate`

### Bước 6: Kiểm tra Logs
1. Tab **"Web"** → **"Error log"**
2. Xem có lỗi gì không
3. Tab **"Web"** → **"Server log"** 
4. Xem Django/Flask có start đúng không

## 🔍 KIỂM TRA CODE ĐÃ CẬP NHẬT:

### Test Flask Endpoint:
```bash
curl -X POST https://buddyskincare.vn/api/upload-cccd -F "file=@test.png"
```

### Test Django Endpoint:
```bash
curl -X POST https://buddyskincare.vn/backend/api/upload-cccd/ -F "file=@test.png"
```

### Test trên Website:
1. Vào: https://buddyskincare.vn/partner
2. Upload ảnh CCCD
3. Check browser console (F12) xem có logs không

## 🚨 NẾU VẪN KHÔNG HOẠT ĐỘNG:

### Option 1: Hard Restart
1. Tab **"Web"** → **"Reload"** cả Flask và Django
2. **Đợi 2-3 phút**
3. Test lại

### Option 2: Check File Permissions
1. Tab **"Files"**
2. Right-click files → **"Properties"**
3. Đảm bảo permissions: **644** cho files, **755** cho folders

### Option 3: Manual File Edit
1. Tab **"Files"** → Edit file trực tiếp trên PythonAnywhere
2. Thêm comment `# UPDATED` vào cuối file
3. Save và reload

## 🎯 DẤU HIỆU THÀNH CÔNG:
- ✅ Flask endpoint trả về JSON thay vì 404
- ✅ Django endpoint trả về JSON thay vì 404  
- ✅ Ảnh upload lên Cloudinary thay vì base64
- ✅ Browser console hiển thị Cloudinary URL

---
**💡 TIP: PythonAnywhere cache rất mạnh, cần reload đúng cách và đợi đủ lâu!**