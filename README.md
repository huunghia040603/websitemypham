# BuddySkincare - Website Bán Mỹ Phẩm

## 📋 Mô tả dự án

BuddySkincare là website bán mỹ phẩm với giao diện hiện đại, tối ưu UX và quy trình đặt hàng hoàn chỉnh (giỏ hàng, thanh toán COD/chuyển khoản, hoá đơn qua email, thông báo đơn hàng mới cho admin).

## ✨ Tính năng chính

### 🏠 Trang chủ
- **Banner slider** với các ưu đãi nổi bật và call-to-action
- **Thương hiệu nổi tiếng** với logo và thông tin xuất xứ
- **Tìm kiếm nhiều nhất** - các từ khóa phổ biến
- **Sản phẩm mới về** với giá tốt nhất
- **Tại sao chọn Buddyskicare** - 4 lý do chính
- **Thống kê ấn tượng** - số liệu về khách hàng và dịch vụ
- **Testimonials** từ khách hàng online
- **Blog làm đẹp** - bài viết hữu ích
- **Newsletter subscription** để nhận thông báo khuyến mãi
- **Floating action buttons** - liên hệ nhanh và scroll to top

### 🛍️ Trang sản phẩm
- **Bộ lọc đa tiêu chí**: Danh mục, thương hiệu, giá, giảm giá
- **Sắp xếp linh hoạt**: Mới nhất, giá, bán chạy, giảm giá
- **Hiển thị dạng lưới** responsive
- **Phân trang** thân thiện
- **Quick view** và thêm vào giỏ hàng nhanh

### 📦 Trang chi tiết sản phẩm
- **Gallery ảnh** với thumbnail
- **Thông tin chi tiết** sản phẩm
- **Yêu thích (Wishlist)** đồng bộ localStorage (trang list, flash sale, chi tiết)
- **Sản phẩm liên quan**
- **Modal viết đánh giá**

### 🎨 Giao diện
- **Responsive design** cho mọi thiết bị
- **Modern UI/UX** với Bootstrap 5
- **Animations** mượt mà
- **Color scheme** chuyên nghiệp
- **Typography** dễ đọc

## 🛠️ Công nghệ sử dụng

### Frontend
- **HTML5** - Cấu trúc trang web
- **CSS3** - Styling và animations
- **JavaScript (ES6+)** - Tương tác và logic
- **Bootstrap 5** - Framework UI
- **Font Awesome** - Icons
- **Google Fonts** - Typography

### Backend
- **Python Flask** - Web framework
- **Jinja2** - Template engine
- **requests** - Gọi API tới `https://buddyskincare.pythonanywhere.com`
- **smtplib** - Gửi email (Gmail SMTP)
- **cloudinary** - Lưu ảnh chuyển khoản

## 📁 Cấu trúc dự án (rút gọn)

```
websitemypham/
├── app.py                    # Ứng dụng Flask (routes, APIs, email)
├── run.py                    # Entry point script
├── setup.py                  # Setup script
├── requirements.txt          # Python dependencies
├── .env                      # Biến môi trường (SMTP, ADMIN_EMAIL, ...)
├── static/
│   ├── css/
│   │   └── style.css          # Custom CSS styles
│   ├── js/
│   │   ├── main.js           # Toàn bộ logic frontend (cart/checkout/wishlist...)
│   │   └── order-notification.js # Gửi thông báo đơn hàng mới (client)
│   └── image/                # Product images
├── templates/
│   ├── base.html             # Base template
│   ├── header.html           # Header component
│   ├── footer.html           # Footer component
│   ├── index.html            # Homepage
│   ├── products.html         # Product listing page
│   └── product-detail.html   # Product detail page
│   └── emails/
│       ├── invoice_email.html            # Mẫu email hoá đơn
│       └── new_order_notification.html   # Mẫu email thông báo đơn hàng mới
├── beautysale_env/           # Virtual environment
├── run.sh                    # Unix/Linux/Mac run script
├── run.bat                   # Windows run script
└── README.md                 # Project documentation
```

## 🚀 Cách chạy dự án

### Yêu cầu hệ thống
- Python 3.10+
- Web browser hiện đại
- Git (để clone repository)

### Cài đặt và chạy

#### Phương pháp 1: Tự động setup (Khuyến nghị)

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd websitemypham
   ```

2. **Chạy setup script**
   ```bash
   # Windows
   python setup.py
   
   # macOS/Linux
   python3 setup.py
   ```

3. **Chạy website**
   ```bash
   # Windows - Double-click file run.bat
   # Hoặc mở Command Prompt và chạy:
   run.bat
   
   # macOS/Linux
   ./run.sh
   ```

#### Phương pháp 2: Thủ công

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd websitemypham
   ```

2. **Tạo môi trường ảo**
   ```bash
   # Windows
   python -m venv beautysale_env
   beautysale_env\Scripts\activate
   
   # macOS/Linux
   python3 -m venv beautysale_env
   source beautysale_env/bin/activate
   ```

3. **Cài đặt dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Tạo file .env**
   ```bash
   cp .env.example .env  # nếu có; hoặc tạo thủ công theo mục bên dưới
   ```

5. **Chạy website**
   ```bash
   # Cách 1
   python app.py
   # Cách 2
   ./run.sh
   ```

5. **Truy cập website**
   ```
   http://localhost:8000
   ```

### 📱 Các trang chính
- **Trang chủ**: http://localhost:8000/
- **Sản phẩm**: http://localhost:8000/products
- **Chi tiết sản phẩm**: http://localhost:8000/product/1
- **Giỏ hàng**: http://localhost:8000/cart
- **Thanh toán**: http://localhost:8000/checkout

