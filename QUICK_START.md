# 🚀 Quick Start - BeautySale Website

## ⚡ Chạy nhanh trong 3 bước

### 1️⃣ Setup môi trường
```bash
# Clone repository (nếu chưa có)
git clone <repository-url>
cd websitemypham

# Chạy setup tự động
python setup.py
```

### 2️⃣ Chạy website
```bash
# Windows
run.bat

# macOS/Linux
./run.sh
```

### 3️⃣ Truy cập website
```
http://localhost:8000
```

## 🎯 Tính năng demo

### 🏠 Trang chủ
- **Flash sale** với countdown timer
- **Danh mục sản phẩm** với icons
- **Sản phẩm nổi bật**
- **Newsletter subscription**

### 🛍️ Trang sản phẩm
- **Bộ lọc đa tiêu chí**: Danh mục, thương hiệu, giá, giảm giá
- **Sắp xếp linh hoạt**: Mới nhất, giá, bán chạy
- **Responsive grid** layout

### 📦 Trang chi tiết sản phẩm
- **Image gallery** với thumbnails
- **Thông tin chi tiết** sản phẩm
- **Đánh giá và bình luận**
- **Sản phẩm liên quan**

### ⚡ API Endpoints
- `POST /api/add-to-cart` - Thêm vào giỏ hàng
- `POST /api/newsletter` - Đăng ký newsletter
- `GET /api/search` - Tìm kiếm sản phẩm

## 🔧 Troubleshooting

### Lỗi "ModuleNotFoundError: No module named 'flask'"
```bash
# Kích hoạt môi trường ảo
# Windows
beautysale_env\Scripts\activate

# macOS/Linux
source beautysale_env/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### Lỗi "Port 8000 is already in use"
```bash
# Thay đổi port trong file run.py
app.run(debug=True, host='0.0.0.0', port=8001)
```

### Lỗi "Permission denied" trên macOS/Linux
```bash
# Cấp quyền thực thi
chmod +x run.sh
chmod +x setup.py
```

## 📱 Test trên mobile

1. **Tìm IP của máy tính**
   ```bash
   # Windows
   ipconfig
   
   # macOS/Linux
   ifconfig
   ```

2. **Truy cập từ mobile**
   ```
   http://[IP_ADDRESS]:8000
   ```

## 🛠️ Development

### Cấu trúc project
```
websitemypham/
├── app.py                # Flask application (main)
├── run.py                # Entry point
├── setup.py              # Setup script
├── requirements.txt      # Dependencies
├── templates/
│   ├── base.html         # Template cơ sở
│   ├── index.html        # Trang chủ
│   ├── products.html     # Danh sách sản phẩm
│   └── product-detail.html # Chi tiết sản phẩm
├── static/
│   ├── css/style.css     # Custom styles
│   └── js/main.js        # JavaScript
└── beautysale_env/       # Virtual environment
```

### Thêm sản phẩm mới
1. Mở file `app.py`
2. Thêm vào list `products_data`
3. Restart server

### Thay đổi giao diện
1. Chỉnh sửa file trong `templates/`
2. Refresh browser (auto-reload enabled)

## 🎨 Customization

### Thay đổi màu sắc
Chỉnh sửa file `static/css/style.css`:
```css
:root {
    --bs-primary: #your-color;
}
```

### Thêm sản phẩm
Chỉnh sửa file `templates/index.py`:
```python
products_data.append({
    'id': len(products_data) + 1,
    'name': 'Tên sản phẩm',
    'brand': 'Thương hiệu',
    # ... thêm các thuộc tính khác
})
```

## 📞 Hỗ trợ

- **Email**: info@myphamthanhly.com
- **Hotline**: 1900-1234
- **Documentation**: README.md

---

**Happy coding! 🎉** 