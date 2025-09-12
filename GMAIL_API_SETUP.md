# Gmail API Setup Guide

## 📧 Hướng dẫn thiết lập Gmail API để lấy dữ liệu email

### **Bước 1: Tạo Gmail API Credentials**

1. **Truy cập Google Cloud Console:**
   - Đi đến: https://console.cloud.google.com/
   - Chọn project: `buddyskincare`

2. **Bật Gmail API:**
   - Vào "APIs & Services" > "Library"
   - Tìm "Gmail API"
   - Click "Enable"

3. **Tạo Service Account:**
   - Vào "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Tên: `gmail-analytics-service`
   - Description: `Service account for Gmail analytics`

4. **Download Credentials:**
   - Click vào Service Account vừa tạo
   - Vào tab "Keys"
   - Click "Add Key" > "Create new key"
   - Chọn "JSON"
   - Download file và đổi tên thành `gmail-credentials.json`

### **Bước 2: Cấp quyền cho Gmail**

1. **Cấp quyền cho Service Account:**
   - Email Service Account: `gmail-analytics-service@buddyskincare.iam.gserviceaccount.com`
   - Cấp quyền "Viewer" cho Gmail: `buddyskincarevn@gmail.com`

2. **Domain-wide Delegation (nếu cần):**
   - Trong Service Account, bật "Enable Google Workspace Domain-wide Delegation"
   - Thêm scope: `https://www.googleapis.com/auth/gmail.readonly`

### **Bước 3: Cài đặt Dependencies**

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### **Bước 4: Cấu hình File**

1. **Đặt file credentials:**
   - Copy `gmail-credentials.json` vào thư mục gốc của project
   - Đảm bảo file có quyền đọc

2. **Test kết nối:**
   - Chạy server Flask
   - Truy cập: `/admin/email-analytics`
   - Kiểm tra console logs

### **Bước 5: Dữ liệu sẽ được lấy**

- **Tổng Email Gửi**: Từ Gmail `buddyskincarevn@gmail.com`
- **Email theo Campaign**: Flash Sale, Lucky Game, Other
- **Thời gian**: Theo date range được chọn
- **Trạng thái**: Sent, Delivered, Bounced

### **Troubleshooting**

1. **Lỗi "Credentials not found":**
   - Kiểm tra file `gmail-credentials.json` có trong thư mục gốc
   - Kiểm tra quyền đọc file

2. **Lỗi "Permission denied":**
   - Kiểm tra Service Account có quyền truy cập Gmail
   - Kiểm tra Gmail API đã được bật

3. **Lỗi "API not installed":**
   - Chạy: `pip install google-api-python-client`

### **Kết quả**

Sau khi thiết lập thành công:
- **Tổng Email Gửi** sẽ hiển thị dữ liệu thật từ Gmail
- **Email theo Campaign** sẽ được phân loại tự động
- **Real-time data** sẽ được cập nhật trong admin panel

---

**Lưu ý:** Dữ liệu Gmail chỉ hiển thị khi có file `gmail-credentials.json` hợp lệ.