## 📱 Responsive Design

Website được thiết kế responsive cho các thiết bị:
- **Desktop** (1200px+)
- **Tablet** (768px - 1199px)
- **Mobile** (< 768px)

## 🎯 Tính năng tương tác

### JavaScript Features
- **Countdown timer** cho flash sale
- **Add to cart** với animation
- **Image gallery** với thumbnail switching
- **Star rating** system
- **Newsletter subscription** với validation
- **Scroll to top** button
- **Mobile menu** enhancements
- **Product filtering** (demo)
- **Smooth scrolling** animations

### CSS Animations
- **Hover effects** cho product cards
- **Fade-in animations** khi scroll
- **Loading animations** cho buttons
- **Transform effects** cho interactive elements

## 🎨 Design System

### Color Palette
- **Primary**: #007bff (Blue)
- **Secondary**: #6c757d (Gray)
- **Success**: #28a745 (Green)
- **Danger**: #dc3545 (Red)
- **Warning**: #ffc107 (Yellow)
- **Info**: #17a2b8 (Cyan)

### Typography
- **Font Family**: Inter (Google Fonts)
- **Headings**: Bold weights (600-700)
- **Body**: Regular weight (400)
- **Small text**: Light weight (300)

## 🧩 Tích hợp & API

- Nguồn dữ liệu: `API_BASE_URL = https://buddyskincare.pythonanywhere.com`
- Các route quan trọng (Flask):
  - Trang chủ: `/`
  - Danh sách SP: `/products`
  - Chi tiết SP: `/product/<id>`
  - Giỏ hàng: `/cart`
  - Thanh toán: `/checkout`
  - Admin: `/admin`, `/admin/orders`, `/admin/products`, ...
  - In hoá đơn: `/admin/orders/<order_id>/invoice`
  - Gửi hoá đơn email: `POST /admin/orders/<order_id>/invoice/email`
  - Upload ảnh chuyển khoản: `POST /api/upload-bank-transfer`
  - Gửi thông báo đơn hàng mới: `POST /api/send-new-order-notification`

## ✉️ Cấu hình Email (SMTP)

Ứng dụng dùng Gmail SMTP. Khuyến nghị dùng App Password.

Biến môi trường trong file `.env`:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASS=your_app_password
SMTP_SENDER=your@gmail.com
ADMIN_EMAIL=admin@yourdomain.com
```

Ghi chú:
- Nếu thiếu `SMTP_USER/SMTP_PASS`, hệ thống sẽ tự lưu HTML email vào thư mục `sent_emails/` và vẫn trả về 200 để không làm gián đoạn UX.
- Có sẵn route preview mẫu email để xem nhanh trên trình duyệt:
  - Hoá đơn: `/templates/emails/invoice_email.html?order_id=<id>` (hoặc dữ liệu demo)
  - Thông báo đơn mới: `/templates/emails/new_order_notification.html?order_id=<id>` (hoặc dữ liệu demo)

## 🔔 Tự động gửi thông báo đơn hàng mới cho Admin

- Sau khi tạo đơn hàng thành công (client gọi), sẽ gửi `POST /api/send-new-order-notification` với JSON:
```json
{ "order_id": 123 }
```
- Server sẽ:
  - Lấy chi tiết đơn `order_id`
  - Lấy danh sách các đơn chưa xác nhận
  - Render email `templates/emails/new_order_notification.html`
  - Gửi tới `ADMIN_EMAIL` qua SMTP (hoặc lưu file fallback)

Client helper: `static/js/order-notification.js` cung cấp `notifyAdminNewOrder(orderId)` để tích hợp sau khi đặt hàng thành công.

## 🛒 Quy trình Checkout (tóm tắt)

- Lưu giỏ hàng, voucher, phương thức thanh toán vào localStorage
- Tạo đơn hàng (gọi API PythonAnywhere)
- Hiển thị modal thành công (`orderSuccessModal`)
- Xoá giỏ hàng local, điều hướng về `/`
- Gọi `notifyAdminNewOrder(orderId)` để báo Admin

## 📊 Dữ liệu demo

Website hiện tại sử dụng dữ liệu demo bao gồm:
- **6 danh mục sản phẩm** chính
- **12+ sản phẩm** với thông tin chi tiết
- **Đánh giá khách hàng** mẫu
- **Flash sale** với countdown timer

## 🔮 Roadmap

### Phase 1 (Hiện tại)
- ✅ Giao diện frontend hoàn chỉnh
- ✅ Responsive design
- ✅ Interactive features
- ✅ Demo data

### Phase 2 (Tương lai gần)
- Hoàn thiện xác thực người dùng (đăng ký/đăng nhập, hồ sơ)
- Lịch sử đơn hàng cho khách
- Đánh giá sản phẩm thực tế
- Tối ưu hiệu năng trang `/products` (pagination/SSR/cache)

### Phase 3 (Nâng cao)
- 🔄 Real-time notifications
- 🔄 Chat support
- 🔄 Advanced search
- 🔄 Product recommendations
- 🔄 Analytics dashboard

## 🤝 Đóng góp

Để đóng góp vào dự án:

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📄 License

Dự án này được phát hành dưới MIT License. Xem file `LICENSE` để biết thêm chi tiết.

## 📞 Liên hệ

- **Email**: buddyskincarevn@gmail.com
- **Hotline**: 0987 789 274
- **Website**: https://www.buddyskincare.com

## 🙏 Cảm ơn

Cảm ơn bạn đã quan tâm đến dự án BeautySale! Chúng tôi hy vọng website này sẽ mang lại trải nghiệm mua sắm tuyệt vời cho khách hàng. 