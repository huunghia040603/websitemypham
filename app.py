from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, session
import os
from datetime import datetime, timedelta
import cloudinary
import cloudinary.uploader
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

app = Flask(__name__)
app.secret_key = 'buddyskincare_secret_key_2024'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# API URL for PythonAnywhere
API_BASE_URL = 'https://buddyskincare.pythonanywhere.com'

# Cache for products
products_cache = {
    'data': None,
    'timestamp': 0,
    'ttl': 300  # 5 minutes
}

# Cloudinary configuration
cloudinary.config(
    cloud_name="deoknys7k",
    api_key="657643869681298",
    api_secret="K8pAAJPmIUcO7ThRnfOtJx7Ntwg"
)

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
    'Bioderma', 'Cetaphil', 'Chanel', 'Dior', 'Estee Lauder', 
    'L\'Oreal Paris', 'Mac Cosmetics', 'SK-II', 'The Ordinary', 'TheFaceShop'
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

# Helper to get products with cache
def get_products_with_cache():
    """Get products from cache or API"""
    current_time = time.time()
    
    # Check if cache is valid
    if (products_cache['data'] is not None and 
        current_time - products_cache['timestamp'] < products_cache['ttl']):
        print("📦 Using cached products")
        return products_cache['data']
    
    # Fetch from API with shorter timeout
    try:
        import requests
        api_url = f'{API_BASE_URL}/products/'
        response = requests.get(api_url, timeout=5)  # Shorter timeout
        
        if response.status_code == 200:
            products = response.json()
            # Update cache
            products_cache['data'] = products
            products_cache['timestamp'] = current_time
            print(f"✅ Fetched {len(products)} products from API and cached")
            return products
        else:
            print(f"❌ API returned status {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error fetching products: {e}")
        # Return empty list if API fails
        return []

# Helper to classify product condition based on status keyword

def _is_new_status(status: str) -> bool:
    try:
        if not status:
            return False
        s = str(status).lower()
        return ('new' in s) or ('chiet' in s)
    except Exception:
        return False

def _extract_category_name(product: dict) -> str:
    try:
        if not isinstance(product, dict):
            return ''
        cat = product.get('category')
        if isinstance(cat, dict):
            return (cat.get('name') or cat.get('title') or '').strip()
        # Fallbacks if API provides flat fields
        return (product.get('category_name') or product.get('category') or '').strip()
    except Exception:
        return ''

@app.route('/')
def index():
    """Trang chủ"""
    # Use cached products
    all_products = get_products_with_cache()
    
    # Filter flash sale products (có discount > 0)
    flash_sale_products = [p for p in all_products if float(p.get('discount_rate', 0)) > 0][:4]
    
    # Filter featured products (không có discount hoặc discount thấp)
    featured_products = [p for p in all_products if float(p.get('discount_rate', 0)) <= 10][:4]
    
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
    # Use cached products
    all_products = get_products_with_cache()
    
    # Lấy tham số filter
    category = request.args.get('category')
    brand = request.args.get('brand')
    price_range = request.args.get('price')
    discount = request.args.get('discount')
    sort_by = request.args.get('sort', 'newest')
    condition = request.args.get('condition', 'all')

    # Hỗ trợ tên tham số mới theo yêu cầu
    category_name = request.args.get('category_name') or category
    brands_name = request.args.get('brands_name') or brand
    new_price_range = request.args.get('price_range') or price_range
    new_discount = request.args.get('discount_range') or discount
    tags_filter = request.args.get('tags')
    
    # Filter sản phẩm
    filtered_products = all_products.copy()
    
    if category_name:
        target = category_name.strip().lower()
        filtered_products = [p for p in filtered_products if _extract_category_name(p).lower() == target]
    
    if brands_name:
        filtered_products = [p for p in filtered_products if (p.get('brand_name') or (p.get('brand') or {}).get('name') or '').strip() == brands_name]
    
    if condition != 'all':
        filtered_products = [p for p in filtered_products if p.get('status') == condition]
    
    # Filter by tags
    if tags_filter:
        def has_tag(product, target_tag):
            try:
                tags = product.get('tags', [])
                if not isinstance(tags, list):
                    return False
                return any(
                    (isinstance(t, str) and t.lower() == target_tag.lower()) or
                    (isinstance(t, dict) and t.get('name', '').lower() == target_tag.lower())
                    for t in tags
                )
            except Exception:
                return False
        
        filtered_products = [p for p in filtered_products if has_tag(p, tags_filter)]
    
    # Khoảng giá mới (VND)
    if new_price_range:
        def price_vnd(x):
            return (x.get('discounted_price', 0) or 0) * 1000
        if new_price_range == 'under_200k':
            filtered_products = [p for p in filtered_products if price_vnd(p) < 200_000]
        elif new_price_range == '200_500':
            filtered_products = [p for p in filtered_products if 200_000 <= price_vnd(p) < 500_000]
        elif new_price_range == '500_1m':
            filtered_products = [p for p in filtered_products if 500_000 <= price_vnd(p) < 1_000_000]
        elif new_price_range == 'over_1m':
            filtered_products = [p for p in filtered_products if price_vnd(p) >= 1_000_000]
        # Giữ tương thích cũ
        elif new_price_range == 'under_500k':
            filtered_products = [p for p in filtered_products if price_vnd(p) < 500_000]
        elif new_price_range == '500k_1m':
            filtered_products = [p for p in filtered_products if 500_000 <= price_vnd(p) < 1_000_000]
        elif new_price_range == '1m_2m':
            filtered_products = [p for p in filtered_products if 1_000_000 <= price_vnd(p) < 2_000_000]
        elif new_price_range == 'over_2m':
            filtered_products = [p for p in filtered_products if price_vnd(p) >= 2_000_000]
    
    # Giảm giá mới
    if new_discount:
        def rate(x):
            try:
                return float(x.get('discount_rate', 0) or 0)
            except Exception:
                return 0.0
        if new_discount == 'under_30':
            filtered_products = [p for p in filtered_products if rate(p) < 30]
        elif new_discount == '50_70':
            filtered_products = [p for p in filtered_products if 50 <= rate(p) <= 70]
        elif new_discount == 'over_70':
            filtered_products = [p for p in filtered_products if rate(p) > 70]
        # Giữ tương thích cũ
        elif new_discount == 'over_50':
            filtered_products = [p for p in filtered_products if rate(p) >= 50]
        elif new_discount == '30_50':
            filtered_products = [p for p in filtered_products if 30 <= rate(p) < 50]
        elif new_discount == 'under_30_old':
            filtered_products = [p for p in filtered_products if rate(p) < 30]
    
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
        response = requests.get(api_url, timeout=30)
        
        if response.status_code == 200:
            all_products = response.json()
            # Filter products with status treated as 'new' (contains 'new' or 'chiet')
            filtered_products = [p for p in all_products if _is_new_status(p.get('status'))]
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
        response = requests.get(api_url, timeout=30)
        
        if response.status_code == 200:
            all_products = response.json()
            # Filter products treated as 'used' (not new by our rule)
            filtered_products = [p for p in all_products if not _is_new_status(p.get('status'))]
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
        response = requests.get(api_url, timeout=30)
        
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
        response = requests.get(api_url, timeout=30)
        
        if response.status_code == 200:
            product = response.json()
            # Check stock
            if product.get('stock_quantity', 0) < quantity:
                return jsonify({'success': False, 'message': 'Số lượng không đủ'})
            
            # Initialize cart in session if not exists
            if 'cart' not in session:
                session['cart'] = {}
            
            # Add/update product in cart
            cart = session['cart']
            if str(product_id) in cart:
                cart[str(product_id)]['quantity'] += quantity
            else:
                cart[str(product_id)] = {
                    'product_id': product_id,
                    'name': product.get('name', ''),
                    'price': product.get('discounted_price', product.get('original_price', 0)),
                    'image': product.get('image', ''),
                    'brand': product.get('brand_name', ''),
                    'quantity': quantity
                }
            
            # Update session
            session['cart'] = cart
            session.modified = True
            
            # Calculate total items in cart
            total_items = sum(item['quantity'] for item in cart.values())
            
            return jsonify({
                'success': True, 
                'message': f'Đã thêm {quantity} {product.get("name", "sản phẩm")} vào giỏ hàng',
                'cart_count': total_items,
                'cart': cart
            })
        else:
            return jsonify({'success': False, 'message': 'Sản phẩm không tồn tại'})
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching product for cart: {e}")
        return jsonify({'success': False, 'message': 'Lỗi khi tải thông tin sản phẩm'})

