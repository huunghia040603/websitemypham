# Hướng Dẫn Force Indexing Google Search Console

## 🎯 Các bước thực hiện:

### 1. Sử dụng URL Inspection Tool
1. Vào Google Search Console
2. Chọn "Kiểm tra URL" (URL Inspection)
3. Nhập URL: `https://buddyskincare.vn/`
4. Click "Kiểm tra"
5. Nếu thấy "URL không có trong Google", click "Yêu cầu lập chỉ mục"

### 2. Resubmit Sitemap
1. Vào "Sơ đồ trang web" (Sitemaps)
2. Xóa sitemap cũ nếu có
3. Thêm mới: `https://buddyskincare.vn/sitemap_index.xml`
4. Click "Gửi"

### 3. Kiểm tra Coverage Report
1. Vào "Lập chỉ mục" > "Trang"
2. Chờ 24-48 giờ để data cập nhật
3. Kiểm tra "Trang hợp lệ" và "Lỗi"

## 🔧 Troubleshooting:

### Nếu vẫn không index:
1. **Kiểm tra noindex tags:**
   - Đảm bảo không có `<meta name="robots" content="noindex">`
   - Kiểm tra trong source code

2. **Kiểm tra canonical URLs:**
   - Đảm bảo canonical trỏ đúng URL
   - Tránh duplicate content

3. **Kiểm tra internal links:**
   - Tạo internal links đến trang chủ
   - Sử dụng anchor text có từ khóa

4. **Tạo backlinks:**
   - Submit lên Google My Business
   - Share trên social media
   - Tạo profile trên các directory

## 📊 Monitoring:

### Sau 24-48 giờ:
- Kiểm tra lại URL Inspection
- Xem Coverage report
- Monitor Search Performance

### Nếu vẫn không work:
- Kiểm tra technical issues
- Contact Google Support
- Consider sitemap structure changes