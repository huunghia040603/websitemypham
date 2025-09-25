# 🔧 Fix Email trên Production - Hướng dẫn chi tiết

## 🚨 Vấn đề hiện tại
- Trên production (buddyskincare.vn), nút "Gửi hóa đơn" vẫn lưu file thay vì gửi email
- Local development hoạt động bình thường
- Code mới chưa được deploy lên production

## 📋 Các bước khắc phục

### **Bước 1: Deploy code mới lên production**

```bash
# Chạy script deploy
chmod +x deploy_to_production.sh
./deploy_to_production.sh
```

Hoặc upload thủ công:
```bash
scp app.py buddyskincare@buddyskincare.pythonanywhere.com:/home/buddyskincare/websitemypham/
scp test_email.py buddyskincare@buddyskincare.pythonanywhere.com:/home/buddyskincare/websitemypham/
```

### **Bước 2: Tạo Gmail App Password**

1. **Truy cập Google Account:**
   - Đi đến: https://myaccount.google.com/
   - Đăng nhập: `buddyskincarevn@gmail.com`

2. **Bật 2-Step Verification:**
   - Security > 2-Step Verification
   - Bật nếu chưa có

3. **Tạo App Password:**
   - Security > App passwords
   - Chọn "Mail" > "Other (Custom name)"
   - Tên: `BuddySkincare Production`
   - **Copy 16 ký tự App Password**

### **Bước 3: Cấu hình trên Production Server**

```bash
# SSH vào production server
ssh buddyskincare@buddyskincare.pythonanywhere.com

# Set Gmail App Password (thay YOUR_APP_PASSWORD)
export GMAIL_APP_PASSWORD="YOUR_APP_PASSWORD"

# Thêm vào .bashrc để persistent
echo 'export GMAIL_APP_PASSWORD="YOUR_APP_PASSWORD"' >> ~/.bashrc
source ~/.bashrc

# Kiểm tra cấu hình
cd /home/buddyskincare/websitemypham
python3 check_production_status.py
```

### **Bước 4: Test email configuration**

```bash
# Test gửi email
python3 test_email.py
```

Nếu thành công, bạn sẽ thấy:
```
✅ Email sent successfully to huunghia040623@gmail.com via Gmail SMTP
```

### **Bước 5: Reload Web App**

1. Vào PythonAnywhere dashboard
2. Vào "Web" tab
3. Click "Reload" button

### **Bước 6: Test từ Admin Panel**

1. Vào: https://buddyskincare.vn/admin/orders
2. Chọn một đơn hàng
3. Click "Gửi hóa đơn"
4. Nhập email và gửi

**Kết quả mong đợi:**
- ✅ Email được gửi thành công
- ✅ Thông báo: "Đã gửi hóa đơn thành công"
- ❌ Không còn thông báo: "Đã lưu file"

## 🔍 Troubleshooting

### **Lỗi: "Gmail App Password not configured"**
```bash
# Kiểm tra environment variable
echo $GMAIL_APP_PASSWORD

# Nếu trống, set lại
export GMAIL_APP_PASSWORD="your-16-character-app-password"
```

### **Lỗi: "Authentication failed"**
- Kiểm tra App Password có đúng 16 ký tự
- Đảm bảo 2-Step Verification đã bật
- Thử tạo App Password mới

### **Lỗi: "Connection refused"**
- Kiểm tra network/firewall
- Thử port 465 thay vì 587

### **Vẫn lưu file thay vì gửi email**
1. Kiểm tra code đã được deploy chưa:
   ```bash
   python3 check_production_status.py
   ```

2. Kiểm tra error log:
   - Vào PythonAnywhere dashboard
   - "Tasks" > "Error log"
   - Tìm lỗi liên quan đến email

3. Test email trực tiếp:
   ```bash
   python3 test_email.py
   ```

## 📊 Kiểm tra trạng thái

Chạy script kiểm tra:
```bash
python3 check_production_status.py
```

Kết quả mong đợi:
```
✅ Environment configured
✅ Code updated  
✅ Gmail credentials
🎉 Email should work! Try sending an invoice email.
```

## 🎯 Kết quả cuối cùng

Sau khi hoàn thành tất cả các bước:

1. **Nút "Gửi hóa đơn"** sẽ gửi email thật
2. **Không còn lưu file** trong sent_emails/
3. **Thông báo thành công** khi gửi email
4. **Email được gửi** đến địa chỉ khách hàng

## 📞 Hỗ trợ

Nếu vẫn gặp vấn đề:
1. Kiểm tra error log trên PythonAnywhere
2. Chạy `python3 test_email.py` để test
3. Kiểm tra Gmail App Password có đúng không
4. Đảm bảo code mới đã được deploy