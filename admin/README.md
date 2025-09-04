# Admin Dashboard - BuddySkincare

## Tổng quan
Hệ thống admin dashboard cho website BuddySkincare, cho phép quản lý sản phẩm và đơn hàng một cách hiệu quả.

## Tính năng chính

### 1. Dashboard Tổng quan
- **URL**: `/admin`
- **Chức năng**: Hiển thị thống kê tổng quan về sản phẩm, đơn hàng, flash sale
- **Thông tin hiển thị**:
  - Tổng số sản phẩm
  - Tổng số đơn hàng
  - Số sản phẩm flash sale
  - Số đơn hàng chờ xử lý
  - Danh sách đơn hàng gần đây

### 2. Quản lý Sản phẩm Mới
- **URL**: `/admin/products/new`
- **Chức năng**: Quản lý các sản phẩm mới 100%
- **Tính năng**:
  - Xem danh sách sản phẩm mới
  - Tìm kiếm và lọc theo thương hiệu, danh mục
  - Chỉnh sửa thông tin sản phẩm
  - Cập nhật giá, số lượng tồn kho
  - Thay đổi trạng thái sản phẩm

### 3. Quản lý Sản phẩm Đã Sử Dụng
- **URL**: `/admin/products/used`
- **Chức năng**: Quản lý các sản phẩm đã qua sử dụng
- **Tính năng**: Tương tự như sản phẩm mới

### 4. Quản lý Flash Sale
- **URL**: `/admin/products/flash-sale`
- **Chức năng**: Quản lý các sản phẩm đang flash sale
- **Tính năng**:
  - Xem danh sách sản phẩm flash sale
  - Thêm flash sale cho sản phẩm
  - Chỉnh sửa tỷ lệ giảm giá
  - Xóa flash sale
  - Lọc theo mức giảm giá, thương hiệu, tồn kho

### 5. Quản lý Đơn Hàng
- **URL**: `/admin/orders`
- **Chức năng**: Quản lý toàn bộ đơn hàng của khách hàng
- **Tính năng**:
  - Xem danh sách tất cả đơn hàng
  - Tìm kiếm theo ID, tên khách hàng
  - Lọc theo trạng thái, xác nhận, ngày tạo
  - Xem chi tiết đơn hàng
  - Xác nhận đơn hàng (tự động giảm tồn kho)
  - Hủy đơn hàng (tự động khôi phục tồn kho)
  - Chỉnh sửa thông tin đơn hàng

## API Endpoints

### Orders API
- `GET /admin/api/orders` - Lấy danh sách đơn hàng
- `GET /admin/api/orders/{id}` - Lấy chi tiết đơn hàng
- `PATCH /admin/api/orders/{id}` - Cập nhật đơn hàng
- `POST /admin/api/orders/{id}/confirm` - Xác nhận đơn hàng
- `POST /admin/api/orders/{id}/cancel` - Hủy đơn hàng

### Products API
- `PATCH /admin/api/products/{id}` - Cập nhật sản phẩm

## Logic Xử Lý Đơn Hàng

### Xác nhận đơn hàng (`is_confirmed = true`)
1. Cập nhật trạng thái xác nhận của đơn hàng
2. Tự động giảm `stock_quantity` của từng sản phẩm trong đơn hàng
3. Không thể thay đổi `status` khi đã xác nhận

### Hủy đơn hàng (`status = cancelled`)
1. Nếu đơn hàng đã được xác nhận trước đó:
   - Tự động khôi phục `stock_quantity` của từng sản phẩm
2. Cập nhật `status` thành `cancelled`

### Ràng buộc
- Khi `is_confirmed = false`: Không thể thay đổi `status`
- Khi `is_confirmed = true`: Có thể thay đổi `status` nhưng không thể hủy xác nhận

## Cấu trúc File

```
admin/
├── templates/
│   ├── admin_base.html          # Template cơ sở
│   ├── admin_dashboard.html     # Dashboard chính
│   ├── admin_products_new.html  # Quản lý sản phẩm mới
│   ├── admin_products_used.html # Quản lý sản phẩm đã sử dụng
│   ├── admin_products_flash_sale.html # Quản lý flash sale
│   └── admin_orders.html        # Quản lý đơn hàng
├── static/
│   ├── css/
│   │   └── admin.css           # CSS cho admin
│   └── js/
│       └── admin.js            # JavaScript cho admin
└── README.md                   # Tài liệu này
```

## Cách sử dụng

1. **Truy cập Admin Dashboard**:
   ```
   http://localhost:8000/admin
   ```

2. **Quản lý sản phẩm**:
   - Chọn loại sản phẩm từ menu dropdown
   - Sử dụng bộ lọc để tìm kiếm
   - Click "Chỉnh sửa" để cập nhật thông tin

3. **Quản lý đơn hàng**:
   - Xem danh sách đơn hàng
   - Click "Xem chi tiết" để xem thông tin đầy đủ
   - Sử dụng nút "Xác nhận" hoặc "Hủy" để thay đổi trạng thái

## Lưu ý kỹ thuật

- Tất cả dữ liệu được lấy từ PythonAnywhere API
- Hệ thống tự động cập nhật tồn kho khi xác nhận/hủy đơn hàng
- Giao diện responsive, hỗ trợ mobile
- Sử dụng Bootstrap 5 và Font Awesome icons
- JavaScript ES6+ với async/await

## Bảo mật

- Cần thêm authentication/authorization
- Validate dữ liệu đầu vào
- Rate limiting cho API calls
- CSRF protection

## Phát triển tiếp

- [ ] Thêm authentication system
- [ ] Export dữ liệu ra Excel
- [ ] Thống kê chi tiết hơn
- [ ] Quản lý người dùng
- [ ] Logs và audit trail
- [ ] Backup và restore dữ liệu