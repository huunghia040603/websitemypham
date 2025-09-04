from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'buddyskincare_secret_key_2024'

# API URL for PythonAnywhere
API_BASE_URL = 'https://buddyskincare.pythonanywhere.com'

# Dữ liệu danh mục
categories_data = [
    {'name': 'Chăm Sóc Da', 'icon': 'fas fa-spa', 'color': 'text-success', 'count': 80},
    {'name': 'Son Môi', 'icon': 'fas fa-lipstick', 'color': 'text-danger', 'count': 50},
    {'name': 'Kem Nền', 'icon': 'fas fa-palette', 'color': 'text-primary', 'count': 30},
    {'name': 'Trang Điểm Mắt', 'icon': 'fas fa-eye', 'color': 'text-warning', 'count': 40},
    {'name': 'Chăm Sóc Cơ Thể', 'icon': 'fas fa-spa', 'color': 'text-info', 'count': 35},
    {'name': 'Nước Hoa', 'icon': 'fas fa-spray-can', 'color': 'text-secondary', 'count': 25}
]

# Dữ liệu thương hiệu
brands_data = [
    'TheFaceShop', 'Cetaphil', 'Bioderma', 'L\'Oreal Paris', 'Mac Cosmetics', 
    'Estee Lauder', 'Dior', 'Chanel', 'The Ordinary', 'SK-II'
]

# Dữ liệu đánh giá
reviews_data = [
    {
        'id': 1,
        'product_id': 1,
        'user_name': 'Nguyễn Thị Anh',
        'rating': 5,
        'comment': 'Combo nước cân bằng sen hậu giang rất tốt! Da mình sạch và mềm mại hơn hẳn. Mùi hương dễ chịu, không gây kích ứng. Sẽ mua lại!',
        'date': '2024-01-15',
        'images': ['https://via.placeholder.com/80x80/ff6b6b/ffffff?text=IMG', 'https://via.placeholder.com/80x80/ff8e8e/ffffff?text=IMG']
    },
    {
        'id': 2,
        'product_id': 1,
        'user_name': 'Trần Văn Bình',
        'rating': 5,
        'comment': 'Mua tặng vợ, cô ấy rất thích! Sản phẩm chất lượng tốt, giá cả hợp lý. Giao hàng nhanh, đóng gói cẩn thận.',
        'date': '2024-01-10'
    },
    {
        'id': 3,
        'product_id': 2,
        'user_name': 'Lê Thị Cẩm',
        'rating': 5,
        'comment': 'Kem nền chất lượng tốt, che phủ hoàn hảo. Không gây mụn và độ bền cao. Rất hài lòng!',
        'date': '2024-01-12'
    }
]

# Dữ liệu testimonials
testimonials_data = [
    {
        'name': 'Nguyễn Thị Anh',
        'rating': 5,
        'comment': 'Sản phẩm chất lượng tốt, giá cả hợp lý. Giao hàng nhanh và đóng gói cẩn thận. Sẽ mua lại!',
        'avatar': 'https://via.placeholder.com/80x80/ff6b6b/ffffff?text=KH'
    },
    {
        'name': 'Trần Văn Bình',
        'rating': 5,
        'comment': 'Mua son Mac với giá rẻ hơn 50% so với giá gốc. Chất lượng vẫn tốt như mới. Rất hài lòng!',
        'avatar': 'https://via.placeholder.com/80x80/4ecdc4/ffffff?text=KH'
    },
    {
        'name': 'Lê Thị Cẩm',
        'rating': 4,
        'comment': 'Website dễ sử dụng, thanh toán thuận tiện. Sản phẩm đúng như mô tả. Đáng tin cậy!',
        'avatar': 'https://via.placeholder.com/80x80/45b7d1/ffffff?text=KH'
    }
]