@app.route('/api/cart', methods=['GET'])
def get_cart():
    """API lấy thông tin giỏ hàng"""
    cart = session.get('cart', {})
    total_items = sum(item['quantity'] for item in cart.values())
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())
    
    return jsonify({
        'success': True,
        'cart': cart,
        'total_items': total_items,
        'total_price': total_price
    })

@app.route('/api/cart/clear', methods=['POST'])
def clear_cart():
    """API xóa giỏ hàng"""
    session['cart'] = {}
    session.modified = True
    return jsonify({'success': True, 'message': 'Đã xóa giỏ hàng'})

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
        response = requests.get(api_url, timeout=30)
        if response.status_code != 200:
            return jsonify([])

        all_products = response.json()

        # Tìm kiếm theo tên sản phẩm, thương hiệu, hoặc danh mục
        results = []
        for product in all_products:
            try:
                product_name = product.get('name', '').lower()
                brand_name = product.get('brand_name', '').lower()
                category_name = ''
                category = product.get('category') or {}
                if isinstance(category, dict):
                    category_name = category.get('name', '').lower()
                if (
                    query in product_name or
                    query in brand_name or
                    query in category_name
                ):
                    results.append({
                        'id': product.get('id'),
                        'name': product.get('name'),
                        'brand': product.get('brand_name'),
                        'price': (product.get('discounted_price', 0) or 0) * 1000,
                        'image': product.get('image')
                    })
            except Exception:
                continue

        return jsonify(results[:5])  # Giới hạn 5 kết quả

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

@app.route('/events/lucky-number')
def lucky_number_event():
    """Trang Số may mắn"""
    return render_template('lucky-number.html')

@app.route('/login')
def login():
    """Trang đăng nhập"""
    return render_template('login.html')

@app.route('/about')
def about():
    """Trang về chúng tôi"""
    return render_template('about.html')

@app.route('/profile')
def profile():
    """Trang hồ sơ cá nhân"""
    return render_template('profile.html')

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

@app.route('/live-chat')
def live_chat():
    return render_template('live-chat.html')

