# Hướng dẫn Deploy lên PythonAnywhere

## Cách 1: Deploy thủ công qua Web Interface

1. **Đăng nhập PythonAnywhere Console:**
   - Vào: https://www.pythonanywhere.com/user/buddyskincarevn/consoles/
   - Chọn "Bash console"

2. **Copy code từ local lên server:**
```bash
# Tạo file mới
nano /home/buddyskincare/websitemypham/static/js/main.js
```

3. **Copy nội dung từ file local `static/js/main.js`** (dòng 863):
```javascript
const uploadResponse = await fetch('/backend/api/upload-bank-transfer/', {
    method: 'POST',
    body: uploadFormData
});
```

4. **Reload web app:**
   - Vào: https://www.pythonanywhere.com/user/buddyskincarevn/webapps/#tab_id_buddyskincare_vn
   - Click nút "Reload"

## Cách 2: Sử dụng Git (Khuyến nghị)

1. **Push code lên GitHub:**
```bash
git add .
git commit -m "Fix bank transfer upload endpoint"
git push origin main
```

2. **Pull code trên PythonAnywhere:**
```bash
cd /home/buddyskincare/websitemypham
git pull origin main
```

3. **Reload web app**

## Cách 3: Upload file qua Web Interface

1. Vào: https://www.pythonanywhere.com/user/buddyskincarevn/files/
2. Upload file `static/js/main.js` lên thư mục `/home/buddyskincare/websitemypham/static/js/`
3. Reload web app

## Kiểm tra sau khi deploy:

1. **Test endpoint:**
   - Vào: https://buddyskincare.vn/backend/api/upload-bank-transfer/
   - Phải trả về method not allowed (405) thay vì 404

2. **Test upload:**
   - Vào trang checkout
   - Chọn "Chuyển khoản ngân hàng"
   - Upload ảnh
   - Đặt hàng

## Files cần thay đổi:

1. `static/js/main.js` - dòng 863: đổi từ `/api/upload-bank-transfer` thành `/backend/api/upload-bank-transfer/`
2. `app.py` - đã xóa duplicate endpoint
3. `views.py` - Django endpoint đã sẵn sàng