@app.route('/')
def index():
    """Trang chủ"""
    import requests
    
    try:
        # Fetch products from API
        api_url = f'{API_BASE_URL}/products/'
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            all_products = response.json()
            print(f"✅ Fetched {len(all_products)} products for homepage")
            
            # Filter flash sale products (có discount > 0)
            flash_sale_products = [p for p in all_products if float(p.get('discount_rate', 0)) > 0][:4]
            
            # Filter featured products (không có discount hoặc discount thấp)
            featured_products = [p for p in all_products if float(p.get('discount_rate', 0)) <= 10][:4]
            
        else:
            print(f"❌ API returned status {response.status_code}")
            flash_sale_products = []
            featured_products = []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching products for homepage: {e}")
        flash_sale_products = []
        featured_products = []
    
    # Tính thời gian flash sale (2 ngày từ hiện tại)
    flash_sale_end = datetime.now() + timedelta(days=2, hours=15, minutes=30, seconds=45)
    
    return render_template('index.html', 
                         categories=categories_data,
                         flash_sale_products=flash_sale_products,
                         featured_products=featured_products,
                         testimonials=testimonials_data,
                         flash_sale_end=flash_sale_end)

@app.route('/products')
def products():
    """Trang danh sách sản phẩm"""
    import requests
    
    try:
        # Fetch products from API
        api_url = f'{API_BASE_URL}/products/'
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            all_products = response.json()
            print(f"✅ Fetched {len(all_products)} products from API")
        else:
            print(f"❌ API returned status {response.status_code}")
            all_products = []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching products from API: {e}")
        all_products = []
    
    # Lấy tham số filter
    category = request.args.get('category')
    brand = request.args.get('brand')
    price_range = request.args.get('price')
    discount = request.args.get('discount')
    sort_by = request.args.get('sort', 'newest')
    condition = request.args.get('condition', 'all')
    
    # Filter sản phẩm
    filtered_products = all_products.copy()
    
    if category:
        filtered_products = [p for p in filtered_products if p.get('category', {}).get('name') == category]
    
    if brand:
        filtered_products = [p for p in filtered_products if p.get('brand_name') == brand]
    
    if condition != 'all':
        filtered_products = [p for p in filtered_products if p.get('status') == condition]
    
    if price_range:
        if price_range == 'under_500k':
            filtered_products = [p for p in filtered_products if (p.get('discounted_price', 0) * 1000) < 500000]
        elif price_range == '500k_1m':
            filtered_products = [p for p in filtered_products if 500000 <= (p.get('discounted_price', 0) * 1000) < 1000000]
        elif price_range == '1m_2m':
            filtered_products = [p for p in filtered_products if 1000000 <= (p.get('discounted_price', 0) * 1000) < 2000000]
        elif price_range == 'over_2m':
            filtered_products = [p for p in filtered_products if (p.get('discounted_price', 0) * 1000) >= 2000000]
    
    if discount:
        if discount == 'over_50':
            filtered_products = [p for p in filtered_products if float(p.get('discount_rate', 0)) >= 50]
        elif discount == '30_50':
            filtered_products = [p for p in filtered_products if 30 <= float(p.get('discount_rate', 0)) < 50]
        elif discount == 'under_30':
            filtered_products = [p for p in filtered_products if float(p.get('discount_rate', 0)) < 30]
    
    # Sort sản phẩm
    if sort_by == 'price_low':
        filtered_products.sort(key=lambda x: x.get('discounted_price', 0) * 1000)
    elif sort_by == 'price_high':
        filtered_products.sort(key=lambda x: x.get('discounted_price', 0) * 1000, reverse=True)
    elif sort_by == 'popular':
        filtered_products.sort(key=lambda x: x.get('sold_quantity', 0), reverse=True)
    elif sort_by == 'discount':
        filtered_products.sort(key=lambda x: float(x.get('discount_rate', 0)), reverse=True)
    else:  # newest
        filtered_products.sort(key=lambda x: x.get('id', 0), reverse=True)
    
    return render_template('products.html',
                         products=filtered_products,
                         categories=categories_data,
                         brands=brands_data,
                         current_condition=condition)

@app.route('/products/new')
def products_new():
    """Trang sản phẩm mới 100%"""
    import requests
    
    try:
        # Fetch products from API
        api_url = f'{API_BASE_URL}/products/'
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            all_products = response.json()
            # Filter products with status 'new'
            filtered_products = [p for p in all_products if p.get('status') == 'new']
        else:
            filtered_products = []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching new products: {e}")
        filtered_products = []
    
    return render_template('products.html',
                         products=filtered_products,
                         categories=categories_data,
                         brands=brands_data,
                         current_condition='new',
                         page_title='Sản Phẩm Mới 100%')

