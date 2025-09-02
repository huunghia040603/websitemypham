from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'buddyskincare_secret_key_2024'

# Dữ liệu demo cho sản phẩm
products_data = [
    {
        'id': 1,
        'name': 'Combo Nước Cân Bằng Sen Hậu Giang',
        'brand': 'TheFaceShop',
        'category': 'Chăm Sóc Da',
        'original_price': 450000,
        'sale_price': 315000,
        'discount': 30,
        'stock': 8,
        'rating': 5.0,
        'reviews': 156,
        'image': 'static/image/demo/facebook-dynamic-combo-cocoon-nuoc-can-bang-sen-hau-giang-310ml-nuoc-tay-trang-bi-dao-500ml-1741320900_img_300x300_b798dd_fit_center.jpg',
        'description': 'Combo nước cân bằng sen hậu giang và nước tẩy trang bi đào, giúp làm sạch và cân bằng da hiệu quả.',
        'features': [
            'Làm sạch sâu',
            'Cân bằng pH',
            'Dưỡng ẩm',
            'Dịu nhẹ cho da'
        ],
        'specifications': {
            'brand': 'TheFaceShop',
            'origin': 'Hàn Quốc',
            'volume': '310ml + 500ml',
            'expiry': '36 tháng',
            'ingredients': 'Sen hậu giang, Bi đào',
            'skin_type': 'Mọi loại da',
            'condition': 'Mới 100%'
        }
    },
    {
        'id': 2,
        'name': 'Sữa Rửa Mặt Cetaphil Dịu Nhẹ',
        'brand': 'Cetaphil',
        'category': 'Chăm Sóc Da',
        'original_price': 320000,
        'sale_price': 240000,
        'discount': 25,
        'stock': 12,
        'rating': 5.0,
        'reviews': 203,
        'image': 'static/image/demo/facebook-dynamic-sua-rua-mat-cetaphil-diu-nhe-khong-xa-phong-500ml-moi-1741235596_img_300x300_b798dd_fit_center.jpg',
        'description': 'Sữa rửa mặt dịu nhẹ không xà phòng, phù hợp cho mọi loại da, đặc biệt là da nhạy cảm.',
        'features': [
            'Không xà phòng',
            'Dịu nhẹ cho da',
            'Làm sạch hiệu quả',
            'Không gây kích ứng'
        ],
        'specifications': {
            'brand': 'Cetaphil',
            'origin': 'Mỹ',
            'volume': '500ml',
            'expiry': '36 tháng',
            'skin_type': 'Mọi loại da',
            'condition': 'Mới 100%'
        }
    },
    {
        'id': 3,
        'name': 'Nước Tẩy Trang Bioderma',
        'brand': 'Bioderma',
        'category': 'Chăm Sóc Da',
        'original_price': 280000,
        'sale_price': 224000,
        'discount': 20,
        'stock': 15,
        'rating': 5.0,
        'reviews': 178,
        'image': 'static/image/demo/facebook-dynamic-nuoc-tay-trang-bioderma-danh-cho-da-dau-hon-hop-500ml-1745303871_img_300x300_b798dd_fit_center.jpg',
        'description': 'Nước tẩy trang chuyên biệt cho da dầu hỗn hợp, giúp làm sạch sâu và cân bằng da.',
        'features': [
            'Tẩy trang hiệu quả',
            'Cân bằng da dầu',
            'Không gây mụn',
            'Dịu nhẹ cho da'
        ],
        'specifications': {
            'brand': 'Bioderma',
            'origin': 'Pháp',
            'volume': '500ml',
            'expiry': '36 tháng',
            'skin_type': 'Da dầu hỗn hợp',
            'condition': 'Mới 100%'
        }
    },
    {
        'id': 4,
        'name': 'Kem Chống Nắng L\'Oreal Paris',
        'brand': 'L\'Oreal Paris',
        'category': 'Chăm Sóc Da',
        'original_price': 350000,
        'sale_price': 245000,
        'discount': 30,
        'stock': 6,
        'rating': 5.0,
        'reviews': 134,
        'image': 'static/image/demo/facebook-dynamic-kem-chong-nang-l-oreal-paris-x20-thoang-da-mong-nhe-50ml-1738898716_img_300x300_b798dd_fit_center.jpg',
        'description': 'Kem chống nắng x20 thoáng da mỏng nhẹ, bảo vệ da khỏi tác hại của tia UV.',
        'features': [
            'Chống nắng SPF 50+',
            'Thoáng da mỏng nhẹ',
            'Không gây nhờn rít',
            'Bảo vệ toàn diện'
        ],
        'specifications': {
            'brand': 'L\'Oreal Paris',
            'origin': 'Pháp',
            'volume': '50ml',
            'expiry': '36 tháng',
            'spf': 'SPF 50+',
            'condition': 'Mới 100%'
        }
    },
    {
        'id': 5,
        'name': 'Son Lì New Bold TheFaceShop',
        'brand': 'TheFaceShop',
        'category': 'Son Môi',
        'original_price': 280000,
        'sale_price': 196000,
        'discount': 30,
        'stock': 10,
        'rating': 4.8,
        'reviews': 98,
        'image': 'static/image/demo/facebook-dynamic-422211183-1696227431_img_300x300_b798dd_fit_center.png',
        'description': 'Son lì New Bold với màu sắc nổi bật và độ bền màu lâu, phù hợp cho mọi dịp.',
        'features': [
            'Màu sắc nổi bật',
            'Độ bền màu lâu',
            'Không khô môi',
            'Dễ thoa đều'
        ],
        'specifications': {
            'brand': 'TheFaceShop',
            'origin': 'Hàn Quốc',
            'volume': '3.5g',
            'expiry': '36 tháng',
            'texture': 'Matte',
            'condition': 'Mới 100%'
        }
    },
    {
        'id': 6,
        'name': 'Mặt Nạ Real Nature',
        'brand': 'TheFaceShop',
        'category': 'Chăm Sóc Da',
        'original_price': 150000,
        'sale_price': 105000,
        'discount': 30,
        'stock': 25,
        'rating': 4.7,
        'reviews': 145,
        'image': 'static/image/demo/facebook-dynamic-206400019-1696052291_img_300x300_b798dd_fit_center.png',
        'description': 'Mặt nạ Real Nature với thành phần tự nhiên, giúp dưỡng ẩm và làm sáng da hiệu quả.',
        'features': [
            'Thành phần tự nhiên',
            'Dưỡng ẩm sâu',
            'Làm sáng da',
            'Dịu nhẹ cho da'
        ],
        'specifications': {
            'brand': 'TheFaceShop',
            'origin': 'Hàn Quốc',
            'volume': '1 miếng',
            'expiry': '36 tháng',
            'skin_type': 'Mọi loại da',
            'condition': 'Mới 100%'
        }
    },
    {
        'id': 7,
        'name': 'Son Mac Ruby Woo (Đã sử dụng)',
        'brand': 'Mac Cosmetics',
        'category': 'Son Môi',
        'original_price': 850000,
        'sale_price': 255000,
        'discount': 70,
        'stock': 3,
        'rating': 4.9,
        'reviews': 67,
        'image': 'static/image/demo/facebook-dynamic-combo-cocoon-nuoc-can-bang-sen-hau-giang-310ml-nuoc-tay-trang-bi-dao-500ml-1741320900_img_300x300_b798dd_fit_center.jpg',
        'description': 'Son Mac Ruby Woo đã sử dụng 1-2 lần, màu đỏ nổi bật, độ bền màu tuyệt vời.',
        'features': [
            'Màu đỏ nổi bật',
            'Độ bền màu cao',
            'Kết cấu mượt mà',
            'Phù hợp mọi tông da'
        ],
        'specifications': {
            'brand': 'Mac Cosmetics',
            'origin': 'Canada',
            'volume': '3g',
            'expiry': '24 tháng',
            'texture': 'Matte',
            'condition': 'Đã sử dụng 1-2 lần',
            'usage_note': 'Còn 95% sản phẩm'
        }
    },
    {
        'id': 8,
        'name': 'Kem Dưỡng Ẩm Cetaphil (Đã mở)',
        'brand': 'Cetaphil',
        'category': 'Chăm Sóc Da',
        'original_price': 450000,
        'sale_price': 180000,
        'discount': 60,
        'stock': 5,
        'rating': 4.6,
        'reviews': 89,
        'image': 'static/image/demo/facebook-dynamic-sua-rua-mat-cetaphil-diu-nhe-khong-xa-phong-500ml-moi-1741235596_img_300x300_b798dd_fit_center.jpg',
        'description': 'Kem dưỡng ẩm Cetaphil đã mở nhưng chưa sử dụng, phù hợp cho da khô và nhạy cảm.',
        'features': [
            'Dưỡng ẩm sâu',
            'Dịu nhẹ cho da',
            'Không gây mụn',
            'Phù hợp da nhạy cảm'
        ],
        'specifications': {
            'brand': 'Cetaphil',
            'origin': 'Mỹ',
            'volume': '100ml',
            'expiry': '18 tháng',
            'skin_type': 'Da khô, nhạy cảm',
            'condition': 'Đã mở, chưa sử dụng',
            'usage_note': 'Còn 100% sản phẩm'
        }
    },
    {
        'id': 9,
        'name': 'Nước Hoa Chanel N°5 (Test)',
        'brand': 'Chanel',
        'category': 'Nước Hoa',
        'original_price': 3500000,
        'sale_price': 1050000,
        'discount': 70,
        'stock': 2,
        'rating': 5.0,
        'reviews': 23,
        'image': 'static/image/demo/facebook-dynamic-nuoc-tay-trang-bioderma-danh-cho-da-dau-hon-hop-500ml-1745303871_img_300x300_b798dd_fit_center.jpg',
        'description': 'Nước hoa Chanel N°5 tester, hương thơm sang trọng và quyến rũ.',
        'features': [
            'Hương thơm sang trọng',
            'Độ bền hương lâu',
            'Thiết kế tinh tế',
            'Phù hợp mọi lứa tuổi'
        ],
        'specifications': {
            'brand': 'Chanel',
            'origin': 'Pháp',
            'volume': '50ml',
            'expiry': '60 tháng',
            'fragrance_type': 'Floral',
            'condition': 'Tester - Đã test',
            'usage_note': 'Còn 90% sản phẩm'
        }
    },
    {
        'id': 10,
        'name': 'Kem Nền Mac Studio Fix (Đã sử dụng)',
        'brand': 'Mac Cosmetics',
        'category': 'Trang Điểm',
        'original_price': 1200000,
        'sale_price': 360000,
        'discount': 70,
        'stock': 4,
        'rating': 4.8,
        'reviews': 45,
        'image': 'static/image/demo/facebook-dynamic-kem-chong-nang-l-oreal-paris-x20-thoang-da-mong-nhe-50ml-1738898716_img_300x300_b798dd_fit_center.jpg',
        'description': 'Kem nền Mac Studio Fix đã sử dụng vài lần, độ che phủ cao và bền màu.',
        'features': [
            'Độ che phủ cao',
            'Bền màu lâu',
            'Kiểm soát dầu tốt',
            'Phù hợp nhiều tông da'
        ],
        'specifications': {
            'brand': 'Mac Cosmetics',
            'origin': 'Canada',
            'volume': '30ml',
            'expiry': '24 tháng',
            'coverage': 'Full Coverage',
            'condition': 'Đã sử dụng vài lần',
            'usage_note': 'Còn 85% sản phẩm'
        }
    }
]

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
    flash_sale_products = [p for p in products_data if p['discount'] > 0][:4]
    featured_products = [p for p in products_data if p['discount'] == 0][:4]
    
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
    # Lấy tham số filter
    category = request.args.get('category')
    brand = request.args.get('brand')
    price_range = request.args.get('price')
    discount = request.args.get('discount')
    sort_by = request.args.get('sort', 'newest')
    condition = request.args.get('condition', 'all')  # Thêm filter theo tình trạng
    
    # Filter sản phẩm
    filtered_products = products_data.copy()
    
    if category:
        filtered_products = [p for p in filtered_products if p['category'] == category]
    
    if brand:
        filtered_products = [p for p in filtered_products if p['brand'] == brand]
    
    if condition != 'all':
        filtered_products = [p for p in filtered_products if p['specifications']['condition'] == condition]
    
    if price_range:
        if price_range == 'under_500k':
            filtered_products = [p for p in filtered_products if p['sale_price'] < 500000]
        elif price_range == '500k_1m':
            filtered_products = [p for p in filtered_products if 500000 <= p['sale_price'] < 1000000]
        elif price_range == '1m_2m':
            filtered_products = [p for p in filtered_products if 1000000 <= p['sale_price'] < 2000000]
        elif price_range == 'over_2m':
            filtered_products = [p for p in filtered_products if p['sale_price'] >= 2000000]
    
    if discount:
        if discount == 'over_50':
            filtered_products = [p for p in filtered_products if p['discount'] >= 50]
        elif discount == '30_50':
            filtered_products = [p for p in filtered_products if 30 <= p['discount'] < 50]
        elif discount == 'under_30':
            filtered_products = [p for p in filtered_products if p['discount'] < 30]
    
    # Sort sản phẩm
    if sort_by == 'price_low':
        filtered_products.sort(key=lambda x: x['sale_price'])
    elif sort_by == 'price_high':
        filtered_products.sort(key=lambda x: x['sale_price'], reverse=True)
    elif sort_by == 'popular':
        filtered_products.sort(key=lambda x: x['reviews'], reverse=True)
    elif sort_by == 'discount':
        filtered_products.sort(key=lambda x: x['discount'], reverse=True)
    else:  # newest
        filtered_products.sort(key=lambda x: x['id'], reverse=True)
    
    return render_template('products.html',
                         products=filtered_products,
                         categories=categories_data,
                         brands=brands_data,
                         current_condition=condition)

