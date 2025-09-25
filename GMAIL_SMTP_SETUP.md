# Gmail SMTP Setup Guide

## 📧 Hướng dẫn thiết lập Gmail SMTP để gửi email

### **Bước 1: Tạo Gmail App Password**

1. **Truy cập Google Account:**
   - Đi đến: https://myaccount.google.com/
   - Đăng nhập bằng tài khoản: `buddyskincarevn@gmail.com`

2. **Bật 2-Step Verification:**
   - Vào "Security" > "2-Step Verification"
   - Bật 2-Step Verification nếu chưa có

3. **Tạo App Password:**
   - Vào "Security" > "App passwords"
   - Chọn "Mail" và "Other (Custom name)"
   - Nhập tên: `BuddySkincare Production`
   - Copy App Password (16 ký tự)

### **Bước 2: Cấu hình trên Production Server**

1. **SSH vào server:**
   ```bash
   ssh buddyskincare@buddyskincare.pythonanywhere.com
   ```

2. **Set environment variable:**
   ```bash
   export GMAIL_APP_PASSWORD="your-16-character-app-password"
   ```

3. **Thêm vào .bashrc để persistent:**
   ```bash
   echo 'export GMAIL_APP_PASSWORD="your-16-character-app-password"' >> ~/.bashrc
   source ~/.bashrc
   ```

4. **Restart web app:**
   - Vào PythonAnywhere dashboard
   - Reload web app

### **Bước 3: Test gửi email**

1. **Test từ admin panel:**
   - Vào `/admin/orders`
   - Chọn một đơn hàng
   - Click "Gửi hóa đơn qua email"

2. **Kiểm tra logs:**
   - Vào "Tasks" > "Error log"
   - Tìm message: `✅ Email sent successfully to ... via Gmail SMTP`

### **Troubleshooting**

#### **Lỗi: "Gmail App Password not configured"**
- Kiểm tra environment variable: `echo $GMAIL_APP_PASSWORD`
- Đảm bảo đã set đúng App Password

#### **Lỗi: "Authentication failed"**
- Kiểm tra App Password có đúng 16 ký tự không
- Đảm bảo 2-Step Verification đã được bật

#### **Lỗi: "Connection refused"**
- Kiểm tra firewall/network
- Thử port 465 thay vì 587

### **Fallback Methods**

Nếu Gmail SMTP không hoạt động, hệ thống sẽ tự động thử:

1. **Gmail API** (nếu có credentials)
2. **Regular SMTP** (nếu có SMTP_USER/SMTP_PASS)
3. **Save to file** (fallback cuối cùng)

### **Security Notes**

- App Password chỉ dùng cho production server
- Không commit App Password vào code
- Sử dụng environment variables
- Thay đổi App Password định kỳ