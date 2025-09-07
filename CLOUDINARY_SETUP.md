# Cloudinary Setup Guide

## Cấu hình Cloudinary cho Upload Ảnh Chuyển Khoản

### 1. Tạo tài khoản Cloudinary
1. Truy cập [https://cloudinary.com](https://cloudinary.com)
2. Đăng ký tài khoản miễn phí
3. Xác nhận email

### 2. Lấy thông tin API
1. Đăng nhập vào Cloudinary Dashboard
2. Vào phần "Dashboard" 
3. Copy các thông tin sau:
   - **Cloud Name**: `deoknys7k` (đã có sẵn)
   - **API Key**: Lấy từ Dashboard
   - **API Secret**: Lấy từ Dashboard

### 3. Cấu hình đã được cập nhật trong app.py
```python
# Cloudinary configuration
cloudinary.config(
    cloud_name="deoknys7k",
    api_key="657643869681298",
    api_secret="K8pAAJPmIUcO7ThRnfOtJx7Ntwg"
)
```

### 4. Cài đặt thư viện
```bash
pip install cloudinary==1.36.0
```

### 5. Test Upload
1. Chạy server: `python app.py`
2. Truy cập: `http://localhost:8000/test_optimized_upload.html`
3. Chọn ảnh và test upload với tối ưu hóa

### 6. Tính năng
- **Upload tự động**: Khi chọn thanh toán ngân hàng và upload ảnh
- **Preview ảnh**: Hiển thị preview ảnh trước khi upload
- **Lưu vào database**: Đường link ảnh được lưu vào `bank_transfer_image`
- **Hiển thị trong admin**: Admin có thể xem ảnh chuyển khoản trong modal chi tiết
- **Tối ưu hóa ảnh**: Tự động nén và giảm dung lượng ảnh
- **Validation**: Kiểm tra kích thước file (tối đa 10MB) và định dạng

### 7. Cấu trúc thư mục Cloudinary
- **Folder**: `bank_transfers/`
- **Public ID**: `transfer_YYYYMMDD_HHMMSS`
- **Format**: Tự động tối ưu theo định dạng gốc

### 8. Tối ưu hóa ảnh
- **Chất lượng**: `auto:low` - Tự động giảm chất lượng để giảm dung lượng
- **Kích thước**: Giới hạn tối đa 1200x1200px
- **Format**: Tự động chọn WebP nếu browser hỗ trợ
- **Progressive**: Tạo ảnh progressive JPEG để tải nhanh hơn
- **Crop**: `limit` - Giữ nguyên tỷ lệ, chỉ resize nếu vượt quá giới hạn

### 9. Bảo mật
- API Key và Secret nên được lưu trong biến môi trường
- Không commit thông tin API vào Git
- Sử dụng HTTPS trong production

### 10. Giới hạn miễn phí
- **Storage**: 25GB
- **Bandwidth**: 25GB/tháng
- **Transformations**: 25,000/tháng
- **Uploads**: 500/tháng

### 11. Troubleshooting
- **Lỗi 401**: Kiểm tra API Key và Secret
- **Lỗi 400**: Kiểm tra định dạng file (chỉ chấp nhận: PNG, JPG, JPEG, GIF, WEBP)
- **Lỗi upload**: Kiểm tra kết nối internet và kích thước file
 
 
 
 