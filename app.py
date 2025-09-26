from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, session
import os
from datetime import datetime, timedelta
import secrets
import cloudinary
import cloudinary.uploader
import time
import smtplib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
import requests
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

# Add timestamp helper for cache busting
@app.template_global()
def timestamp():
    return int(time.time())

# API URL for PythonAnywhere
API_BASE_URL = 'https://buddyskincare.vn/backend/api'

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

# Context processor để tạo CSRF token cho templates
@app.context_processor
def inject_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)
    return dict(csrf_token=session['csrf_token'])

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

@app.route('/api/filters/data')
def api_filters_data():
    """API endpoint để lấy dữ liệu filters (danh mục, thương hiệu, tags) - cache để không load lại"""
    try:
        print(f"🔍 Loading REAL filters data from {API_BASE_URL}")

        # Get categories
        try:
            categories_response = requests.get(f"{API_BASE_URL}/category/", timeout=10)
            print(f"🔍 Categories response status: {categories_response.status_code}")
            categories = categories_response.json() if categories_response.status_code == 200 else []
            print(f"🔍 Found {len(categories)} categories")
        except Exception as e:
            print(f"❌ Categories error: {e}")
            categories = []

        # Get brands
        try:
            brands_response = requests.get(f"{API_BASE_URL}/brands/", timeout=10)
            print(f"🔍 Brands response status: {brands_response.status_code}")
            brands = brands_response.json() if brands_response.status_code == 200 else []
            print(f"🔍 Found {len(brands)} brands")
        except Exception as e:
            print(f"❌ Brands error: {e}")
            brands = []

        # Get products for tags (only get first page to avoid timeout)
        try:
            products_response = requests.get(f"{API_BASE_URL}/products/?page=1&per_page=48", timeout=10)
            print(f"🔍 Products response status: {products_response.status_code}")
            products = products_response.json().get('results', []) if products_response.status_code == 200 else []
            print(f"🔍 Found {len(products)} products for tags")
        except Exception as e:
            print(f"❌ Products error: {e}")
            products = []

        # Get tags from products
        all_tags = set()
        for product in products:
            tags = product.get('tags', [])
            if isinstance(tags, list):
                for tag in tags:
                    if isinstance(tag, str) and tag.strip():
                        all_tags.add(tag.strip())
                    elif isinstance(tag, dict) and tag.get('name'):
                        all_tags.add(tag['name'].strip())

        tags_with_stock = sorted(list(all_tags))
        print(f"🔍 Found {len(tags_with_stock)} tags")

        result = {
            'categories': categories,
            'brands': brands,
            'tags': tags_with_stock
        }

        print(f"✅ Returning REAL filters data: {len(result['categories'])} categories, {len(result['brands'])} brands, {len(result['tags'])} tags")
        return jsonify(result)

    except Exception as e:
        print(f"❌ Error in api_filters_data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Lỗi server'}), 500

@app.route('/api/products/filtered')
def api_products_filtered():
    """API endpoint để lấy sản phẩm đã lọc mà không cần reload trang"""
    try:
        # Get filter parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 48, type=int)
        search_query = request.args.get('search', '').strip()
        category_name = request.args.get('category_name', '').strip()
        brands_name = request.args.get('brands_name', '').strip()
        tags = request.args.get('tags', '').strip()
        condition = request.args.get('condition', '').strip()
        price_range = request.args.get('price_range', '').strip()
        discount_range = request.args.get('discount_range', '').strip()
        sort_by = request.args.get('sort', 'newest')

        print(f"🔍 Filtering products with: page={page}, per_page={per_page}, search='{search_query}', category='{category_name}', brand='{brands_name}', tags='{tags}', condition='{condition}', price='{price_range}', discount='{discount_range}', sort='{sort_by}'")

        # Build API URL with filters
        api_params = {
            'page': page,
            'per_page': per_page
        }

        # Add ordering
        if sort_by == 'newest':
            api_params['ordering'] = '-id'
        elif sort_by == 'price_asc':
            api_params['ordering'] = 'discounted_price'
        elif sort_by == 'price_desc':
            api_params['ordering'] = '-discounted_price'
        elif sort_by == 'sales':
            api_params['ordering'] = '-sold_quantity'
        elif sort_by == 'discount':
            api_params['ordering'] = '-discount_rate'

        if search_query:
            api_params['search'] = search_query
        if category_name:
            api_params['category_name'] = category_name
        if brands_name:
            api_params['brands_name'] = brands_name
        if tags:
            api_params['tags'] = tags
        if condition and condition != 'all':
            api_params['condition'] = condition

        # Get products from Django API
        api_url = f"{API_BASE_URL}/products/"
        print(f"🔍 Fetching from: {api_url} with params: {api_params}")
        response = requests.get(api_url, params=api_params, timeout=30)

        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return jsonify({'error': 'Không thể lấy dữ liệu sản phẩm'}), 500

        data = response.json()
        print(f"🔍 Got {len(data.get('results', []))} products from API")

        # Apply client-side filters for price and discount
        filtered_products = data.get('results', [])

        # Price filter (VND)
        if price_range:
            print(f"🔍 DEBUG: Price range filter: {price_range}")
            print(f"🔍 DEBUG: Total products before filter: {len(filtered_products)}")
            def price_vnd(x):
                return (x.get('discounted_price', 0) or 0) * 1000
            if price_range == 'under_200k':
                filtered_products = [p for p in filtered_products if price_vnd(p) < 200_000]
                print(f"🔍 DEBUG: Products under 200k: {len(filtered_products)}")
            elif price_range == '200_500':
                filtered_products = [p for p in filtered_products if 200_000 <= price_vnd(p) < 500_000]
            elif price_range == '500_1m':
                filtered_products = [p for p in filtered_products if 500_000 <= price_vnd(p) < 1_000_000]
            elif price_range == 'over_1m':
                filtered_products = [p for p in filtered_products if price_vnd(p) >= 1_000_000]

        # Discount filter
        if discount_range:
            def discount_rate(p):
                return float(p.get('discount_rate', 0) or 0)
            if discount_range == 'under_30':
                filtered_products = [p for p in filtered_products if discount_rate(p) < 30]
            elif discount_range == '50_70':
                filtered_products = [p for p in filtered_products if 50 <= discount_rate(p) < 70]
            elif discount_range == 'over_70':
                filtered_products = [p for p in filtered_products if discount_rate(p) >= 70]

        # Update data with filtered results
        data['results'] = filtered_products
        data['count'] = len(filtered_products)

        print(f"✅ Returning REAL products data: {len(filtered_products)} products")
        return jsonify(data)

    except Exception as e:
        print(f"❌ Error in api_products_filtered: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Lỗi server'}), 500

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

    # Hỗ trợ tên tham số mới theo yêu cầu - hỗ trợ multiple values
    category_names = request.args.getlist('category_name') or ([category] if category else [])
    brands_names = request.args.getlist('brands_name') or ([brand] if brand else [])
    new_price_range = request.args.get('price_range') or price_range
    new_discount = request.args.get('discount_range') or discount
    tags_filter = request.args.get('tags')

    # Filter sản phẩm
    filtered_products = all_products.copy()

    # Filter by multiple categories
    if category_names:
        category_targets = [name.strip().lower() for name in category_names if name.strip()]
        if category_targets:
            filtered_products = [p for p in filtered_products if _extract_category_name(p).lower() in category_targets]

    # Filter by multiple brands
    if brands_names:
        brand_targets = [name.strip() for name in brands_names if name.strip()]
        if brand_targets:
            filtered_products = [p for p in filtered_products if (p.get('brand_name') or (p.get('brand') or {}).get('name') or '').strip() in brand_targets]

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
        print(f"🔍 DEBUG: Price range filter: {new_price_range}")
        print(f"🔍 DEBUG: Total products before filter: {len(filtered_products)}")
        def price_vnd(x):
            return (x.get('discounted_price', 0) or 0) * 1000
        if new_price_range == 'under_200k':
            filtered_products = [p for p in filtered_products if price_vnd(p) < 200_000]
            print(f"🔍 DEBUG: Products under 200k: {len(filtered_products)}")
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

    # Pagination logic
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 48, type=int)

    # Calculate pagination
    total_products = len(filtered_products)
    total_pages = (total_products + per_page - 1) // per_page

    # Get products for current page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_products = filtered_products[start_idx:end_idx]

    # Check if this is an AJAX request
    is_ajax = request.args.get('ajax') == '1'

    if is_ajax:
        # Return only the products grid HTML for AJAX requests
        from flask import render_template_string
        return render_template_string('''
            <div id="products-page-grid" class="row g-4">
                {% for product in products %}
                <div class="col-6 col-md-4 col-lg-3">
                    {% set image_url = product.image or '/static/image/default-product.jpg' %}
                    {% set brand_name = product.brand_name or 'Không rõ' %}
                    {% set status_text = (product.status or '').lower() %}
                    {% set is_new_by_status = 'new' in status_text or 'chiet' in status_text %}
                    {% set remaining_percent = None %}
                    {% if not is_new_by_status %}
                        {% set remaining_percent = None %}
                    {% endif %}
                    {% set used_label = None %}
                    {% if not is_new_by_status %}
                        {% if 'test' in status_text %}
                            {% set used_label = 'Test 1-2 lần' %}
                        {% elif remaining_percent %}
                            {% set used_label = 'Còn ' + remaining_percent + '%' %}
                        {% endif %}
                    {% endif %}
                    {% set new_label = None %}
                    {% if is_new_by_status %}
                        {% if 'chiet' in status_text %}
                            {% set new_label = 'Chiết' %}
                        {% elif status_text == 'new' %}
                            {% set new_label = 'New đẹp' %}
                        {% elif 'newmh' in status_text %}
                            {% set new_label = 'New mất hộp' %}
                        {% elif 'newm' in status_text %}
                            {% set new_label = 'New móp hộp' %}
                        {% elif 'newrt' in status_text %}
                            {% set new_label = 'New rách tem' %}
                        {% elif 'newmn' in status_text %}
                            {% set new_label = 'New móp nhẹ' %}
                        {% elif 'newx' in status_text %}
                            {% set new_label = 'New xước nhẹ' %}
                        {% elif 'newspx' in status_text %}
                            {% set new_label = 'New xước' %}
                        {% else %}
                            {% set new_label = 'New' %}
                        {% endif %}
                    {% endif %}
                    {% set info_label = new_label if is_new_by_status else used_label %}
                    {% set original_price = product.original_price * 1000 if product.original_price else None %}
                    {% set discounted_price = product.discounted_price * 1000 if product.discounted_price else 0 %}
                    {% set rating = product.rating | float if product.rating else 0 %}
                    {% set full_stars = rating | int %}
                    {% set has_half_star = (rating % 1) >= 0.5 and (rating % 1) < 1 %}
                    {% set discount_rate = (product.discount_rate | float | round | int) if product.discount_rate else 0 %}
                    {% set stock_quantity = product.stock_quantity or 0 %}
                    {% set is_out_of_stock = stock_quantity <= 0 %}

                    <div class="product-card card h-100 border-0 shadow-sm">
                        <div class="position-relative">
                            <a href="/product/{{ product.id }}" class="text-decoration-none">
                                <img src="{{ image_url }}"
                                     class="card-img-top" alt="{{ product.name }}"
                                     style="height: 220px; object-fit: cover;{% if is_out_of_stock %} filter: grayscale(100%);{% endif %}"
                                     onerror="this.src='/static/image/default-product.jpg'">
                            </a>
                            {% if is_out_of_stock %}
                            <div class="position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center"
                                 style="background-color: rgba(0,0,0,0.7); border-radius: 6px;">
                                <div class="text-center text-white">
                                    <i class="fas fa-times-circle fa-2x mb-1"></i>
                                    <h6 class="fw-bold mb-0">HẾT HÀNG</h6>
                                </div>
                            </div>
                            {% endif %}
                            <button class="fav-toggle position-absolute top-0 end-0 m-2"
                                    title="Thêm vào yêu thích"
                                    data-id="{{ product.id }}"
                                    data-name="{{ product.name }}"
                                    data-image="{{ image_url }}"
                                    data-brand="{{ brand_name }}"
                                    data-price="{{ discounted_price }}"
                                    style="border:none;background:transparent;cursor:pointer;">
                                <i class="far fa-heart" style="font-size: 18px; color:#fff; text-shadow: 0 1px 3px rgba(0,0,0,0.5);"></i>
                            </button>
                            <div class="position-absolute bottom-0 start-0 m-1">
                                <img src="/static/image/logo.png" alt="Logo" class="product-logo" style="width: 28px; height: 28px; object-fit: contain; border-radius: 50%; background: white; padding: 2px; display: block; z-index: 10; box-shadow: 0 1px 3px rgba(0,0,0,0.2);" onerror="this.style.display='none';">
                            </div>
                            <div class="product-badges-row position-absolute" style="top:8px;left:10px;display:flex;gap:6px;align-items:center;z-index:2;">
                                {% if discount_rate > 0 %}
                                <div class="badge bg-danger discount-badge-left" style="font-size: 11px; padding: 4px 8px;">-{{ discount_rate }}%</div>
                                {% endif %}
                                {% if info_label %}
                                <div class="product-info-badge" style="font-size: 10px; padding: 1px 6px; background:#eaf4ff; border:1px solid #b8d4ff; color:#1e56a0; border-radius:6px;"><i class="fas fa-circle-info me-1"></i>{{ info_label }}</div>
                                {% endif %}
                            </div>
                        </div>
                        <div class="card-body d-flex flex-column">
                            <h6 class="card-title fw-bold" style="font-size: 12px; line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; height: 16px;">
                                <a href="/product/{{ product.id }}" class="text-decoration-none text-dark">{{ product.name }}</a>
                            </h6>
                            <p class="text-muted small mb-2" style="font-size: 10px;">{{ brand_name }}{% if info_label %} • {{ info_label }}{% endif %}</p>
                            <div class="d-flex align-items-center mb-1">
                                {% if original_price %}
                                <span class="text-decoration-line-through text-muted me-1" style="font-size: 11px;">{{ "{:,.0f}".format(original_price) }}đ</span>
                                {% endif %}
                                <span class="text-danger fw-bold" style="font-size: 15px;">{{ "{:,.0f}".format(discounted_price) }}đ</span>
                            </div>
                            <div class="d-flex align-items-center mb-3">
                                <div class="stars text-warning me-2" style="font-size: 12px;">
                                    {% for i in range(5) %}
                                        {% if i < full_stars %}
                                        <i class="fas fa-star"></i>
                                        {% elif i == full_stars and has_half_star %}
                                        <i class="fas fa-star-half-alt"></i>
                                        {% else %}
                                        <i class="far fa-star"></i>
                                        {% endif %}
                                    {% endfor %}
                                </div>
                                <small class="text-muted" style="font-size: 11px;">({{ rating }})</small>
                                <span class="badge {% if is_out_of_stock %}bg-danger{% else %}bg-success{% endif %}" style="font-size: 10px; padding: 4px 8px; margin-left: 10px;">{% if is_out_of_stock %}Hết hàng{% else %}Còn {{ stock_quantity }}{% endif %}</span>
                            </div>
                            <button class="btn w-100 add-to-cart-btn {% if is_out_of_stock %}btn-secondary{% else %}btn-light text-dark border{% endif %}"
                                    data-product-id="{{ product.id }}"
                                    style="font-size: 13px; padding: 8px;"
                                    {% if is_out_of_stock %}disabled{% endif %}>
                                {% if is_out_of_stock %}Hết hàng{% else %}Thêm vào giỏ{% endif %}
                            </button>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            <div id="products-showing">{{ products|length }}</div>
            <div id="products-total">{{ total_products }}</div>
        ''', products=paginated_products, total_products=total_products)

    return render_template('products.html',
                         products=paginated_products,
                         total_products=total_products,
                         total_pages=total_pages,
                         current_page=page,
                         per_page=per_page,
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

@app.route('/favicon.ico')
def favicon():
    try:
        return send_file('static/favicon.ico', mimetype='image/vnd.microsoft.icon')
    except FileNotFoundError:
        # Fallback to logo if favicon doesn't exist
        return send_file('static/image/logo.png', mimetype='image/png')
    except Exception as e:
        print(f"Error serving favicon: {e}")
        return '', 204  # No content

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

    # SMTP configuration from Django settings
    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER') or 'buddyskincarevn@gmail.com'
    smtp_pass = os.getenv('SMTP_PASS') or 'fkoz aohr yeub fncz'
    sender = os.getenv('SMTP_SENDER', smtp_user or 'buddyskincarevn@gmail.com')

    # Try Gmail API first, then SMTP, then fallback to file
    email_sent = False
    
    # Try Gmail API
    try:
        email_sent = send_email_via_gmail_api(
            to_email=recipient,
            subject=f'Hóa đơn đơn hàng #{order_id} - BuddySkincare',
            html_content=html_content,
            plain_text=f'Hóa đơn đơn hàng #{order_id} từ BuddySkincare'
        )
    except Exception as e:
        print(f"❌ Gmail API failed: {e}")
    
    # If Gmail API failed, try SMTP
    if not email_sent and (smtp_user and smtp_pass):
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'Hóa đơn đơn hàng #{order_id} - BuddySkincare'
            msg['From'] = sender
            msg['To'] = recipient
            
            # Add plain text version
            text_content = f'Hóa đơn đơn hàng #{order_id} từ BuddySkincare'
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # Add HTML version
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Send email
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            server.quit()
            
            email_sent = True
            print(f"✅ Email sent via SMTP to {recipient}")
        except Exception as e:
            print(f"❌ SMTP failed: {e}")
    
    # If both failed, save to file
    if not email_sent:
        try:
            fallback_dir = os.path.join(os.getcwd(), 'sent_emails')
            os.makedirs(fallback_dir, exist_ok=True)
            filename = f'invoice_{order_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            file_path = os.path.join(fallback_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return jsonify({'success': True, 'message': f'Đã lưu hóa đơn vào file: {file_path}', 'saved_path': file_path}), 200
        except Exception as e:
            return jsonify({'success': False, 'message': f'Gửi email thất bại và lưu file thất bại: {str(e)}'}), 500

    # Return success if email was sent
    if email_sent:
        return jsonify({'success': True, 'message': f'Đã gửi hóa đơn đến {recipient}'}), 200
    else:
        return jsonify({'success': False, 'message': 'Không thể gửi email'}), 500

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

def send_email_via_gmail_api(to_email, subject, html_content, plain_text=None):
    """Gửi email qua Gmail API"""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        credentials_path = os.path.join(os.getcwd(), 'gmail-credentials.json')
        if not os.path.exists(credentials_path):
            print("❌ Gmail credentials not found")
            return False
            
        # Initialize Gmail service with send scope
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/gmail.send']
        )
        
        service = build('gmail', 'v1', credentials=credentials)
        
        # Create message
        message = MIMEMultipart('alternative')
        message['to'] = to_email
        message['from'] = 'buddyskincarevn@gmail.com'
        message['subject'] = subject
        
        # Add plain text version if provided
        if plain_text:
            text_part = MIMEText(plain_text, 'plain', 'utf-8')
            message.attach(text_part)
        
        # Add HTML version
        html_part = MIMEText(html_content, 'html', 'utf-8')
        message.attach(html_part)
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send email
        result = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        print(f"✅ Email sent successfully to {to_email}, message ID: {result['id']}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email via Gmail API: {e}")
        return False

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

# Orders API Endpoints
@app.route('/orders/', methods=['GET'])
def api_orders():
    """API lấy danh sách đơn hàng (public endpoint for CTV orders)"""
    import requests

    try:
        # Get query parameters
        collaborator_code = request.args.get('collaborator_code__isnull', '')
        ctv_code = request.args.get('collaborator_code', '')
        start_date = request.args.get('order_date__gte', '')
        end_date = request.args.get('order_date__lte', '')

        print(f"🔍 Fetching orders from: {API_BASE_URL}/orders/")
        print(f"📋 Query params: collaborator_code__isnull={collaborator_code}, collaborator_code={ctv_code}")

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        # Build query URL
        query_params = []
        if collaborator_code == 'false':
            query_params.append('collaborator_code__isnull=false')
        if ctv_code:
            query_params.append(f'collaborator_code={ctv_code}')
        if start_date:
            query_params.append(f'order_date__gte={start_date}')
        if end_date:
            query_params.append(f'order_date__lte={end_date}')

        query_string = '&'.join(query_params)
        url = f'{API_BASE_URL}/orders/?ordering=-order_date'
        if query_string:
            url += f'&{query_string}'

        print(f"📡 Full URL: {url}")

        response = requests.get(url, headers=headers, timeout=30)
        print(f"📡 Orders API response status: {response.status_code}")

        if response.status_code == 200:
            orders = response.json()
            print(f"✅ Successfully fetched {len(orders)} orders")
            return jsonify(orders)
        else:
            print(f"❌ Orders API error: {response.status_code} - {response.text}")
            return jsonify({'error': f'Không thể lấy danh sách đơn hàng. API trả về: {response.status_code}'}), 500
    except requests.exceptions.RequestException as e:
        print(f"❌ Orders API connection error: {e}")
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

# CTVs API Endpoints
@app.route('/ctvs/', methods=['GET'])
def api_ctvs():
    """API lấy danh sách CTV"""
    import requests

    try:
        print(f"🔍 Fetching CTVs from: {API_BASE_URL}/ctvs/")

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.get(f'{API_BASE_URL}/ctvs/', headers=headers, timeout=30)
        print(f"📡 CTVs API response status: {response.status_code}")

        if response.status_code == 200:
            ctvs = response.json()
            print(f"✅ Successfully fetched {len(ctvs)} CTVs")
            return jsonify(ctvs)
        else:
            print(f"❌ CTVs API error: {response.status_code} - {response.text}")
            return jsonify({'error': f'Không thể lấy danh sách CTV. API trả về: {response.status_code}'}), 500
    except requests.exceptions.RequestException as e:
        print(f"❌ CTVs API connection error: {e}")
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

@app.route('/ctvs/by-code/', methods=['GET'])
def api_ctvs_by_code():
    """API lấy CTV theo mã"""
    import requests

    try:
        code = request.args.get('code', '').strip()
        if not code:
            return jsonify({'error': 'Thiếu mã CTV'}), 400

        print(f"🔍 Fetching CTV by code: {code} from: {API_BASE_URL}/ctvs/by-code/")

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.get(f'{API_BASE_URL}/ctvs/by-code/?code={code}', headers=headers, timeout=30)
        print(f"📡 CTV by code API response status: {response.status_code}")

        if response.status_code == 200:
            ctv = response.json()
            print(f"✅ Successfully fetched CTV: {ctv.get('code', 'N/A')}")
            return jsonify(ctv)
        elif response.status_code == 404:
            print(f"❌ CTV not found with code: {code}")
            return jsonify({'error': 'Không tìm thấy CTV với mã này'}), 404
        else:
            print(f"❌ CTV by code API error: {response.status_code} - {response.text}")
            return jsonify({'error': f'Không thể lấy thông tin CTV. API trả về: {response.status_code}'}), 500
    except requests.exceptions.RequestException as e:
        print(f"❌ CTV by code API connection error: {e}")
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

@app.route('/ctvs/<int:ctv_id>/stats/', methods=['GET'])
def api_ctv_stats(ctv_id):
    """API lấy thống kê CTV"""
    import requests

    try:
        print(f"🔍 Fetching CTV stats for ID: {ctv_id} from: {API_BASE_URL}/ctvs/{ctv_id}/stats/")

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.get(f'{API_BASE_URL}/ctvs/{ctv_id}/stats/', headers=headers, timeout=30)
        print(f"📡 CTV stats API response status: {response.status_code}")

        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Successfully fetched CTV stats for ID: {ctv_id}")
            return jsonify(stats)
        elif response.status_code == 404:
            print(f"❌ CTV stats not found for ID: {ctv_id}")
            return jsonify({'error': 'Không tìm thấy thống kê CTV'}), 404
        else:
            print(f"❌ CTV stats API error: {response.status_code} - {response.text}")
            return jsonify({'error': f'Không thể lấy thống kê CTV. API trả về: {response.status_code}'}), 500
    except requests.exceptions.RequestException as e:
        print(f"❌ CTV stats API connection error: {e}")
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

@app.route('/ctvs/<int:ctv_id>/commissions/', methods=['GET'])
def api_ctv_commissions(ctv_id):
    """API lấy danh sách hoa hồng CTV"""
    import requests

    try:
        print(f"🔍 Fetching CTV commissions for ID: {ctv_id} from: {API_BASE_URL}/ctvs/{ctv_id}/commissions/")

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.get(f'{API_BASE_URL}/ctvs/{ctv_id}/commissions/', headers=headers, timeout=30)
        print(f"📡 CTV commissions API response status: {response.status_code}")

        if response.status_code == 200:
            commissions = response.json()
            print(f"✅ Successfully fetched CTV commissions for ID: {ctv_id}")
            return jsonify(commissions)
        elif response.status_code == 404:
            print(f"❌ CTV commissions not found for ID: {ctv_id}")
            return jsonify({'error': 'Không tìm thấy hoa hồng CTV'}), 404
        else:
            print(f"❌ CTV commissions API error: {response.status_code} - {response.text}")
            return jsonify({'error': f'Không thể lấy hoa hồng CTV. API trả về: {response.status_code}'}), 500
    except requests.exceptions.RequestException as e:
        print(f"❌ CTV commissions API connection error: {e}")
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

@app.route('/ctvs/<int:ctv_id>/wallet/', methods=['GET'])
def api_ctv_wallet(ctv_id):
    """API lấy thông tin ví CTV"""
    import requests

    try:
        print(f"🔍 Fetching CTV wallet for ID: {ctv_id} from: {API_BASE_URL}/ctvs/{ctv_id}/wallet/")

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.get(f'{API_BASE_URL}/ctvs/{ctv_id}/wallet/', headers=headers, timeout=30)
        print(f"📡 CTV wallet API response status: {response.status_code}")

        if response.status_code == 200:
            wallet = response.json()
            print(f"✅ Successfully fetched CTV wallet for ID: {ctv_id}")
            return jsonify(wallet)
        elif response.status_code == 404:
            print(f"❌ CTV wallet not found for ID: {ctv_id}")
            return jsonify({'error': 'Không tìm thấy ví CTV'}), 404
        else:
            print(f"❌ CTV wallet API error: {response.status_code} - {response.text}")
            return jsonify({'error': f'Không thể lấy ví CTV. API trả về: {response.status_code}'}), 500
    except requests.exceptions.RequestException as e:
        print(f"❌ CTV wallet API connection error: {e}")
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

@app.route('/ctvs/<int:ctv_id>/withdrawals/', methods=['GET'])
def api_ctv_withdrawals(ctv_id):
    """API lấy lịch sử rút tiền CTV"""
    import requests

    try:
        print(f"🔍 Fetching CTV withdrawals for ID: {ctv_id} from: {API_BASE_URL}/ctvs/{ctv_id}/withdrawals/")

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.get(f'{API_BASE_URL}/ctvs/{ctv_id}/withdrawals/', headers=headers, timeout=30)
        print(f"📡 CTV withdrawals API response status: {response.status_code}")

        if response.status_code == 200:
            withdrawals = response.json()
            print(f"✅ Successfully fetched CTV withdrawals for ID: {ctv_id}")
            return jsonify(withdrawals)
        elif response.status_code == 404:
            print(f"❌ CTV withdrawals not found for ID: {ctv_id}")
            return jsonify({'error': 'Không tìm thấy lịch sử rút tiền CTV'}), 404
        else:
            print(f"❌ CTV withdrawals API error: {response.status_code} - {response.text}")
            return jsonify({'error': f'Không thể lấy lịch sử rút tiền CTV. API trả về: {response.status_code}'}), 500
    except requests.exceptions.RequestException as e:
        print(f"❌ CTV withdrawals API connection error: {e}")
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

@app.route('/ctvs/<int:ctv_id>/withdraw/', methods=['POST'])
def api_ctv_withdraw(ctv_id):
    """API gửi yêu cầu rút tiền CTV"""
    import requests

    try:
        print(f"🔍 Sending CTV withdrawal request for ID: {ctv_id} to: {API_BASE_URL}/ctvs/{ctv_id}/withdraw/")

        # Lấy dữ liệu từ request body
        data = request.get_json()
        print(f"📋 Withdrawal data: {data}")

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.post(f'{API_BASE_URL}/ctvs/{ctv_id}/withdraw/', json=data, headers=headers, timeout=30)
        print(f"📡 CTV withdraw API response status: {response.status_code}")

        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print(f"✅ Successfully sent CTV withdrawal request for ID: {ctv_id}")
            return jsonify(result)
        elif response.status_code == 400:
            error_data = response.json()
            print(f"❌ CTV withdraw validation error: {error_data}")
            return jsonify({'error': error_data.get('detail', 'Dữ liệu không hợp lệ')}), 400
        elif response.status_code == 404:
            print(f"❌ CTV not found for withdrawal ID: {ctv_id}")
            return jsonify({'error': 'Không tìm thấy CTV'}), 404
        else:
            print(f"❌ CTV withdraw API error: {response.status_code} - {response.text}")
            return jsonify({'error': f'Không thể gửi yêu cầu rút tiền. API trả về: {response.status_code}'}), 500
    except requests.exceptions.RequestException as e:
        print(f"❌ CTV withdraw API connection error: {e}")
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

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
                                data=update_data,
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
        response = requests.get(f'{API_BASE_URL}/admin-products/', timeout=30)
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
        response = requests.post(f'{API_BASE_URL}/admin-products/', json=data, timeout=30)
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
            'stock_quantity', 'sold_quantity', 'status', 'description', 'is_visible'
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
                elif key == 'is_visible':
                    # Handle boolean field
                    cleaned_data[key] = bool(value)
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
        if 'is_visible' in cleaned_data:
            minimal_data['is_visible'] = cleaned_data['is_visible']

        print(f"🎯 Trying minimal update with: {minimal_data}")

        response = requests.patch(f'{API_BASE_URL}/admin-products/{product_id}/',
                                data=minimal_data, timeout=30)

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
                price_response = requests.patch(f'{API_BASE_URL}/admin-products/{product_id}/',
                                              data=price_data, timeout=30)
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
                quantity_response = requests.patch(f'{API_BASE_URL}/admin-products/{product_id}/',
                                                  data=quantity_data, timeout=30)
                if quantity_response.status_code != 200:
                    print(f"⚠️ Quantity update failed: {quantity_response.status_code}")
                else:
                    print(f"✅ Quantity update successful")

            # Get the final updated product data
            final_response = requests.get(f'{API_BASE_URL}/admin-products/{product_id}/', timeout=30)
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

@app.route('/admin/api/products/<int:product_id>', methods=['DELETE'])
def admin_api_delete_product(product_id):
    """API xóa sản phẩm cho admin"""
    import requests

    try:
        print(f"🗑️ Deleting product {product_id}")
        
        response = requests.delete(f'{API_BASE_URL}/admin-products/{product_id}/', timeout=30)
        
        if response.status_code == 204:
            print(f"✅ Product {product_id} deleted successfully")
            return jsonify({'success': True, 'message': 'Sản phẩm đã được xóa thành công'})
        elif response.status_code == 404:
            return jsonify({'error': 'Không tìm thấy sản phẩm'}), 404
        else:
            print(f"❌ Delete failed: {response.status_code} - {response.text}")
            return jsonify({'error': f'Không thể xóa sản phẩm. API trả về: {response.status_code}'}), response.status_code

    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return jsonify({'error': f'Lỗi không xác định: {str(e)}'}), 500

@app.route('/backend/api/products/<int:product_id>/remove_tag/', methods=['POST'])
def remove_product_tag(product_id):
    """API xóa tag khỏi sản phẩm"""
    import requests

    try:
        data = request.get_json()
        tag_name = data.get('tag_name', 'FlashSale')
        
        print(f"🏷️ Removing tag '{tag_name}' from product {product_id}")
        
        # Gọi Django API để xóa tag
        response = requests.post(
            f'{API_BASE_URL}/products/{product_id}/remove_tag/',
            json={'tag_name': tag_name},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Successfully removed tag '{tag_name}' from product {product_id}")
            return jsonify({
                'success': True,
                'message': f'Đã xóa tag "{tag_name}" khỏi sản phẩm',
                'data': result
            })
        elif response.status_code == 404:
            print(f"❌ Product {product_id} not found")
            return jsonify({'error': 'Không tìm thấy sản phẩm'}), 404
        else:
            print(f"❌ Failed to remove tag: {response.status_code} - {response.text}")
            return jsonify({'error': 'Không thể xóa tag khỏi sản phẩm'}), 500
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return jsonify({'error': f'Lỗi không xác định: {str(e)}'}), 500

@app.route('/backend/api/products/<int:product_id>/add_tag/', methods=['POST'])
def add_product_tag(product_id):
    """API thêm tag vào sản phẩm"""
    import requests

    try:
        data = request.get_json()
        tag_name = data.get('tag_name', 'FlashSale')
        
        print(f"🏷️ Adding tag '{tag_name}' to product {product_id}")
        
        # Gọi Django API để thêm tag
        response = requests.post(
            f'{API_BASE_URL}/products/{product_id}/add_tag/',
            json={'tag_name': tag_name},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Successfully added tag '{tag_name}' to product {product_id}")
            return jsonify({
                'success': True,
                'message': f'Đã thêm tag "{tag_name}" vào sản phẩm',
                'data': result
            })
        elif response.status_code == 404:
            print(f"❌ Product {product_id} not found")
            return jsonify({'error': 'Không tìm thấy sản phẩm'}), 404
        else:
            print(f"❌ Failed to add tag: {response.status_code} - {response.text}")
            return jsonify({'error': 'Không thể thêm tag vào sản phẩm'}), 500
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return jsonify({'error': f'Lỗi không xác định: {str(e)}'}), 500

@app.route('/backend/api/products/add_tag/', methods=['POST'])
def add_products_to_tag():
    """API thêm nhiều sản phẩm vào tag"""
    import requests

    try:
        data = request.get_json()
        tag_name = data.get('tag_name', 'FlashSale')
        product_ids = data.get('product_ids', [])
        
        if not product_ids:
            return jsonify({'error': 'Không có sản phẩm nào được chọn'}), 400
        
        print(f"🏷️ Adding tag '{tag_name}' to products: {product_ids}")
        
        success_count = 0
        errors = []
        
        # Thêm tag cho từng sản phẩm
        for product_id in product_ids:
            try:
                response = requests.post(
                    f'{API_BASE_URL}/products/{product_id}/add_tag/',
                    json={'tag_name': tag_name},
                    timeout=30
                )
                
                if response.status_code == 200:
                    success_count += 1
                else:
                    errors.append(f"Sản phẩm {product_id}: {response.status_code}")
            except Exception as e:
                errors.append(f"Sản phẩm {product_id}: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': f'Đã thêm tag "{tag_name}" cho {success_count}/{len(product_ids)} sản phẩm',
            'success_count': success_count,
            'total_count': len(product_ids),
            'errors': errors
        })
        
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
        print(f"🔍 Upload request received. Files: {list(request.files.keys())}")
        
        if 'file' not in request.files:
            print("❌ No file in request")
            return jsonify({'error': 'Không có file được chọn'}), 400

        file = request.files['file']
        print(f"📁 File received: {file.filename}, Content type: {file.content_type}")
        
        if file.filename == '':
            print("❌ Empty filename")
            return jsonify({'error': 'Không có file được chọn'}), 400

        # Check file extension
        allowed_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.webp')
        if not file.filename.lower().endswith(allowed_extensions):
            print(f"❌ Invalid file extension: {file.filename}")
            return jsonify({'error': 'File không đúng định dạng. Chỉ chấp nhận: PNG, JPG, JPEG, GIF, WEBP'}), 400

        # Check file size (max 10MB)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        print(f"📏 File size: {file_size} bytes")

        if file_size > 10 * 1024 * 1024:  # 10MB limit
            print(f"❌ File too large: {file_size} bytes")
            return jsonify({'error': 'File quá lớn. Kích thước tối đa là 10MB'}), 400

        # Check Cloudinary configuration
        try:
            import cloudinary
            print(f"☁️ Cloudinary configured: {cloudinary.config().cloud_name}")
        except Exception as config_error:
            print(f"❌ Cloudinary config error: {config_error}")
            return jsonify({'error': 'Lỗi cấu hình Cloudinary'}), 500

        # Upload to Cloudinary with simplified settings
        print("🚀 Starting Cloudinary upload...")
        upload_result = cloudinary.uploader.upload(
            file,
            folder="bank_transfers",
            public_id=f"transfer_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            resource_type="image",
            quality="auto",
            fetch_format="auto"
        )

        print(f"✅ Upload successful: {upload_result.get('secure_url', 'No URL')}")
        return jsonify({
            'success': True,
            'url': upload_result['secure_url'],
            'public_id': upload_result['public_id']
        })

    except Exception as e:
        print(f"❌ Error uploading bank transfer image: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Lỗi upload ảnh: {str(e)}'}), 500

@app.route('/api/ctv-applications/', methods=['POST'])
def api_ctv_applications():
    """API proxy cho đăng ký CTV - forward đến Django backend"""
    import requests
    
    try:
        # Forward request đến Django backend
        django_url = f'{API_BASE_URL}/ctv-applications/'
        
        # Lấy dữ liệu từ request
        data = request.get_json()
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        print(f"🔍 Forwarding CTV application to: {django_url}")
        print(f"📝 Data: {data}")
        
        response = requests.post(django_url, json=data, headers=headers, timeout=30)
        
        print(f"📡 Django response status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ CTV application submitted successfully")
            return jsonify(result)
        else:
            print(f"❌ Django API error: {response.status_code} - {response.text}")
            return jsonify({'error': f'Đăng ký thất bại. API trả về: {response.status_code}'}), response.status_code
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Django API connection error: {e}")
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500
    except Exception as e:
        print(f"❌ CTV application error: {e}")
        return jsonify({'error': f'Lỗi hệ thống: {str(e)}'}), 500

@app.route('/api/upload-marketing-resources-bulk', methods=['POST'])
def upload_marketing_resources_bulk():
    """API upload nhiều ảnh tài nguyên marketing lên Cloudinary hàng loạt"""
    try:
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            return jsonify({'error': 'Không có file nào được chọn'}), 400

        # Get form data
        resource_type = request.form.get('resource_type', 'new_product')
        description = request.form.get('description', '')
        is_active = request.form.get('is_active') == 'on'

        results = []
        errors = []

        for i, file in enumerate(files):
            try:
                if file.filename == '':
                    errors.append(f"File {i+1}: Tên file trống")
                    continue

                # Check file extension
                if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.pdf', '.doc', '.docx')):
                    errors.append(f"File {i+1} ({file.filename}): Định dạng không hỗ trợ")
                    continue

                # Check file size (max 10MB)
                file.seek(0, 2)  # Seek to end
                file_size = file.tell()
                file.seek(0)  # Reset to beginning

                if file_size > 10 * 1024 * 1024:
                    errors.append(f"File {i+1} ({file.filename}): Quá lớn ({file_size/1024/1024:.1f}MB)")
                    continue

                # Upload to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    file,
                    folder="marketing_resources",
                    public_id=f"resource_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}_{file.filename.split('.')[0]}",
                    resource_type="image" if file.content_type.startswith('image/') else "raw",
                    quality="auto:good" if file.content_type.startswith('image/') else None,
                    fetch_format="auto" if file.content_type.startswith('image/') else None,
                    width=2000 if file.content_type.startswith('image/') else None,
                    height=2000 if file.content_type.startswith('image/') else None,
                    crop="limit" if file.content_type.startswith('image/') else None,
                    flags="progressive" if file.content_type.startswith('image/') else None
                )

                # Create MarketingResource record via API
                resource_data = {
                    'name': file.filename.rsplit('.', 1)[0],  # Remove extension
                    'description': description,
                    'resource_type': resource_type,
                    'file_url': upload_result['secure_url'],
                    'thumbnail_url': upload_result['secure_url'],
                    'file_size': upload_result.get('bytes', file_size),
                    'is_active': is_active
                }

                # Call Django API to create resource record
                import requests
                api_response = requests.post(
                    f'{API_BASE_URL}/marketing-resources/',
                    json=resource_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )

                if api_response.status_code in [200, 201]:
                    results.append({
                        'filename': file.filename,
                        'url': upload_result['secure_url'],
                        'status': 'success'
                    })
                    print(f"✅ Successfully processed: {file.filename}")
                else:
                    errors.append(f"File {i+1} ({file.filename}): Lỗi tạo record ({api_response.status_code})")
                    print(f"❌ Failed to create record for: {file.filename}")

            except Exception as file_error:
                errors.append(f"File {i+1} ({file.filename}): {str(file_error)}")
                print(f"❌ Error processing {file.filename}: {str(file_error)}")

        return jsonify({
            'success': True,
            'total_files': len(files),
            'successful_uploads': len(results),
            'errors': errors,
            'results': results,
            'message': f'Upload hoàn tất: {len(results)}/{len(files)} file thành công'
        })

    except Exception as e:
        print(f"❌ Bulk upload error: {str(e)}")
        return jsonify({'error': f'Lỗi upload hàng loạt: {str(e)}'}), 500

@app.route('/api/upload-marketing-resource', methods=['POST'])
def upload_marketing_resource():
    """API upload ảnh tài nguyên marketing lên Cloudinary"""
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

            # Upload to Cloudinary with image optimization for marketing resources
            upload_result = cloudinary.uploader.upload(
                file,
                folder="marketing_resources",
                public_id=f"resource_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename.split('.')[0]}",
                resource_type="image",
                # Image optimization settings
                quality="auto:good",  # Chất lượng tốt cho marketing materials
                fetch_format="auto",  # Tự động chọn format tối ưu
                width=2000,  # Giới hạn chiều rộng tối đa cho marketing
                height=2000,  # Giới hạn chiều cao tối đa cho marketing
                crop="limit",  # Giữ nguyên tỷ lệ
                flags="progressive",  # Tạo ảnh progressive
                transformation=[
                    {"width": 2000, "height": 2000, "crop": "limit"},
                    {"quality": "auto:good"},
                    {"fetch_format": "auto"}
                ]
            )

            return jsonify({
                'success': True,
                'url': upload_result['secure_url'],
                'public_id': upload_result['public_id'],
                'file_size': file_size
            })
        else:
            return jsonify({'error': 'File không đúng định dạng. Chỉ chấp nhận: PNG, JPG, JPEG, GIF, WEBP'}), 400

    except Exception as e:
        print(f"❌ Error uploading marketing resource image: {e}")
        return jsonify({'error': f'Lỗi upload ảnh: {str(e)}'}), 500

@app.route('/api/product-stock/<int:product_id>')
def api_product_stock(product_id):
    """API lấy thông tin stock của sản phẩm"""
    import requests

    try:
        response = requests.get(f'{API_BASE_URL}/admin-products/{product_id}/', timeout=30)
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

@app.route('/backend/api/orders/<int:order_id>/confirm', methods=['POST'])
def api_confirm_order(order_id):
    """API xác nhận đơn hàng (không giảm tồn kho)"""
    import requests
    
    try:
        # Gọi API Django để xác nhận đơn hàng
        response = requests.post(f'{API_BASE_URL}/orders/{order_id}/confirm/', timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return jsonify(result)
        else:
            error_data = response.json() if response.content else {}
            return jsonify({'error': error_data.get('error', f'HTTP error! status: {response.status_code}')}), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

@app.route('/backend/api/orders/<int:order_id>/cancel', methods=['POST'])
def api_cancel_order(order_id):
    """API hủy đơn hàng và khôi phục tồn kho"""
    import requests
    
    try:
        # Gọi API Django để hủy đơn hàng
        response = requests.post(f'{API_BASE_URL}/orders/{order_id}/cancel/', timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return jsonify(result)
        else:
            error_data = response.json() if response.content else {}
            return jsonify({'error': error_data.get('error', f'HTTP error! status: {response.status_code}')}), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

@app.route('/backend/api/orders/<int:order_id>/update-items', methods=['POST'])
def api_update_order_items(order_id):
    """Proxy cập nhật danh sách sản phẩm trong đơn hàng"""
    import requests
    try:
        response = requests.post(f'{API_BASE_URL}/orders/{order_id}/update-items/', json=request.get_json(force=True), timeout=30)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            error_data = response.json() if response.content else {}
            return jsonify({'error': error_data.get('error', f'HTTP error! status: {response.status_code}')}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Lỗi kết nối: {str(e)}'}), 500

@app.route('/backend/api/orders/<int:order_id>/ship', methods=['POST'])
def api_ship_order(order_id):
    """API đánh dấu đơn hàng đã giao"""
    import requests
    
    try:
        # Gọi API Django để đánh dấu đơn hàng đã giao
        response = requests.post(f'{API_BASE_URL}/orders/{order_id}/ship/', timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return jsonify(result)
        else:
            error_data = response.json() if response.content else {}
            return jsonify({'error': error_data.get('error', f'HTTP error! status: {response.status_code}')}), response.status_code
            
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

        # Tạo URLs cho admin panel
        order_absolute_url = f'https://buddyskincare.vn/admin/orders/{order_id}/'
        all_orders_url = 'https://buddyskincare.vn/admin/orders'

        # Render email template
        html_content = render_template('emails/new_order_notification.html',
                                     order=order,
                                     pending_orders=pending_orders,
                                     order_absolute_url=order_absolute_url,
                                     all_orders_url=all_orders_url,
                                     current_time=datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

        # SMTP configuration
        smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_user = os.getenv('SMTP_USER')
        smtp_pass = os.getenv('SMTP_PASS')
        sender = os.getenv('SMTP_SENDER', smtp_user or 'no-reply@buddyskincare.vn')
        admin_email = os.getenv('ADMIN_EMAIL', 'buddyskincarevn@gmail.com')

        # Try Gmail API first, then SMTP, then fallback to file
        email_sent = False
        
        # Try Gmail API
        try:
            email_sent = send_email_via_gmail_api(
                to_email=admin_email,
                subject=f'🔔 Đơn hàng mới #{order_id} cần xác nhận - BuddySkincare',
                html_content=html_content,
                plain_text=f'Đơn hàng mới #{order_id} từ {order.get("customer_name", "Khách hàng")} cần xác nhận'
            )
        except Exception as e:
            print(f"❌ Gmail API failed: {e}")
        
        # If Gmail API failed, try SMTP
        if not email_sent and (smtp_user and smtp_pass):
            try:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = f'🔔 Đơn hàng mới #{order_id} cần xác nhận - BuddySkincare'
                msg['From'] = sender
                msg['To'] = admin_email
                
                # Add plain text version
                text_content = f'Đơn hàng mới #{order_id} từ {order.get("customer_name", "Khách hàng")} cần xác nhận'
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
                
                # Add HTML version
                html_part = MIMEText(html_content, 'html', 'utf-8')
                msg.attach(html_part)
                
                # Send email
                server = smtplib.SMTP(smtp_host, smtp_port)
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
                server.quit()
                
                email_sent = True
                print(f"✅ Email sent via SMTP to {admin_email}")
            except Exception as e:
                print(f"❌ SMTP failed: {e}")
        
        # If both failed, save to file
        if not email_sent:
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
                return jsonify({'success': False, 'message': f'Gửi email thất bại và lưu file thất bại: {str(e)}'}), 500

        # Return success if email was sent
        if email_sent:
            return jsonify({
                'success': True,
                'message': f'Đã gửi thông báo đơn hàng mới đến {admin_email}'
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Không thể gửi email'}), 500

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


@app.route('/admin/messages')
def admin_messages():
    """Admin page for managing customer messages."""
    return render_template('admin_messages.html')

@app.route('/admin/ctv')
def admin_ctv():
    """Admin page for managing CTVs."""
    return render_template('admin_ctv.html')

@app.route('/admin/resources')
def admin_resources():
    """Admin page for managing marketing resources."""
    return render_template('admin_resources.html')

@app.route('/admin/api/ctvs/<int:ctv_id>/send-welcome-email', methods=['POST'])
def send_ctv_welcome_email(ctv_id):
    """Send welcome email to CTV with login credentials."""
    try:
        # Get CTV data from API
        resp = requests.get(f'{API_BASE_URL}/ctvs/{ctv_id}/', timeout=30)
        if resp.status_code != 200:
            return jsonify({'success': False, 'message': 'Không tìm thấy CTV'}), 404

        ctv_data = resp.json()

        # Get data from request
        data = request.get_json(silent=True) or {}
        ctv_name = data.get('ctv_name') or ctv_data.get('full_name', '')
        ctv_email = data.get('ctv_email') or ctv_data.get('email', '')
        ctv_phone = ctv_data.get('phone', '')
        ctv_password = ctv_data.get('password_text', '')

        if not ctv_email or '@' not in ctv_email:
            return jsonify({'success': False, 'message': 'Email CTV không hợp lệ'}), 400

        if not ctv_password:
            return jsonify({'success': False, 'message': 'CTV chưa có mật khẩu. Vui lòng cập nhật mật khẩu trước khi gửi email.'}), 400

        # Create login URL
        login_url = f"{request.url_root}ctv/login"

        # Render email template
        html_content = render_template('emails/ctv_welcome_email.html',
                                     ctv_name=ctv_name,
                                     ctv_phone=ctv_phone,
                                     ctv_password=ctv_password,
                                     login_url=login_url)

        # SMTP configuration
        smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_user = os.getenv('SMTP_USER', 'buddyskincarevn@gmail.com')
        smtp_pass = os.getenv('SMTP_PASS', 'pyvd idcm rsrf apjn')
        sender = os.getenv('SMTP_SENDER', smtp_user)

        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'🎉 Chào mừng đến với BuddySkincare - Thông tin tài khoản CTV'
        msg['From'] = sender
        msg['To'] = ctv_email

        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        # Send email
        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(sender, [ctv_email], msg.as_string())

        return jsonify({
            'success': True,
            'message': f'Đã gửi email chào mừng đến {ctv_email}',
            'email_sent': True
        }), 200

    except smtplib.SMTPAuthenticationError:
        return jsonify({
            'success': False,
            'message': 'Lỗi xác thực email. Vui lòng kiểm tra cấu hình SMTP.',
            'email_sent': False
        }), 500
    except smtplib.SMTPException as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi khi gửi email: {str(e)}',
            'email_sent': False
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi hệ thống: {str(e)}',
            'email_sent': False
        }), 500

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


# Sitemap routes
@app.route('/sitemap_index.xml')
def sitemap_index():
    """Sitemap index file"""
    from flask import make_response
    response = make_response(render_template('sitemap_index.html', current_date=datetime.now().strftime('%Y-%m-%d')))
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/sitemap_pages.xml')
def sitemap_pages():
    """Main pages sitemap"""
    from flask import make_response
    response = make_response(render_template('sitemap_pages.xml', current_date=datetime.now().strftime('%Y-%m-%d')))
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/sitemap_products.xml')
def sitemap_products():
    """Products sitemap"""
    from flask import make_response
    response = make_response(render_template('sitemap_products.xml', current_date=datetime.now().strftime('%Y-%m-%d')))
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/sitemap_blog.xml')
def sitemap_blog():
    """Blog sitemap"""
    from flask import make_response
    response = make_response(render_template('sitemap_blog.xml', current_date=datetime.now().strftime('%Y-%m-%d')))
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/sitemap_categories.xml')
def sitemap_categories():
    """Categories sitemap"""
    from flask import make_response
    response = make_response(render_template('sitemap_categories.xml', current_date=datetime.now().strftime('%Y-%m-%d')))
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/sitemap_static.xml')
def sitemap_static():
    """Static pages sitemap"""
    from flask import make_response
    response = make_response(render_template('sitemap_static.xml', current_date=datetime.now().strftime('%Y-%m-%d')))
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/sitemap_simple.xml')
def sitemap_simple():
    """Simple sitemap for testing"""
    from flask import make_response
    response = make_response(render_template('sitemap_simple.xml', current_date=datetime.now().strftime('%Y-%m-%d')))
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/robots.txt')
def robots_txt():
    """Robots.txt file"""
    from flask import make_response
    response = make_response(render_template('robots.txt'))
    response.headers['Content-Type'] = 'text/plain'
    return response



@app.route('/api/upload-cccd', methods=['POST'])
def upload_cccd_image():
    """Upload ảnh CCCD lên Cloudinary - đơn giản"""
    try:
        print(f"🔍 CCCD Upload request received")
        
        if 'file' not in request.files:
            return jsonify({'error': 'Không có file được chọn'}), 400

        file = request.files['file']
        print(f"📁 File: {file.filename}")
        
        # Upload trực tiếp lên Cloudinary
        from datetime import datetime
        
        # Reset file pointer
        file.seek(0)
        
        print(f"🚀 Uploading to Cloudinary...")
        print(f"📁 File size: {file.content_length} bytes")
        print(f"📁 File type: {file.content_type}")
        
        upload_result = cloudinary.uploader.upload(
            file,
            folder="ctv_cccd",
            public_id=f"cccd_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            resource_type="image",
            # Thêm các tham số để đảm bảo upload thành công
            use_filename=True,
            unique_filename=True,
            overwrite=False
        )

        print(f"✅ Upload successful!")
        print(f"🔗 URL: {upload_result['secure_url']}")
        print(f"🆔 Public ID: {upload_result['public_id']}")
        print(f"📏 Size: {upload_result.get('bytes', 'Unknown')} bytes")
        
        return jsonify({
            'success': True,
            'url': upload_result['secure_url'],
            'public_id': upload_result['public_id'],
            'size': upload_result.get('bytes', 0)
        })

    except Exception as e:
        print(f"❌ Upload error: {e}")
        return jsonify({'error': f'Lỗi upload: {str(e)}'}), 500

# Backlink Content Routes
@app.route('/beauty-ingredient-dictionary')
def beauty_ingredient_dictionary():
    """Từ điển thành phần mỹ phẩm - Linkable asset cho backlinks"""
    return render_template('beauty_ingredient_dictionary.html')

@app.route('/skin-type-quiz')
def skin_type_quiz():
    """Quiz kiểm tra loại da - Interactive tool cho backlinks"""
    return render_template('skin_type_quiz.html')

@app.route('/skincare-step')
def skincare_step():
    """Quy trình skincare - Hướng dẫn chăm sóc da"""
    return render_template('skincare-step.html')

@app.route('/skincare-guide-2024')
def skincare_guide_2024():
    """Hướng dẫn skincare toàn diện 2024 - Ultimate guide cho backlinks"""
    return render_template('skincare_guide_2024.html')

@app.route('/beauty-trends-vietnam')
def beauty_trends_vietnam():
    """Xu hướng làm đẹp Việt Nam 2024 - Data-driven content cho backlinks"""
    return render_template('beauty_trends_vietnam.html')

@app.route('/expert-beauty-advice')
def expert_beauty_advice():
    """Tư vấn làm đẹp từ chuyên gia - Expert roundup cho backlinks"""
    return render_template('expert_beauty_advice.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