@app.route('/products/new')
def products_new():
    """Trang sản phẩm mới 100%"""
    filtered_products = [p for p in products_data if p['specifications']['condition'] == 'Mới 100%']
    
    return render_template('products.html',
                         products=filtered_products,
                         categories=categories_data,
                         brands=brands_data,
                         current_condition='Mới 100%',
                         page_title='Sản Phẩm Mới 100%')

@app.route('/products/used')
def products_used():
    """Trang sản phẩm đã sử dụng"""
    filtered_products = [p for p in products_data if p['specifications']['condition'] != 'Mới 100%']
    
    return render_template('products.html',
                         products=filtered_products,
                         categories=categories_data,
                         brands=brands_data,
                         current_condition='Đã sử dụng',
                         page_title='Sản Phẩm Đã Sử Dụng')

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Trang chi tiết sản phẩm"""
    product = next((p for p in products_data if p['id'] == product_id), None)
    
    if not product:
        return redirect(url_for('products'))
    
    # Lấy đánh giá của sản phẩm
    product_reviews = [r for r in reviews_data if r['product_id'] == product_id]
    
    # Tính rating trung bình
    if product_reviews:
        avg_rating = sum(r['rating'] for r in product_reviews) / len(product_reviews)
    else:
        avg_rating = 0
    
    # Sản phẩm liên quan (cùng danh mục)
    related_products = [p for p in products_data if p['category'] == product['category'] and p['id'] != product_id][:4]
    
    return render_template('product-detail.html',
                         product=product,
                         reviews=product_reviews,
                         avg_rating=avg_rating,
                         related_products=related_products)

@app.route('/api/add-to-cart', methods=['POST'])
def add_to_cart():
    """API thêm vào giỏ hàng"""
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    # Tìm sản phẩm
    product = next((p for p in products_data if p['id'] == product_id), None)
    
    if not product:
        return jsonify({'success': False, 'message': 'Sản phẩm không tồn tại'})
    
    if product['stock'] < quantity:
        return jsonify({'success': False, 'message': 'Số lượng không đủ'})
    
    # Ở đây sẽ lưu vào session hoặc database
    # Hiện tại chỉ trả về thành công
    return jsonify({
        'success': True, 
        'message': f'Đã thêm {quantity} {product["name"]} vào giỏ hàng',
        'cart_count': 3  # Demo
    })

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
    query = request.args.get('q', '').lower()
    
    if len(query) < 2:
        return jsonify([])
    
    # Tìm kiếm theo tên sản phẩm hoặc thương hiệu
    results = []
    for product in products_data:
        if (query in product['name'].lower() or 
            query in product['brand'].lower() or
            query in product['category'].lower()):
            results.append({
                'id': product['id'],
                'name': product['name'],
                'brand': product['brand'],
                'price': product['sale_price'],
                'image': product['image']
            })
    
    return jsonify(results[:5])  # Giới hạn 5 kết quả

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

@app.route('/live-chat')
def live_chat():
    return render_template('live-chat.html')

@app.route('/skincare')
def skincare():
    return render_template('skincare.html')

# Demo metadata for skincare steps (frontend content demo)
SKINCARE_STEPS = {
    "1": {
        "title": "Bước 1: Làm sạch",
        "desc": "Loại bỏ bụi bẩn, dầu thừa và lớp trang điểm để da thông thoáng.",
        "how": [
            "Làm ướt mặt với nước ấm",
            "Lấy lượng sữa rửa mặt vừa đủ, tạo bọt và massage 30–60 giây",
            "Rửa sạch, lau khô bằng khăn mềm"
        ],
        "tips": [
            "Buổi tối nên tẩy trang trước khi rửa mặt",
            "Chọn pH dịu nhẹ ~5.5 cho mọi loại da"
        ],
        "products": [
            {"name": "Sữa rửa mặt dịu nhẹ", "price": "128.000₫", "old": "320.000₫", "img": "image/demo/facebook-dynamic-sua-rua-mat-cetaphil-diu-nhe-khong-xa-phong-500ml-moi-1741235596_img_300x300_b798dd_fit_center.jpg"}
        ]
    },
    "2": {
        "title": "Bước 2: Cân bằng",
        "desc": "Phục hồi pH và cấp ẩm nhẹ, chuẩn bị cho serum.",
        "how": ["Thấm toner ra bông, lau nhẹ nhàng hoặc vỗ trực tiếp"],
        "tips": ["Tránh cồn khô nếu da nhạy cảm"],
        "products": []
    },
    "3": {
        "title": "Bước 3: Serum điều trị",
        "desc": "Tập trung giải quyết vấn đề da: ẩm, dầu, nám, mụn...",
        "how": ["Dùng 2–3 giọt, vỗ nhẹ đến khi thấm"],
        "tips": ["Không trộn quá nhiều hoạt chất mạnh cùng lúc"],
        "products": []
    },
    "4": {"title": "Bước 4: Khóa ẩm", "desc": "Giữ ẩm cho da suốt nhiều giờ.", "how": ["Thoa kem dưỡng vừa đủ"], "tips": [], "products": []},
    "5": {"title": "Bước 5: Chống nắng", "desc": "Bảo vệ da ban ngày.", "how": ["SPF 30+ phổ rộng, đủ 2 ngón tay"], "tips": ["Thoa lại sau 2–3 giờ"], "products": []},
    "6": {"title": "Bước 6: Mask/Peel", "desc": "Bổ sung theo tuần.", "how": ["1–2 lần/tuần tùy da"], "tips": [], "products": []}
}

@app.route('/skincare/step/<step_id>')
def skincare_step(step_id):
    data = SKINCARE_STEPS.get(step_id)
    if not data:
        return render_template('skincare-step.html', not_found=True, step_id=step_id)
    return render_template('skincare-step.html', data=data, step_id=step_id)

@app.route('/consign')
def consign():
    return render_template('consign.html')

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