@app.route('/test-order-notification')
def test_order_notification():
    """Test page for order notification system"""
    return render_template('test_order_notification.html')

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin Login Page"""
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Check admin credentials
        admin_credentials = [
            {'username': 'admin', 'password': 'admin123'},
            {'username': '0987789274', 'password': '123'},
            {'username': 'admin@buddyskincare.com', 'password': '123'},
            {'username': 'Admin BuddySkincare', 'password': '123'}
        ]
        
        # Validate credentials
        valid_login = False
        for cred in admin_credentials:
            if username == cred['username'] and password == cred['password']:
                valid_login = True
                break
        
        if valid_login:
            return jsonify({
                'success': True,
                'message': 'Đăng nhập thành công'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Tên đăng nhập hoặc mật khẩu không đúng'
            }), 401
    
    return render_template('admin_login.html')

@app.route('/logout')
def admin_logout():
    """Admin Logout"""
    return redirect('/admin/login')

@app.route('/admin')
def admin_dashboard():
    """Admin Dashboard"""
    return render_template('admin_dashboard.html')

@app.route('/admin/products')
def admin_products():
    """Admin - Quản lý sản phẩm (unified)"""
    return render_template('admin_products.html')

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

@app.route('/admin/analytics')
def admin_analytics():
    """Admin - Thống kê doanh thu"""
    return render_template('admin_analytics.html')

@app.route('/admin/orders/<int:order_id>')
def admin_order_detail(order_id):
    """Admin - Chi tiết đơn hàng"""
    return render_template('admin_orders.html')

@app.route('/admin/orders/<int:order_id>/invoice')
def admin_order_invoice(order_id: int):
    """Admin - Hóa đơn in/ảnh cho đơn hàng"""
    import requests
    try:
        resp = requests.get(f'{API_BASE_URL}/orders/{order_id}/', timeout=30)
        if resp.status_code != 200:
            return render_template('admin_invoice.html', order=None, error=f'Không tìm thấy đơn hàng #{order_id}')
        order = resp.json()
    except Exception as e:
        return render_template('admin_invoice.html', order=None, error=f'Lỗi tải đơn hàng: {str(e)}')
    return render_template('admin_invoice.html', order=order)

@app.route('/admin/orders/<int:order_id>/invoice/email', methods=['POST'])
def admin_order_invoice_email(order_id: int):
    """Send invoice via email."""
    import requests
    try:
        resp = requests.get(f'{API_BASE_URL}/orders/{order_id}/', timeout=30)
        if resp.status_code != 200:
            return jsonify({'success': False, 'message': 'Không tìm thấy đơn hàng'}), 404
        order = resp.json()
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi tải đơn hàng: {str(e)}'}), 500

    # Determine recipient
    data = request.get_json(silent=True) or {}
    recipient = (data.get('email') or order.get('email') or '').strip()
    if not recipient or '@' not in recipient:
        return jsonify({'success': False, 'message': 'Email khách hàng không hợp lệ'}), 400

    # Render minimal HTML invoice for email
    html_content = render_template('emails/invoice_email.html', order=order)

    # SMTP configuration from environment
    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')
    sender = os.getenv('SMTP_SENDER', smtp_user or 'no-reply@buddyskincare.vn')

    if not (smtp_user and smtp_pass):
        # Development fallback: save invoice HTML to file instead of sending email
        try:
            fallback_dir = os.path.join(os.getcwd(), 'sent_emails')
            os.makedirs(fallback_dir, exist_ok=True)
            filename = f'invoice_{order_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            file_path = os.path.join(fallback_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return jsonify({'success': True, 'message': f'Đã lưu hóa đơn vào file: {file_path}', 'saved_path': file_path}), 200
        except Exception as e:
            return jsonify({'success': False, 'message': f'SMTP chưa cấu hình và lưu file thất bại: {str(e)}'}), 500

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Hóa đơn đơn hàng #{order_id} - BuddySkincare'
        msg['From'] = sender
        msg['To'] = recipient
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(sender, [recipient], msg.as_string())
        return jsonify({'success': True, 'message': f'Đã gửi hóa đơn đến {recipient}'}), 200
    except (smtplib.SMTPAuthenticationError, smtplib.SMTPException, TimeoutError) as e:
        # Graceful fallback: save HTML to file when SMTP fails, return 200 for UX
        try:
            fallback_dir = os.path.join(os.getcwd(), 'sent_emails')
            os.makedirs(fallback_dir, exist_ok=True)
            filename = f'invoice_{order_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            file_path = os.path.join(fallback_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return jsonify({'success': True, 'message': f'Không gửi được qua SMTP, đã lưu hóa đơn vào file', 'saved_path': file_path, 'error': str(e)}), 200
        except Exception as save_err:
            return jsonify({'success': False, 'message': f'Lỗi SMTP và lưu file thất bại: {str(save_err)}', 'error': str(e)}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi gửi email: {str(e)}'}), 500

@app.route('/admin/customers')
def admin_customers():
    """Admin - Quản lý khách hàng"""
    return render_template('admin_customers.html')

@app.route('/admin/vouchers')
def admin_vouchers():
    """Admin - Quản lý voucher"""
    return render_template('admin_vouchers.html')

# Lucky Number admin page
@app.route('/admin/lucky-number')
def admin_lucky_number():
    """Admin - Quản lý sự kiện Số may mắn"""
    return render_template('admin_lucky_number.html')

@app.route('/admin/customer-data')
def admin_customer_data():
    """Admin - Dữ liệu tiệp khách hàng"""
    return render_template('admin_customer_data.html')

@app.route('/admin/blog')
def admin_blog():
    """Admin - Quản lý Blog"""
    return render_template('admin_blog.html')

@app.route('/blog/<int:blog_id>')
def blog_detail(blog_id):
    """Chi tiết bài viết blog"""
    return render_template('blog_detail.html', blog_id=blog_id)

@app.route('/admin/email-analytics')
def admin_email_analytics():
    """Admin - Thống kê Email Marketing"""
    return render_template('admin_email_analytics.html')

@app.route('/admin/api/email-analytics', methods=['GET'])
def admin_api_email_analytics():
    """API lấy dữ liệu thống kê email từ Gmail và Google Analytics"""
    try:
        # Get date range from query parameters
        start_date = request.args.get('start_date', '7daysAgo')
        end_date = request.args.get('end_date', 'today')
        
        # Get Gmail data (emails sent)
        gmail_data = get_gmail_data(start_date, end_date)
        
        # Get Google Analytics data (clicks, conversions)
        analytics_data = get_google_analytics_data(start_date, end_date)
        
        # Combine data
        combined_data = {}
        
        if gmail_data:
            combined_data['total_emails'] = gmail_data['total_emails']
            combined_data['flashsale_emails'] = gmail_data['flashsale_emails']
            combined_data['luckygame_emails'] = gmail_data['luckygame_emails']
            combined_data['other_emails'] = gmail_data['other_emails']
        else:
            # Fallback to mock data for emails
            combined_data['total_emails'] = 0
            combined_data['flashsale_emails'] = 0
            combined_data['luckygame_emails'] = 0
            combined_data['other_emails'] = 0
        
        if analytics_data:
            combined_data.update(analytics_data)
        else:
            # Fallback to mock data for analytics
            mock_data = get_mock_analytics_data()
            combined_data.update(mock_data)
        
        return jsonify(combined_data)
            
    except Exception as e:
        print(f"❌ Error in email analytics API: {e}")
        return jsonify(get_mock_analytics_data())

def get_gmail_data(start_date, end_date):
    """Lấy dữ liệu thật từ Gmail API"""
    try:
        # Check if Gmail credentials are available
        credentials_path = os.path.join(os.getcwd(), 'gmail-credentials.json')
        
        if not os.path.exists(credentials_path):
            print("❌ Gmail credentials not found at:", credentials_path)
            print("💡 To enable real Gmail data, create gmail-credentials.json")
            return None
        
        # Try to import and use Gmail API
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
        except ImportError:
            print("❌ Gmail API not installed")
            print("💡 Run: pip install google-api-python-client")
            return None
        
        # Initialize Gmail service
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/gmail.readonly']
        )
        
        service = build('gmail', 'v1', credentials=credentials)
        
        print(f"🔍 Fetching Gmail data from buddyskincarevn@gmail.com ({start_date} to {end_date})")
        
        # Query for sent emails
        query = f'from:buddyskincarevn@gmail.com after:{start_date} before:{end_date}'
        
        try:
            results = service.users().messages().list(
                userId='buddyskincarevn@gmail.com',
                q=query,
                maxResults=1000
            ).execute()
            
            messages = results.get('messages', [])
            
            # Count emails by campaign
            flashsale_count = 0
            luckygame_count = 0
            total_emails = len(messages)
            
            for message in messages:
                msg = service.users().messages().get(
                    userId='buddyskincarevn@gmail.com',
                    id=message['id']
                ).execute()
                
                # Check subject for campaign type
                headers = msg['payload'].get('headers', [])
                subject = ''
                for header in headers:
                    if header['name'] == 'Subject':
                        subject = header['value']
                        break
                
                if 'flash' in subject.lower() or 'sale' in subject.lower():
                    flashsale_count += 1
                elif 'lucky' in subject.lower() or 'game' in subject.lower():
                    luckygame_count += 1
            
            return {
                'total_emails': total_emails,
                'flashsale_emails': flashsale_count,
                'luckygame_emails': luckygame_count,
                'other_emails': total_emails - flashsale_count - luckygame_count
            }
            
        except Exception as e:
            print(f"❌ Error querying Gmail: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Error setting up Gmail API: {e}")
        return None

def get_google_analytics_data(start_date, end_date):
    """Lấy dữ liệu thật từ Google Analytics"""
    try:
        # Check if Google Analytics credentials are available
        credentials_path = os.path.join(os.getcwd(), 'google-analytics-credentials.json')
        
        if not os.path.exists(credentials_path):
            print("❌ Google Analytics credentials not found at:", credentials_path)
            print("💡 To enable real data, follow the setup guide in GOOGLE_ANALYTICS_SETUP.md")
            return None
        
        # Try to import and use Google Analytics Data API
        try:
            from google.analytics.data_v1beta import BetaAnalyticsDataClient
            from google.analytics.data_v1beta.types import (
                DateRange,
                Dimension,
                Metric,
                RunReportRequest,
            )
        except ImportError:
            print("❌ Google Analytics Data API not installed")
            print("💡 Run: pip install google-analytics-data")
            return None
        
        # Initialize client
        client = BetaAnalyticsDataClient.from_service_account_file(credentials_path)
        
        # Your actual Property ID from Google Analytics
        property_id = "504734762"  # Real Property ID from GA4
        
        print(f"🔍 Fetching GA4 data from property {property_id} ({start_date} to {end_date})")
        
        # Query for email campaign data
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[
                Dimension(name="campaignName"),
                Dimension(name="source"),
                Dimension(name="medium"),
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="activeUsers"),
                Metric(name="bounceRate"),
                Metric(name="conversions"),
                Metric(name="totalRevenue"),
            ],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimension_filter={
                "filter": {
                    "field_name": "medium",
                    "string_filter": {
                        "match_type": "EXACT",
                        "value": "email"
                    }
                }
            }
        )
        
        response = client.run_report(request)
        
        # Process the response
        campaigns = []
        total_sessions = 0
        total_users = 0
        total_conversions = 0
        total_revenue = 0
        
        for row in response.rows:
            campaign_name = row.dimension_values[0].value
            sessions = int(row.metric_values[0].value)
            new_users = int(row.metric_values[1].value)
            bounce_rate = float(row.metric_values[2].value)
            conversions = int(row.metric_values[3].value)
            revenue = float(row.metric_values[4].value)
            
            total_sessions += sessions
            total_users += new_users
            total_conversions += conversions
            total_revenue += revenue
            
            campaigns.append({
                'name': campaign_name,
                'sessions': sessions,
                'users': new_users,
                'bounceRate': bounce_rate,
                'conversions': conversions,
                'revenue': revenue,
                'roi': (revenue / sessions * 100) if sessions > 0 else 0
            })
        
        # Get timeline data
        timeline = get_timeline_data(client, property_id, start_date, end_date)
        
        # Get top pages data
        top_pages = get_top_pages_data(client, property_id, start_date, end_date)
        
        result = {
            'totalSessions': total_sessions,
            'totalUsers': total_users,
            'avgClickRate': (total_users / total_sessions * 100) if total_sessions > 0 else 0,
            'avgConversionRate': (total_conversions / total_sessions * 100) if total_sessions > 0 else 0,
            'campaigns': campaigns,
            'timeline': timeline,
            'topPages': top_pages,
            'recentActivity': []  # This would need additional API calls
        }
        
        print(f"✅ Successfully fetched {len(campaigns)} campaigns from Google Analytics")
        return result
        
    except Exception as e:
        print(f"❌ Error fetching Google Analytics data: {e}")
        return None

def get_timeline_data(client, property_id, start_date, end_date):
    """Lấy dữ liệu timeline từ Google Analytics"""
    try:
        from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="date")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="activeUsers"),
            ],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimension_filter={
                "filter": {
                    "field_name": "medium",
                    "string_filter": {
                        "match_type": "EXACT",
                        "value": "email"
                    }
                }
            }
        )
        
        response = client.run_report(request)
        timeline = []
        
        for row in response.rows:
            timeline.append({
                'date': row.dimension_values[0].value,
                'sessions': int(row.metric_values[0].value),
                'users': int(row.metric_values[1].value)
            })
        
        return timeline
    except Exception as e:
        print(f"❌ Error fetching timeline data: {e}")
        return []

def get_top_pages_data(client, property_id, start_date, end_date):
    """Lấy dữ liệu top pages từ Google Analytics"""
    try:
        from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="pagePath")],
            metrics=[Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimension_filter={
                "filter": {
                    "field_name": "medium",
                    "string_filter": {
                        "match_type": "EXACT",
                        "value": "email"
                    }
                }
            },
            order_bys=[{"metric": {"metric_name": "activeUsers"}, "desc": True}],
            limit=10
        )
        
        response = client.run_report(request)
        top_pages = []
        total_users = sum(int(row.metric_values[0].value) for row in response.rows)
        
        for row in response.rows:
            users = int(row.metric_values[0].value)
            percentage = (users / total_users * 100) if total_users > 0 else 0
            
            top_pages.append({
                'page': row.dimension_values[0].value,
                'users': users,
                'percentage': percentage
            })
        
        return top_pages
    except Exception as e:
        print(f"❌ Error fetching top pages data: {e}")
        return []

def get_mock_analytics_data():
    """Mock data for demonstration"""
    return {
        'totalSessions': 1250,
        'totalUsers': 187,
        'avgClickRate': 14.96,
        'avgConversionRate': 3.2,
        'campaigns': [
            {
                'name': 'Flash Sale',
                'sessions': 500,
                'users': 89,
                'bounceRate': 82.2,
                'conversions': 18,
                'revenue': 5400000,
                'roi': 12.5
            },
            {
                'name': 'Lucky Game',
                'sessions': 400,
                'users': 67,
                'bounceRate': 83.25,
                'conversions': 12,
                'revenue': 3600000,
                'roi': 10.2
            },
            {
                'name': 'Newsletter',
                'sessions': 350,
                'users': 31,
                'bounceRate': 91.14,
                'conversions': 5,
                'revenue': 1500000,
                'roi': 6.8
            }
        ],
        'timeline': [
            {'date': '2024-01-01', 'sessions': 45, 'users': 7},
            {'date': '2024-01-02', 'sessions': 52, 'users': 9},
            {'date': '2024-01-03', 'sessions': 38, 'users': 6},
            {'date': '2024-01-04', 'sessions': 67, 'users': 12},
            {'date': '2024-01-05', 'sessions': 43, 'users': 8},
            {'date': '2024-01-06', 'sessions': 55, 'users': 10},
            {'date': '2024-01-07', 'sessions': 48, 'users': 9}
        ],
        'topPages': [
            {'page': '/products', 'users': 89, 'percentage': 47.6},
            {'page': '/events/lucky-number', 'users': 67, 'percentage': 35.8},
            {'page': '/', 'users': 31, 'percentage': 16.6}
        ],
        'recentActivity': [
            {
                'time': '2024-01-07 14:30',
                'campaign': 'Flash Sale',
                'subject': 'Hàng mới về, flash sale ngập tràn!',
                'sent': 500,
                'clicks': 89,
                'status': 'Delivered'
            },
            {
                'time': '2024-01-06 10:15',
                'campaign': 'Lucky Game',
                'subject': 'Trò chơi may mắn tháng này!',
                'sent': 400,
                'clicks': 67,
                'status': 'Delivered'
            },
            {
                'time': '2024-01-05 16:45',
                'campaign': 'Newsletter',
                'subject': 'Tin tức mỹ phẩm tuần này',
                'sent': 350,
                'clicks': 31,
                'status': 'Delivered'
            }
        ]
    }

# Preview invoice email template in browser
@app.route('/templates/emails/invoice_email.html')
def preview_invoice_email():
    """Preview the invoice email template at a direct URL for design/testing.
    Optional query: ?order_id=123 to load real order from API.
    """
    import requests
    order = None
    order_id = request.args.get('order_id')
    if order_id:
        try:
            resp = requests.get(f'{API_BASE_URL}/orders/{order_id}/', timeout=15)
            if resp.status_code == 200:
                order = resp.json()
        except Exception:
            order = None
    if not order:
        # Fallback demo order for preview
        order = {
            'id': 9999,
            'order_date': datetime.now().isoformat(timespec='minutes'),
            'payment_method': 'bank',
            'is_confirmed': True,
            'status': 'processing',
            'voucher_code': 'WELCOME10',
            'phone_number': '0987789274',
            'customer_name': 'Buddy Skincare',
            'street': '123 Đường ABC',
            'ward': 'Phường 1',
            'district': 'Quận 1',
            'province': 'TP.HCM',
            'shipping_fee': 30.0,
            'discount_applied': 20.0,
            'total_amount': 350.0,
            'items': [
                {
                    'product': {
                        'name': 'Nước cân bằng Sen Hậu Giang',
                        'discounted_price': 120.0,
                    },
                    'price_at_purchase': 120.0,
                    'quantity': 1
                },
                {
                    'product': {
                        'name': 'Kem chống nắng SPF50+',
                        'discounted_price': 200.0,
                    },
                    'price_at_purchase': 200.0,
                    'quantity': 1
                }
            ]
        }
    return render_template('emails/invoice_email.html', order=order)

# Preview flash sale announcement email
@app.route('/templates/emails/flash_sale_announcement.html')
def preview_flash_sale_announcement():
    """Preview flash sale announcement email template."""
    return render_template('emails/flash_sale_announcement.html')

# Preview lucky game announcement email
@app.route('/templates/emails/lucky_game_announcement.html')
def preview_lucky_game_announcement():
    """Preview lucky game announcement email template.
    Lấy dữ liệu sự kiện từ API lucky-events và truyền vào template.
    """
    import requests
    event = None
    prizes = []
    total_value_vnd = 0
    end_time_display = None
    try:
        resp = requests.get(f'{API_BASE_URL}/lucky-events/', timeout=15)
        if resp.status_code == 200:
            events = resp.json() or []
            # Ưu tiên sự kiện active, nếu không có lấy sự kiện mới nhất
            active = [e for e in events if e.get('is_active')]
            event = (active[0] if active else (events[0] if events else None))
            if event:
                prizes = event.get('prizes') or []
                try:
                    total_value_vnd = int(sum(float(p.get('value') or 0) for p in prizes) * 1000)
                except Exception:
                    total_value_vnd = 0
                # Format end time
                try:
                    raw = event.get('end_at')
                    if raw:
                        dt = datetime.fromisoformat(str(raw).replace('Z', '+00:00'))
                        end_time_display = dt.strftime('%d/%m/%Y %H:%M')
                except Exception:
                    end_time_display = None
    except Exception:
        event = None
        prizes = []
        total_value_vnd = 0
        end_time_display = None

    def fmt_vnd(n: int) -> str:
        try:
            return f"{n:,.0f}".replace(',', '.') + 'đ'
        except Exception:
            return '0đ'

    return render_template(
        'emails/lucky_game_announcement.html',
        event=event,
        prizes=prizes,
        total_value_display=fmt_vnd(total_value_vnd),
        end_time_display=end_time_display
    )

# Preview new order notification email template in browser
@app.route('/templates/emails/new_order_notification.html')
def preview_new_order_notification():
    """Preview the new order notification email template at a direct URL for design/testing.
    Optional query: ?order_id=123 to load real order from API.
    """
    import requests
    order = None
    pending_orders = []
    order_id = request.args.get('order_id')
    
    if order_id:
        try:
            # Get specific order
            resp = requests.get(f'{API_BASE_URL}/orders/{order_id}/', timeout=15)
            if resp.status_code == 200:
                order = resp.json()
        except Exception:
            order = None
    
    if not order:
        # Fallback demo order for preview
        order = {
            'id': 12345,
            'order_date': datetime.now().isoformat(timespec='minutes'),
            'payment_method': 'bank',
            'is_confirmed': False,
            'status': 'pending',
            'phone_number': '0987789274',
            'customer_name': 'Nguyễn Thị Minh Anh',
            'email': 'minhanh@gmail.com',
            'street': '456 Đường XYZ',
            'ward': 'Phường 2',
            'district': 'Quận 3',
            'province': 'TP.HCM',
            'total_amount': 450.0,
        }
    
    # Get pending orders for demo
    try:
        resp = requests.get(f'{API_BASE_URL}/orders/', timeout=15)
        if resp.status_code == 200:
            all_orders = resp.json()
            pending_orders = [o for o in all_orders if not o.get('is_confirmed', False)][:5]
    except Exception:
        # Demo pending orders
        pending_orders = [
            {
                'id': 12344,
                'customer_name': 'Trần Văn Bình',
                'phone_number': '0987654321',
                'total_amount': 320.0,
                'order_date': (datetime.now() - timedelta(hours=2)).isoformat(),
                'is_confirmed': False
            },
            {
                'id': 12343,
                'customer_name': 'Lê Thị Cẩm',
                'phone_number': '0987123456',
                'total_amount': 180.0,
                'order_date': (datetime.now() - timedelta(hours=5)).isoformat(),
                'is_confirmed': False
            },
            {
                'id': 12342,
                'customer_name': 'Phạm Văn Đức',
                'phone_number': '0987234567',
                'total_amount': 650.0,
                'order_date': (datetime.now() - timedelta(days=1)).isoformat(),
                'is_confirmed': False
            }
        ]
    
    return render_template('emails/new_order_notification.html', 
                         order=order, 
                         pending_orders=pending_orders,
                         current_time=datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

# Admin API Endpoints
@app.route('/admin/api/orders', methods=['GET'])
def admin_api_orders():
    """API lấy danh sách đơn hàng cho admin"""
    import requests
    
    try:
        print(f"🔍 Fetching orders from: {API_BASE_URL}/orders/")
        
        # Try with different authentication methods
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # First try without authentication (in case it's public)
        # Sort by order_date descending (newest first)
        response = requests.get(f'{API_BASE_URL}/orders/?ordering=-order_date', headers=headers, timeout=30)
        print(f"📡 Orders API response status: {response.status_code}")
        
        if response.status_code == 200:
            orders = response.json()
            print(f"✅ Successfully fetched {len(orders)} orders")
            return jsonify(orders)
        elif response.status_code == 401:
            # If authentication required, try with basic auth or return empty list for now
            print("🔐 Orders API requires authentication, returning empty list")
            return jsonify([])
        else:
            print(f"❌ Orders API error: {response.status_code} - {response.text}")
            return jsonify({'error': f'Không thể lấy danh sách đơn hàng. API trả về: {response.status_code}'}), 500
    except requests.exceptions.RequestException as e:
        print(f"❌ Orders API connection error: {e}")
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

@app.route('/admin/api/orders/<int:order_id>', methods=['GET', 'PATCH'])
def admin_api_order_detail(order_id):
    """API chi tiết đơn hàng cho admin"""
    import requests
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if request.method == 'GET':
            response = requests.get(f'{API_BASE_URL}/orders/{order_id}/', headers=headers, timeout=30)
            if response.status_code == 200:
                return jsonify(response.json())
            elif response.status_code == 401:
                return jsonify({'error': 'API yêu cầu xác thực'}), 401
            else:
                return jsonify({'error': 'Không tìm thấy đơn hàng'}), 404
                
        elif request.method == 'PATCH':
            data = request.get_json()
            response = requests.patch(f'{API_BASE_URL}/orders/{order_id}/', 
                                    json=data, headers=headers, timeout=30)
            if response.status_code == 200:
                return jsonify(response.json())
            elif response.status_code == 401:
                return jsonify({'error': 'API yêu cầu xác thực'}), 401
            else:
                return jsonify({'error': 'Không thể cập nhật đơn hàng'}), 500
                
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

@app.route('/admin/api/orders/<int:order_id>/confirm', methods=['POST'])
def admin_api_confirm_order(order_id):
    """API xác nhận đơn hàng"""
    import requests
    
    try:
        print(f"🔍 Confirming order {order_id}...")
        
        # Lấy thông tin đơn hàng trước
        order_response = requests.get(f'{API_BASE_URL}/orders/{order_id}/', timeout=30)
        if order_response.status_code != 200:
            return jsonify({'error': 'Không tìm thấy đơn hàng'}), 404
        
        order_data = order_response.json()
        print(f"📦 Order data: {order_data}")
        
        # Cập nhật trạng thái đơn hàng
        update_data = {
            'is_confirmed': True,
            'status': 'processing'
        }
        
        # Gọi API cập nhật đơn hàng
        update_response = requests.patch(
            f'{API_BASE_URL}/orders/{order_id}/', 
            json=update_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"🔍 Update response status: {update_response.status_code}")
        print(f"🔍 Update response content: {update_response.text}")
        
        if update_response.status_code == 200:
            print(f"✅ Order {order_id} confirmed successfully")
            return jsonify({
                'success': True, 
                'message': f'Đã xác nhận đơn hàng #{order_id} thành công!'
            })
        elif update_response.status_code == 401:
            print(f"🔐 API requires authentication for order update")
            return jsonify({
                'success': False, 
                'message': f'⚠️ Không thể cập nhật đơn hàng #{order_id} do yêu cầu xác thực API.',
                'error': 'API requires authentication for order updates'
            })
        else:
            print(f"❌ Failed to update order: {update_response.status_code}")
            return jsonify({'error': f'Không thể cập nhật đơn hàng: {update_response.status_code}'}), 500
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error confirming order {order_id}: {e}")
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500
    except Exception as e:
        print(f"❌ Error confirming order {order_id}: {e}")
        return jsonify({'error': f'Lỗi xác nhận đơn hàng: {str(e)}'}), 500

@app.route('/admin/api/orders/<int:order_id>/cancel', methods=['POST'])
def admin_api_cancel_order(order_id):
    """API hủy đơn hàng"""
    import requests
    
    try:
        print(f"🔍 Cancelling order {order_id}...")
        
        # Lấy thông tin đơn hàng trước
        order_response = requests.get(f'{API_BASE_URL}/orders/{order_id}/', timeout=30)
        if order_response.status_code != 200:
            return jsonify({'error': 'Không tìm thấy đơn hàng'}), 404
        
        order_data = order_response.json()
        print(f"📦 Order data: {order_data}")
        
        # Cập nhật trạng thái đơn hàng
        update_data = {
            'is_confirmed': False,
            'status': 'cancelled'
        }
        
        # Gọi API cập nhật đơn hàng
        update_response = requests.patch(
            f'{API_BASE_URL}/orders/{order_id}/', 
            json=update_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if update_response.status_code == 200:
            print(f"✅ Order {order_id} cancelled successfully")
            return jsonify({
                'success': True, 
                'message': f'Đã hủy đơn hàng #{order_id} thành công!'
            })
        elif update_response.status_code == 401:
            print(f"🔐 API requires authentication for order update")
            return jsonify({
                'success': False, 
                'message': f'⚠️ Không thể hủy đơn hàng #{order_id} do yêu cầu xác thực API.',
                'error': 'API requires authentication for order updates'
            })
        else:
            print(f"❌ Failed to update order: {update_response.status_code}")
            return jsonify({'error': f'Không thể cập nhật đơn hàng: {update_response.status_code}'}), 500
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error cancelling order {order_id}: {e}")
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500
    except Exception as e:
        print(f"❌ Error cancelling order {order_id}: {e}")
        return jsonify({'error': f'Lỗi hủy đơn hàng: {str(e)}'}), 500

@app.route('/admin/api/orders/<int:order_id>/ship', methods=['POST'])
def admin_api_ship_order(order_id):
    """API đánh dấu đơn hàng đã giao hàng"""
    import requests
    
    try:
        print(f"🚚 Shipping order {order_id}...")
        
        # Lấy thông tin đơn hàng trước
        order_response = requests.get(f'{API_BASE_URL}/orders/{order_id}/', timeout=30)
        if order_response.status_code != 200:
            return jsonify({'error': 'Không tìm thấy đơn hàng'}), 404
        
        order_data = order_response.json()
        print(f"📦 Order data: {order_data}")
        
        # Cập nhật trạng thái đơn hàng thành 'shipped'
        update_data = {
            'status': 'shipped'
        }
        
        # Gọi API cập nhật đơn hàng
        update_response = requests.patch(
            f'{API_BASE_URL}/orders/{order_id}/', 
            json=update_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if update_response.status_code == 200:
            print(f"✅ Order {order_id} shipped successfully")
            return jsonify({
                'success': True, 
                'message': f'Đã đánh dấu đơn hàng #{order_id} là đã giao hàng thành công!'
            })
        else:
            print(f"❌ Failed to update order: {update_response.status_code}")
            return jsonify({'error': f'Không thể cập nhật đơn hàng: {update_response.status_code}'}), 500
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error shipping order {order_id}: {e}")
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500
    except Exception as e:
        print(f"❌ Error shipping order {order_id}: {e}")
        return jsonify({'error': f'Lỗi đánh dấu giao hàng: {str(e)}'}), 500

@app.route('/admin/api/orders/auto-complete', methods=['POST'])
def admin_api_auto_complete_orders():
    """API tự động cập nhật đơn hàng từ 'shipped' sang 'completed' sau 10 phút (để test)"""
    import requests
    
    try:
        # Lấy tất cả đơn hàng có trạng thái 'shipped'
        response = requests.get(f'{API_BASE_URL}/orders/', timeout=30)
        if response.status_code != 200:
            return jsonify({'error': 'Không thể lấy danh sách đơn hàng'}), 500
        
        orders = response.json()
        current_time = datetime.now()
        updated_orders = []
        
        for order in orders:
            if order.get('status') == 'shipped':
                # Kiểm tra xem đơn hàng đã được giao hàng hơn 5 ngày chưa
                updated_at_str = order.get('updated_at')
                if updated_at_str and updated_at_str != 'None':
                    try:
                        # Parse thời gian cập nhật
                        updated_at = datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))
                        # Chuyển về timezone local để so sánh
                        updated_at = updated_at.replace(tzinfo=None)
                        
                        # Kiểm tra nếu đã qua 10 phút (để test)
                        time_diff = current_time - updated_at
                        if time_diff.total_seconds() >= 600:  # 600 giây = 10 phút
                            # Cập nhật trạng thái sang 'completed'
                            update_data = {
                                'status': 'completed'
                            }
                            
                            update_response = requests.patch(
                                f'{API_BASE_URL}/orders/{order["id"]}/',
                                json=update_data,
                                timeout=30
                            )
                            
                            if update_response.status_code == 200:
                                updated_orders.append({
                                    'id': order['id'],
                                    'customer_name': order.get('customer_name', 'N/A'),
                                    'updated_at': updated_at_str
                                })
                                print(f"✅ Auto-completed order {order['id']}")
                            else:
                                print(f"❌ Failed to auto-complete order {order['id']}: {update_response.status_code}")
                    except Exception as e:
                        print(f"❌ Error processing order {order['id']}: {e}")
                        continue
        
        return jsonify({
            'message': f'Đã tự động hoàn thành {len(updated_orders)} đơn hàng',
            'updated_orders': updated_orders
        })
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error in auto-complete: {e}")
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500
    except Exception as e:
        print(f"❌ Error in auto-complete: {e}")
        return jsonify({'error': f'Lỗi tự động hoàn thành đơn hàng: {str(e)}'}), 500

@app.route('/admin/api/products', methods=['GET'])
def admin_api_products():
    """API lấy danh sách tất cả sản phẩm cho admin"""
    import requests
    
    try:
        response = requests.get(f'{API_BASE_URL}/products/', timeout=30)
        if response.status_code == 200:
            products = response.json()
            return jsonify(products)
        else:
            return jsonify({'error': 'Không thể lấy danh sách sản phẩm'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

@app.route('/admin/api/products', methods=['POST'])
def admin_api_add_product():
    """API thêm sản phẩm mới cho admin"""
    import requests
    
    try:
        data = request.get_json()
        response = requests.post(f'{API_BASE_URL}/products/', json=data, timeout=30)
        if response.status_code == 201:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Không thể thêm sản phẩm'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

# Customer API Endpoints
@app.route('/admin/api/customers', methods=['GET'])
def admin_api_customers():
    """API lấy danh sách khách hàng cho admin"""
    import requests
    
    try:
        print(f"🔍 Fetching customers from: {API_BASE_URL}/customer/")
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.get(f'{API_BASE_URL}/customer/', headers=headers, timeout=30)
        print(f"📡 Customers API response status: {response.status_code}")
        
        if response.status_code == 200:
            customers = response.json()
            print(f"✅ Successfully fetched {len(customers)} customers")
            return jsonify(customers)
        elif response.status_code == 401:
            print("🔐 Customers API requires authentication, returning empty list")
            return jsonify([])
        else:
            print(f"❌ Customers API error: {response.status_code} - {response.text}")
            return jsonify({'error': f'Không thể lấy danh sách khách hàng. API trả về: {response.status_code}'}), 500
    except requests.exceptions.RequestException as e:
        print(f"❌ Customers API connection error: {e}")
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

@app.route('/admin/api/customers/<int:customer_id>', methods=['GET', 'PATCH'])
def admin_api_customer_detail(customer_id):
    """API chi tiết khách hàng cho admin"""
    import requests
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if request.method == 'GET':
            response = requests.get(f'{API_BASE_URL}/customer/{customer_id}/', headers=headers, timeout=30)
            if response.status_code == 200:
                return jsonify(response.json())
            elif response.status_code == 401:
                return jsonify({'error': 'API yêu cầu xác thực'}), 401
            else:
                return jsonify({'error': 'Không tìm thấy khách hàng'}), 404
                
        elif request.method == 'PATCH':
            data = request.get_json()
            response = requests.patch(f'{API_BASE_URL}/customer/{customer_id}/', 
                                    json=data, headers=headers, timeout=30)
            if response.status_code == 200:
                return jsonify(response.json())
            elif response.status_code == 401:
                return jsonify({'error': 'API yêu cầu xác thực'}), 401
            else:
                return jsonify({'error': 'Không thể cập nhật khách hàng'}), 500
                
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

@app.route('/admin/api/products/<int:product_id>', methods=['PATCH'])
def admin_api_update_product(product_id):
    """API cập nhật sản phẩm cho admin"""
    import requests
    
    try:
        data = request.get_json()
        print(f"🔧 Updating product {product_id} with data: {data}")
        print(f"🔧 Data keys: {list(data.keys()) if data else 'None'}")
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'Không có dữ liệu để cập nhật'}), 400
            
        # Clean up data - remove None values and ensure proper types
        # Only send fields that the Django API can handle for updates
        allowed_fields = {
            'name', 'brand_name', 'original_price', 'discounted_price', 'import_price',
            'stock_quantity', 'sold_quantity', 'status', 'description'
        }
        
        cleaned_data = {}
        for key, value in data.items():
            if key in allowed_fields and value is not None and value != '':
                # Convert data types to match Django API expectations
                if key in ['original_price', 'discounted_price', 'import_price']:
                    try:
                        cleaned_data[key] = float(value)
                    except (ValueError, TypeError):
                        print(f"⚠️ Could not convert {key}={value} to float, skipping")
                        continue
                elif key in ['stock_quantity', 'sold_quantity']:
                    try:
                        cleaned_data[key] = int(value)
                    except (ValueError, TypeError):
                        print(f"⚠️ Could not convert {key}={value} to int, skipping")
                        continue
                else:
                    cleaned_data[key] = str(value)
        
        print(f"🧹 Cleaned data: {cleaned_data}")
        print(f"🧹 Cleaned data keys: {list(cleaned_data.keys())}")
        
        # Try to work around the Django model bug by sending minimal data
        # Start with just the most essential fields that we know work
        minimal_data = {}
        if 'name' in cleaned_data:
            minimal_data['name'] = cleaned_data['name']
        if 'status' in cleaned_data:
            minimal_data['status'] = cleaned_data['status']
        if 'description' in cleaned_data:
            minimal_data['description'] = cleaned_data['description']
        
        print(f"🎯 Trying minimal update with: {minimal_data}")
        
        response = requests.patch(f'{API_BASE_URL}/products/{product_id}/', 
                                json=minimal_data, timeout=30)
        
        # If the minimal update works, try to update additional fields in separate requests
        if response.status_code == 200 and len(cleaned_data) > len(minimal_data):
            print(f"✅ Minimal update successful, trying additional fields...")
            
            # Try to update price fields separately
            price_data = {}
            if 'original_price' in cleaned_data:
                price_data['original_price'] = cleaned_data['original_price']
            if 'discounted_price' in cleaned_data:
                price_data['discounted_price'] = cleaned_data['discounted_price']
            if 'import_price' in cleaned_data:
                price_data['import_price'] = cleaned_data['import_price']
            
            if price_data:
                print(f"💰 Trying price update with: {price_data}")
                price_response = requests.patch(f'{API_BASE_URL}/products/{product_id}/', 
                                              json=price_data, timeout=30)
                if price_response.status_code != 200:
                    print(f"⚠️ Price update failed: {price_response.status_code}")
                else:
                    print(f"✅ Price update successful")
            
            # Try to update quantity fields separately
            quantity_data = {}
            if 'stock_quantity' in cleaned_data:
                quantity_data['stock_quantity'] = cleaned_data['stock_quantity']
            if 'sold_quantity' in cleaned_data:
                quantity_data['sold_quantity'] = cleaned_data['sold_quantity']
            
            if quantity_data:
                print(f"📦 Trying quantity update with: {quantity_data}")
                quantity_response = requests.patch(f'{API_BASE_URL}/products/{product_id}/', 
                                                  json=quantity_data, timeout=30)
                if quantity_response.status_code != 200:
                    print(f"⚠️ Quantity update failed: {quantity_response.status_code}")
                else:
                    print(f"✅ Quantity update successful")
            
            # Get the final updated product data
            final_response = requests.get(f'{API_BASE_URL}/products/{product_id}/', timeout=30)
            if final_response.status_code == 200:
                response = final_response
        
        print(f"📡 API Response status: {response.status_code}")
        if response.status_code != 200:
            print(f"❌ API Error response: {response.text}")
            try:
                error_data = response.json()
                return jsonify({'error': f'API Error: {error_data}'}), response.status_code
            except:
                return jsonify({'error': f'API Error: {response.text}'}), response.status_code
            
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Update successful: {result}")
            return jsonify(result)
        else:
            return jsonify({'error': f'Không thể cập nhật sản phẩm. API trả về: {response.status_code} - {response.text}'}), 500
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return jsonify({'error': f'Lỗi không xác định: {str(e)}'}), 500

@app.route('/api/upload-blog-image', methods=['POST'])
def upload_blog_image():
    """API upload ảnh blog lên Cloudinary"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Không có file được chọn'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Không có file được chọn'}), 400
        
        if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            # Check file size (max 10MB)
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Reset to beginning
            
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                return jsonify({'error': 'File quá lớn. Kích thước tối đa là 10MB'}), 400
            
            # Upload to Cloudinary with image optimization for blog
            upload_result = cloudinary.uploader.upload(
                file,
                folder="blog_images",
                public_id=f"blog_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                resource_type="image",
                # Image optimization settings for blog
                quality="auto:good",  # Chất lượng tốt cho blog
                fetch_format="auto",  # Tự động chọn format tối ưu
                width=1200,  # Giới hạn chiều rộng tối đa
                height=800,  # Giới hạn chiều cao tối đa (tỷ lệ 3:2)
                crop="limit",  # Giữ nguyên tỷ lệ, chỉ resize nếu vượt quá giới hạn
                flags="progressive",  # Tạo ảnh progressive JPEG
                transformation=[
                    {"width": 1200, "height": 800, "crop": "limit"},
                    {"quality": "auto:good"},
                    {"fetch_format": "auto"}
                ]
            )
            
            return jsonify({
                'success': True,
                'url': upload_result['secure_url'],
                'public_id': upload_result['public_id']
            })
        else:
            return jsonify({'error': 'Định dạng file không được hỗ trợ. Chỉ chấp nhận PNG, JPG, JPEG, GIF, WEBP'}), 400
            
    except Exception as e:
        print(f"Error uploading blog image: {str(e)}")
        return jsonify({'error': f'Lỗi upload: {str(e)}'}), 500

