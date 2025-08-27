# BeautySale - Website Bán Mỹ Phẩm Thanh Lý Online

## 📋 Mô tả dự án

BeautySale là một website bán mỹ phẩm thanh lý online hiện đại, được thiết kế với giao diện đẹp mắt và trải nghiệm người dùng tối ưu. Website tập trung vào mô hình bán hàng online với giao hàng toàn quốc, thanh toán khi nhận hàng (COD) và các sản phẩm mỹ phẩm chính hãng với giá tốt nhất thị trường.

## ✨ Tính năng chính

### 🏠 Trang chủ
- **Banner slider** với các ưu đãi nổi bật và call-to-action
- **Thương hiệu nổi tiếng** với logo và thông tin xuất xứ
- **Tìm kiếm nhiều nhất** - các từ khóa phổ biến
- **Sản phẩm mới về** với giá tốt nhất
- **Tại sao chọn BeautySale** - 4 lý do chính
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
- **Đánh giá và bình luận** từ khách hàng
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

### Backend (Dự kiến)
- **Python Flask** - Web framework
- **SQLite/PostgreSQL** - Database
- **Jinja2** - Template engine

## 📁 Cấu trúc dự án

```
websitemypham/
├── app.py                    # Flask application (main)
├── run.py                    # Entry point script
├── setup.py                  # Setup script
├── requirements.txt          # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css          # Custom CSS styles
│   ├── js/
│   │   └── main.js           # JavaScript functionality
│   └── image/                # Product images
├── templates/
│   ├── base.html             # Base template
│   ├── header.html           # Header component
│   ├── footer.html           # Footer component
│   ├── index.html            # Homepage
│   ├── products.html         # Product listing page
│   └── product-detail.html   # Product detail page
├── beautysale_env/           # Virtual environment
├── run.sh                    # Unix/Linux/Mac run script
├── run.bat                   # Windows run script
└── README.md                 # Project documentation
```

## 🚀 Cách chạy dự án

### Yêu cầu hệ thống
- Python 3.7+
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

4. **Chạy website**
   ```bash
   python run.py
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

### Phase 2 (Tương lai)
- 🔄 Backend API với Flask
- 🔄 Database integration
- 🔄 User authentication
- 🔄 Shopping cart functionality
- 🔄 Payment integration
- 🔄 Admin panel

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

- **Email**: info@myphamthanhly.com
- **Hotline**: 1900-1234
- **Website**: https://myphamthanhly.com

## 🙏 Cảm ơn

Cảm ơn bạn đã quan tâm đến dự án BeautySale! Chúng tôi hy vọng website này sẽ mang lại trải nghiệm mua sắm tuyệt vời cho khách hàng. 