@app.route('/products/used')
def products_used():
    """Trang sản phẩm đã sử dụng"""
    import requests
    
    try:
        # Fetch products from API
        api_url = f'{API_BASE_URL}/products/'
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            all_products = response.json()
            # Filter products that are not 'new'
            filtered_products = [p for p in all_products if p.get('status') != 'new']
        else:
            filtered_products = []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching used products: {e}")
        filtered_products = []
    
    return render_template('products.html',
                         products=filtered_products,
                         categories=categories_data,
                         brands=brands_data,
                         current_condition='used',
                         page_title='Sản Phẩm Đã Sử Dụng')

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Trang chi tiết sản phẩm"""
    import requests
    
    try:
        # Fetch product data from API
        api_url = f'{API_BASE_URL}/products/{product_id}/'
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            product = response.json()
            print(f"✅ Fetched product {product_id} from API: {product.get('name', 'Unknown')}")
        else:
            print(f"❌ API returned status {response.status_code} for product {product_id}")
            return redirect(url_for('products'))
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching product {product_id} from API: {e}")
        return redirect(url_for('products'))
    
    # Lấy đánh giá của sản phẩm (tạm thời để trống)
    product_reviews = []
    avg_rating = product.get('rating', 0)
    
    # Sản phẩm liên quan (tạm thời để trống)
    related_products = []
    
    return render_template('product-detail.html',
                         product=product,
                         reviews=product_reviews,
                         avg_rating=avg_rating,
                         related_products=related_products)

@app.route('/api/add-to-cart', methods=['POST'])
def add_to_cart():
    """API thêm vào giỏ hàng"""
    import requests
    
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    try:
        # Fetch product from API
        api_url = f'{API_BASE_URL}/products/{product_id}/'
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            product = response.json()
            
            if product.get('stock_quantity', 0) < quantity:
                return jsonify({'success': False, 'message': 'Số lượng không đủ'})
            
            # Ở đây sẽ lưu vào session hoặc database
            # Hiện tại chỉ trả về thành công
            return jsonify({
                'success': True, 
                'message': f'Đã thêm {quantity} {product.get("name", "sản phẩm")} vào giỏ hàng',
                'cart_count': 3  # Demo
            })
        else:
            return jsonify({'success': False, 'message': 'Sản phẩm không tồn tại'})
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching product for cart: {e}")
        return jsonify({'success': False, 'message': 'Lỗi khi tải thông tin sản phẩm'})

@app.route('/api/newsletter', methods=['POST'])
def newsletter_subscribe():
    """API đăng ký newsletter"""
    data = request.get_json()
    email = data.get('email')
    
    if not email or '@' not in email:
        return jsonify({'success': False, 'message': 'Email không hợp lệ'})
    
    # Ở đây sẽ lưu email vào database
    return jsonify({'success': True, 'message': 'Đăng ký thành công!'})

@app.route('/api/search')
def search_products():
    """API tìm kiếm sản phẩm"""
    import requests
    
    query = request.args.get('q', '').lower()
    
    if len(query) < 2:
        return jsonify([])
    
    try:
        # Fetch products from API
        api_url = f'{API_BASE_URL}/products/'
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            all_products = response.json()
            
            # Tìm kiếm theo tên sản phẩm hoặc thương hiệu
            results = []
            for product in all_products:
                if (query in product.get('name', '').lower() or 
                    query in product.get('brand_name', '').lower() or
                    query in product.get('category', {}).get('name', '').lower()):
                    results.append({
                        'id': product.get('id'),
                        'name': product.get('name'),
                        'brand': product.get('brand_name'),
                        'price': product.get('discounted_price', 0) * 1000,
                        'image': product.get('image')
                    })
            
            return jsonify(results[:5])  # Giới hạn 5 kết quả
        else:
            return jsonify([])
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error searching products: {e}")
        return jsonify([])

@app.route('/cart')
def cart():
    """Trang giỏ hàng"""
    # Khởi tạo giỏ hàng trống mặc định
    cart_items = []
    subtotal = 0
    shipping = 0
    total = 0
    
    return render_template('cart.html', 
                         cart_items=cart_items,
                         subtotal=subtotal,
                         shipping=shipping,
                         total=total)

@app.route('/checkout')
def checkout():
    """Trang thanh toán"""
    # Mặc định giỏ hàng trống cho trang thanh toán khi chưa thêm sản phẩm
    cart_items = []
    subtotal = 0
    shipping = 0
    total = 0
    return render_template('checkout.html',
                           cart_items=cart_items,
                           subtotal=subtotal,
                           shipping=shipping,
                           total=total)

@app.route('/events/voucher')
def voucher_wheel():
    """Trang Vòng Quay May Mắn"""
    return render_template('voucher.html')

@app.route('/events/partner')
def partner_registration():
    """Trang đăng ký cộng tác viên"""
    return render_template('partner.html')

@app.route('/events/flash-sale')
def flash_sale_events():
    """Trang flash sale chớp nhoáng"""
    return render_template('flash_sale.html')

@app.route('/events')
def all_events():
    """Trang tất cả sự kiện"""
    return render_template('events.html')

@app.route('/login')
def login():
    """Trang đăng nhập"""
    return render_template('login.html')

@app.route('/about')
def about():
    """Trang về chúng tôi"""
    return render_template('about.html')

@app.route('/shipping-payment')
def shipping_payment():
    return render_template('shipping-payment.html')

@app.route('/shopping-guide')
def shopping_guide():
    return render_template('shopping-guide.html')

@app.route('/return-policy')
def return_policy():
    return render_template('return-policy.html')

@app.route('/online-payment-safety')
def online_payment_safety():
    return render_template('online-payment-safety.html')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/skincare')
def skincare():
    return render_template('skincare.html')

# Admin Routes
@app.route('/admin')
def admin_dashboard():
    """Admin Dashboard"""
    return render_template('admin_dashboard.html')

@app.route('/admin/products/new')
def admin_products_new():
    """Admin - Quản lý sản phẩm mới"""
    return render_template('admin_products_new.html')

@app.route('/admin/products/used')
def admin_products_used():
    """Admin - Quản lý sản phẩm đã sử dụng"""
    return render_template('admin_products_used.html')

@app.route('/admin/products/flash-sale')
def admin_products_flash_sale():
    """Admin - Quản lý flash sale"""
    return render_template('admin_products_flash_sale.html')

@app.route('/admin/orders')
def admin_orders():
    """Admin - Quản lý đơn hàng"""
    return render_template('admin_orders.html')

@app.route('/admin/orders/<int:order_id>')
def admin_order_detail(order_id):
    """Admin - Chi tiết đơn hàng"""
    return render_template('admin_orders.html')

# Admin API Endpoints
@app.route('/admin/api/orders', methods=['GET'])
def admin_api_orders():
    """API lấy danh sách đơn hàng cho admin"""
    import requests
    
    try:
        response = requests.get(f'{API_BASE_URL}/orders/', timeout=10)
        if response.status_code == 200:
            orders = response.json()
            return jsonify(orders)
        else:
            return jsonify({'error': 'Không thể lấy danh sách đơn hàng'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

@app.route('/admin/api/orders/<int:order_id>', methods=['GET', 'PATCH'])
def admin_api_order_detail(order_id):
    """API chi tiết đơn hàng cho admin"""
    import requests
    
    try:
        if request.method == 'GET':
            response = requests.get(f'{API_BASE_URL}/orders/{order_id}/', timeout=10)
            if response.status_code == 200:
                return jsonify(response.json())
            else:
                return jsonify({'error': 'Không tìm thấy đơn hàng'}), 404
                
        elif request.method == 'PATCH':
            data = request.get_json()
            response = requests.patch(f'{API_BASE_URL}/orders/{order_id}/', 
                                    json=data, timeout=10)
            if response.status_code == 200:
                return jsonify(response.json())
            else:
                return jsonify({'error': 'Không thể cập nhật đơn hàng'}), 500
                
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

@app.route('/admin/api/orders/<int:order_id>/confirm', methods=['POST'])
def admin_api_confirm_order(order_id):
    """API xác nhận đơn hàng"""
    import requests
    
    try:
        # Lấy thông tin đơn hàng
        order_response = requests.get(f'{API_BASE_URL}/orders/{order_id}/', timeout=10)
        if order_response.status_code != 200:
            return jsonify({'error': 'Không tìm thấy đơn hàng'}), 404
            
        order = order_response.json()
        
        # Cập nhật trạng thái xác nhận
        confirm_response = requests.patch(f'{API_BASE_URL}/orders/{order_id}/', 
                                        json={'is_confirmed': True}, timeout=10)
        if confirm_response.status_code != 200:
            return jsonify({'error': 'Không thể xác nhận đơn hàng'}), 500
            
        # Cập nhật số lượng tồn kho cho từng sản phẩm
        for item in order.get('items', []):
            product_id = item.get('product_id')
            quantity = item.get('quantity', 0)
            
            # Lấy thông tin sản phẩm hiện tại
            product_response = requests.get(f'{API_BASE_URL}/products/{product_id}/', timeout=10)
            if product_response.status_code == 200:
                product = product_response.json()
                new_stock = product.get('stock_quantity', 0) - quantity
                
                # Cập nhật số lượng tồn kho
                requests.patch(f'{API_BASE_URL}/products/{product_id}/', 
                             json={'stock_quantity': new_stock}, timeout=10)
        
        return jsonify({'success': True, 'message': 'Đã xác nhận đơn hàng và cập nhật tồn kho'})
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

@app.route('/admin/api/orders/<int:order_id>/cancel', methods=['POST'])
def admin_api_cancel_order(order_id):
    """API hủy đơn hàng"""
    import requests
    
    try:
        # Lấy thông tin đơn hàng
        order_response = requests.get(f'{API_BASE_URL}/orders/{order_id}/', timeout=10)
        if order_response.status_code != 200:
            return jsonify({'error': 'Không tìm thấy đơn hàng'}), 404
            
        order = order_response.json()
        
        # Nếu đơn hàng đã được xác nhận, khôi phục số lượng tồn kho
        if order.get('is_confirmed'):
            for item in order.get('items', []):
                product_id = item.get('product_id')
                quantity = item.get('quantity', 0)
                
                # Lấy thông tin sản phẩm hiện tại
                product_response = requests.get(f'{API_BASE_URL}/products/{product_id}/', timeout=10)
                if product_response.status_code == 200:
                    product = product_response.json()
                    new_stock = product.get('stock_quantity', 0) + quantity
                    
                    # Cập nhật số lượng tồn kho
                    requests.patch(f'{API_BASE_URL}/products/{product_id}/', 
                                 json={'stock_quantity': new_stock}, timeout=10)
        
        # Cập nhật trạng thái đơn hàng thành cancelled
        cancel_response = requests.patch(f'{API_BASE_URL}/orders/{order_id}/', 
                                       json={'status': 'cancelled'}, timeout=10)
        if cancel_response.status_code == 200:
            return jsonify({'success': True, 'message': 'Đã hủy đơn hàng và khôi phục tồn kho'})
        else:
            return jsonify({'error': 'Không thể hủy đơn hàng'}), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

@app.route('/admin/api/products/<int:product_id>', methods=['PATCH'])
def admin_api_update_product(product_id):
    """API cập nhật sản phẩm cho admin"""
    import requests
    
    try:
        data = request.get_json()
        response = requests.patch(f'{API_BASE_URL}/products/{product_id}/', 
                                json=data, timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Không thể cập nhật sản phẩm'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

@app.route('/api/product-stock/<int:product_id>')
def api_product_stock(product_id):
    """API lấy thông tin stock của sản phẩm"""
    import requests
    
    try:
        response = requests.get(f'{API_BASE_URL}/products/{product_id}/', timeout=10)
        if response.status_code == 200:
            product = response.json()
            return jsonify({
                'id': product.get('id'),
                'name': product.get('name'),
                'stock_quantity': product.get('stock_quantity', 0)
            })
        else:
            return jsonify({'error': 'Không tìm thấy sản phẩm'}), 404
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Tạo thư mục static nếu chưa có
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/image', exist_ok=True)
    
    print("🚀 BuddySkincare Website đang khởi động...")
    print("📱 Truy cập: http://localhost:8000")
    print("🛍️ Trang chủ: http://localhost:8000/")
    print("📦 Sản phẩm: http://localhost:8000/products")
    print("🛒 Giỏ hàng: http://localhost:8000/cart")
    print("💳 Thanh toán: http://localhost:8000/checkout")
    print("🔐 Đăng nhập: http://localhost:8000/login")
    print("\n✨ Tính năng demo:")
    print("- Flash sale với countdown timer")
    print("- Bộ lọc sản phẩm đa tiêu chí")
    print("- Đánh giá và bình luận")
    print("- Responsive design")
    print("- Add to cart với animation")
    print("- Newsletter subscription")
    print("\n🔧 Để dừng server: Ctrl+C")
    
    app.run(debug=True, host='0.0.0.0', port=8000)