@app.route('/api/upload-bank-transfer', methods=['POST'])
def upload_bank_transfer():
    """API upload ảnh chuyển khoản lên Cloudinary"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Không có file được chọn'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Không có file được chọn'}), 400
        
        if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            # Check file size (max 10MB)
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Reset to beginning
            
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                return jsonify({'error': 'File quá lớn. Kích thước tối đa là 10MB'}), 400
            
            # Upload to Cloudinary with image optimization
            upload_result = cloudinary.uploader.upload(
                file,
                folder="bank_transfers",
                public_id=f"transfer_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                resource_type="image",
                # Image optimization settings
                quality="auto:low",  # Tự động giảm chất lượng để giảm dung lượng
                fetch_format="auto",  # Tự động chọn format tối ưu (WebP nếu browser hỗ trợ)
                width=1200,  # Giới hạn chiều rộng tối đa
                height=1200,  # Giới hạn chiều cao tối đa
                crop="limit",  # Giữ nguyên tỷ lệ, chỉ resize nếu vượt quá giới hạn
                flags="progressive",  # Tạo ảnh progressive JPEG
                transformation=[
                    {"width": 1200, "height": 1200, "crop": "limit"},
                    {"quality": "auto:low"},
                    {"fetch_format": "auto"}
                ]
            )
            
            return jsonify({
                'success': True,
                'url': upload_result['secure_url'],
                'public_id': upload_result['public_id']
            })
        else:
            return jsonify({'error': 'File không đúng định dạng. Chỉ chấp nhận: PNG, JPG, JPEG, GIF, WEBP'}), 400
            
    except Exception as e:
        print(f"❌ Error uploading bank transfer image: {e}")
        return jsonify({'error': f'Lỗi upload ảnh: {str(e)}'}), 500

@app.route('/api/product-stock/<int:product_id>')
def api_product_stock(product_id):
    """API lấy thông tin stock của sản phẩm"""
    import requests
    
    try:
        response = requests.get(f'{API_BASE_URL}/products/{product_id}/', timeout=30)
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

@app.route('/api/download-image')
def api_download_image():
    """Proxy download an image URL with Content-Disposition attachment to force save-as.
    Query params:
      - url: required, absolute image URL
      - filename: optional, suggested filename (fallback derives from URL)
    """
    try:
        import requests
        img_url = request.args.get('url', '').strip()
        filename = request.args.get('filename', '').strip()
        if not img_url:
            return jsonify({'error': 'Thiếu tham số url'}), 400

        # Fetch binary with short timeout
        resp = requests.get(img_url, timeout=20, stream=True)
        if resp.status_code != 200:
            return jsonify({'error': f'Không tải được ảnh: {resp.status_code}'}), 502

        # Guess filename
        if not filename:
            try:
                from urllib.parse import urlparse
                import os as _os
                path = urlparse(img_url).path
                base = _os.path.basename(path) or 'image'
                # ensure simple name
                filename = base.split('?')[0] or 'image'
            except Exception:
                filename = 'image'

        # Detect content-type
        content_type = resp.headers.get('Content-Type', 'application/octet-stream')
        data = resp.content
        return send_file(
            BytesIO(data),
            mimetype=content_type,
            as_attachment=True,
            download_name=filename
        )
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Lỗi tải ảnh: {str(e)}'}), 502
    except Exception as e:
        return jsonify({'error': f'Lỗi không xác định: {str(e)}'}), 500

@app.route('/api/send-new-order-notification', methods=['POST'])
def send_new_order_notification():
    """API gửi thông báo đơn hàng mới cho admin"""
    import requests
    
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        
        if not order_id:
            return jsonify({'error': 'Thiếu order_id'}), 400
        
        # Lấy thông tin đơn hàng
        order_response = requests.get(f'{API_BASE_URL}/orders/{order_id}/', timeout=30)
        if order_response.status_code != 200:
            return jsonify({'error': 'Không tìm thấy đơn hàng'}), 404
        
        order = order_response.json()
        
        # Lấy danh sách đơn hàng chờ xác nhận
        orders_response = requests.get(f'{API_BASE_URL}/orders/', timeout=30)
        pending_orders = []
        if orders_response.status_code == 200:
            all_orders = orders_response.json()
            pending_orders = [o for o in all_orders if not o.get('is_confirmed', False)][:10]  # Lấy tối đa 10 đơn hàng
        
        # Render email template
        html_content = render_template('emails/new_order_notification.html', 
                                     order=order, 
                                     pending_orders=pending_orders,
                                     current_time=datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        
        # SMTP configuration
        smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_user = os.getenv('SMTP_USER')
        smtp_pass = os.getenv('SMTP_PASS')
        sender = os.getenv('SMTP_SENDER', smtp_user or 'no-reply@buddyskincare.vn')
        admin_email = os.getenv('ADMIN_EMAIL', 'buddyskincarevn@gmail.com')
        
        if not (smtp_user and smtp_pass):
            # Development fallback: save email HTML to file
            print(f"🔍 SMTP not configured, saving email to file for order {order_id}")
            try:
                fallback_dir = os.path.join(os.getcwd(), 'sent_emails')
                os.makedirs(fallback_dir, exist_ok=True)
                filename = f'new_order_notification_{order_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
                file_path = os.path.join(fallback_dir, filename)
                print(f"🔍 Saving email to: {file_path}")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"✅ Email saved successfully to: {file_path}")
                return jsonify({
                    'success': True, 
                    'message': f'Đã lưu thông báo đơn hàng mới vào file: {file_path}',
                    'saved_path': file_path
                }), 200
            except Exception as e:
                print(f"❌ Error saving email file: {e}")
                return jsonify({'success': False, 'message': f'SMTP chưa cấu hình và lưu file thất bại: {str(e)}'}), 500
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'🔔 Đơn hàng mới #{order_id} cần xác nhận - BuddySkincare'
            msg['From'] = sender
            msg['To'] = admin_email
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(sender, [admin_email], msg.as_string())
            
            return jsonify({
                'success': True, 
                'message': f'Đã gửi thông báo đơn hàng mới đến {admin_email}'
            }), 200
            
        except (smtplib.SMTPAuthenticationError, smtplib.SMTPException, TimeoutError) as e:
            # Graceful fallback: save HTML to file when SMTP fails
            try:
                fallback_dir = os.path.join(os.getcwd(), 'sent_emails')
                os.makedirs(fallback_dir, exist_ok=True)
                filename = f'new_order_notification_{order_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
                file_path = os.path.join(fallback_dir, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                return jsonify({
                    'success': True, 
                    'message': f'Không gửi được qua SMTP, đã lưu thông báo vào file',
                    'saved_path': file_path,
                    'error': str(e)
                }), 200
            except Exception as save_err:
                return jsonify({
                    'success': False, 
                    'message': f'Lỗi SMTP và lưu file thất bại: {str(save_err)}',
                    'error': str(e)
                }), 500
        except Exception as e:
            return jsonify({'success': False, 'message': f'Lỗi gửi email: {str(e)}'}), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Lỗi kết nối API: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Lỗi không xác định: {str(e)}'}), 500

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

# --- CTV Pages (Flask render) ---
@app.route('/ctv/login')
@app.route('/ctv/login/')
def ctv_login_page():
    return render_template('ctv_login.html')


@app.route('/ctv/dashboard')
@app.route('/ctv/dashboard/')
def ctv_dashboard_page():
    return render_template('ctv_dashboard.html')


@app.route('/ctv/wallet')
@app.route('/ctv/wallet/')
def ctv_wallet_page():
    return render_template('ctv_wallet.html')


@app.route('/ctv/orders')
@app.route('/ctv/orders/')
def ctv_orders_page():
    return render_template('ctv_orders.html')


@app.route('/ctv/profile')
@app.route('/ctv/profile/')
def ctv_profile_page():
    return render_template('ctv_profile.html')


@app.route('/ctv/place-order')
@app.route('/ctv/place-order/')
def ctv_place_order_page():
    return render_template('ctv_place_order.html')


@app.route('/ctv/resources')
@app.route('/ctv/resources/')
def ctv_resources_page():
    return render_template('ctv_resources.html')


# --- CTV Auth (server-side session) ---
@app.route('/ctv/auth/login', methods=['POST'])
def ctv_auth_login():
    import requests
    try:
        data = request.get_json(silent=True) or {}
        print(f"🔍 Login attempt: {data}")
        # Login CTV bằng phone và password_text
        resp = requests.post(f"{API_BASE_URL}/ctvs/login/", json=data, timeout=20)
        print(f"🔍 API Response status: {resp.status_code}")
        print(f"🔍 API Response content: {resp.text}")
        
        if resp.status_code != 200:
            return (resp.text, resp.status_code, resp.headers.items())
        payload = resp.json()
        print(f"🔍 API Payload: {payload}")
        
        # Set session với CTV data
        session['ctv'] = payload.get('ctv', {})
        print(f"✅ Session set: {session.get('ctv', {}).get('code', 'Unknown')}")
        print(f"✅ Session data: {session.get('ctv')}")
        
        return jsonify({'success': True, 'ctv': payload.get('ctv', {})})
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return jsonify({'detail': f'Lỗi đăng nhập: {str(e)}'}), 502


@app.route('/ctv/auth/logout')
def ctv_auth_logout():
    session.pop('ctv', None)
    session.pop('access_token', None)
    return redirect('/ctv/login')


@app.before_request
def _guard_ctv_pages():
    path = request.path or ''
    print(f"🔍 Before request - Path: {path}")
    if path.startswith('/ctv/') and not path.startswith('/ctv/login') and not path.startswith('/ctv/auth/'):
        ctv_session = session.get('ctv')
        print(f"🔍 CTV Guard - Path: {path}, Session CTV: {ctv_session}")
        print(f"🔍 Session keys: {list(session.keys())}")
        if not ctv_session:
            print(f"❌ Redirecting to login - No CTV session found")
            return redirect('/ctv/login')
        else:
            print(f"✅ CTV session found: {ctv_session.get('code', 'Unknown')}")
            # Thêm thông tin CTV vào context để template có thể sử dụng
            from flask import g
            g.ctv = ctv_session


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
