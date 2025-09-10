from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from .google_social_auth import Google
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import F
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum


# --- User Serializers ---

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer to display and update user profile information.
    """
    points = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'phone_number', 'address', 'dob', 'avatar', 'points', 'level')

    def get_points(self, obj):
        try:
            return obj.customer.points if hasattr(obj, 'customer') else (obj.collaborator.points if hasattr(obj, 'collaborator') else 0)
        except (Customer.DoesNotExist, Collaborator.DoesNotExist):
            return 0

    def get_level(self, obj):
        try:
            return obj.customer.level if hasattr(obj, 'customer') else (obj.collaborator.level if hasattr(obj, 'collaborator') else 1)
        except (Customer.DoesNotExist, Collaborator.DoesNotExist):
            return 1


class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer to display customer information.
    """
    class Meta:
        model = Customer
        fields = ('id', 'name', 'email', 'phone_number', 'address', 'dob', 'avatar', 'points', 'level')


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer to display and edit user profile information.
    """
    points = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'phone_number',
            'email',
            'name',
            'address',
            'dob',
            'avatar',
            'points',
            'level'
        ]
        read_only_fields = ['id']

    def validate_email(self, value):
        if value and self.instance and User.objects.exclude(id=self.instance.id).filter(email=value).exists():
            raise serializers.ValidationError("Email này đã được sử dụng. Vui lòng chọn một email khác.")
        return value

    def get_points(self, obj):
        try:
            return obj.customer.points if hasattr(obj, 'customer') else (obj.collaborator.points if hasattr(obj, 'collaborator') else 0)
        except (Customer.DoesNotExist, Collaborator.DoesNotExist):
            return 0

    def get_level(self, obj):
        try:
            return obj.customer.level if hasattr(obj, 'customer') else (obj.collaborator.level if hasattr(obj, 'collaborator') else 1)
        except (Customer.DoesNotExist, Collaborator.DoesNotExist):
            return 1


class CollaboratorSerializer(serializers.ModelSerializer):
    """
    Serializer to display collaborator information.
    """
    class Meta:
        model = Collaborator
        fields = ('id', 'name', 'email', 'phone_number', 'sales_code', 'points', 'level')

class PhoneNumberLoginSerializer(serializers.Serializer):
    """
    Serializer to handle login with phone number and password,
    and return user info and JWT tokens.
    """
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)
    user_info = serializers.SerializerMethodField()

    def validate(self, data):
        phone_number = data.get('phone_number')
        password = data.get('password')

        if not phone_number or not password:
            raise serializers.ValidationError('Vui lòng cung cấp cả số điện thoại và mật khẩu.')

        user = authenticate(request=self.context.get('request'),
                            phone_number=phone_number, password=password)

        if not user:
            raise serializers.ValidationError('Số điện thoại hoặc mật khẩu không đúng.')

        if not user.is_active:
            raise serializers.ValidationError('Tài khoản đã bị vô hiệu hóa.')

        self.user = user  # Lưu người dùng vào self để sử dụng trong get_user_info
        return data

    def get_user_info(self, data):
        if self.user:
            return UserSerializer(self.user).data
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Lấy người dùng từ validated data
        user = self.user

        # Lấy JWT tokens
        refresh = RefreshToken.for_user(user)
        representation['access_token'] = str(refresh.access_token)
        representation['refresh_token'] = str(refresh)

        # Trả về thông tin người dùng chi tiết
        representation['user'] = UserSerializer(user).data

        return representation


class GoogleSocialAuthSerializer(serializers.Serializer):
    """
    Serializer to handle Google social authentication.
    """
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        try:
            user_data = Google.validate(auth_token)
        except ValueError as e:
            raise serializers.ValidationError(str(e))
        except Exception as e:
            raise serializers.ValidationError(f"Google token validation failed: {str(e)}")

        email = user_data.get('email', '')
        name = user_data.get('name', '')
        avatar = user_data.get('picture', None)

        if not email:
            raise serializers.ValidationError("Email is not provided in Google token.")

        try:
            with transaction.atomic():
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'name': name,
                        'avatar': avatar,
                        'is_google_user': True,
                        'is_active': True,
                    }
                )
                if created:
                    # Gán user_type='customer' và tạo Customer object liên quan
                    Customer.objects.create(
                        user_ptr=user,
                        name=name,
                        email=email,
                        avatar=avatar,
                        is_google_user=True,
                    )
                else:
                    # Nếu người dùng đã tồn tại, cập nhật thông tin nếu cần
                    if not user.name:
                        user.name = name
                    if not user.avatar:
                        user.avatar = avatar
                    user.is_google_user = True
                    user.save()
        except Exception as e:
            print(f"Lỗi khi xử lý người dùng Google: {e}")
            raise serializers.ValidationError(f"Lỗi khi xử lý dữ liệu người dùng: {str(e)}")

        return user


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=3
    )
    user_type = serializers.CharField(write_only=True, required=False, default='customer')


    class Meta:
        model = User
        fields = ('name', 'phone_number', 'password', 'email', 'avatar', 'user_type')
        extra_kwargs = {
            'phone_number': {'required': False},
            'email': {'required': False},
            'name': {'required': False},
            'avatar': {'required': False},
        }

    def validate(self, data):
        phone_number = data.get('phone_number')
        email = data.get('email')

        if not phone_number and not email:
            raise serializers.ValidationError("Phải cung cấp số điện thoại hoặc email.")

        if phone_number and User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError("Số điện thoại này đã được đăng ký.")

        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email này đã được đăng ký.")

        return data

    def create(self, validated_data):
        user_type = validated_data.pop('user_type', 'customer')
        password = validated_data.pop('password')

        with transaction.atomic():
            user = User.objects.create_user(
                password=password,
                **validated_data
            )

            # Sau khi user được tạo, tạo đối tượng con tương ứng
            if user_type == 'customer':
                Customer.objects.create(user_ptr=user, **validated_data)
            elif user_type == 'collaborator':
                Collaborator.objects.create(user_ptr=user, **validated_data)
            elif user_type == 'staff':
                Staff.objects.create(user_ptr=user, **validated_data)

            return user


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer to handle forgot password requests.
    """
    email = serializers.EmailField(required=True)


# --- Product-related Serializers ---

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name', 'country', 'introduction')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'code', 'name', 'description', 'start_date', 'end_date', 'status', 'discounted_price_reduction']


class GiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gift
        fields = ('id', 'name', 'description', 'image')



class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer cho Product, hiển thị tên hãng, danh mục và tags.
    Cho phép thêm/sửa sản phẩm bằng cách chọn các đối tượng liên quan qua tên.
    """
    # Hiển thị tên hãng (brand) khi GET
    brand_name = serializers.CharField(source='brand.name', read_only=True)

    # Cho phép người dùng chọn brand bằng tên khi POST/PUT
    brand = serializers.SlugRelatedField(
        queryset=Brand.objects.all(),
        slug_field='name',
        write_only=True
    )

    # Hiển thị tên danh mục (category) khi GET
    category_name = serializers.CharField(source='category.name', read_only=True)

    # Cho phép người dùng chọn category bằng tên khi POST/PUT
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='name',
        write_only=True
    )

    # Hiển thị tên các tags khi GET
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    # Cho phép người dùng thêm/sửa tags bằng tên khi POST/PUT
    tags_write = serializers.SlugRelatedField(
        queryset=Tag.objects.all(),
        slug_field='name',
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'description', 'image', 'brand', 'brand_name',
            'category', 'category_name', 'tags', 'tags_write', 'gifts',
            'stock_quantity', 'sold_quantity', 'rating', 'savings_price',
            'import_price', 'original_price', 'discount_rate',
            'discounted_price', 'status'
        )
        read_only_fields = ('savings_price', 'discount_rate')

    def create(self, validated_data):
        tags_data = validated_data.pop('tags_write', [])
        product = Product.objects.create(**validated_data)
        product.tags.set(tags_data)
        return product

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags_write', None)

        # Cập nhật các trường thông thường
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Cập nhật tags nếu có dữ liệu mới
        if tags_data is not None:
            instance.tags.set(tags_data)

        return instance


# --- Analytics ---
class AnalyticsSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsSnapshot
        fields = ['id', 'period', 'period_key', 'total_revenue', 'total_profit', 'data', 'created_at']


class ComputeAnalyticsSerializer(serializers.Serializer):
    period = serializers.ChoiceField(choices=['day','week','month','year'])
    start = serializers.DateField(required=False)
    end = serializers.DateField(required=False)

    def create(self, validated_data):
        from .models import Order
        from datetime import date, timedelta
        period = validated_data.get('period')
        start = validated_data.get('start')
        end = validated_data.get('end')

        # Only count orders that are confirmed and not cancelled
        orders = Order.objects.filter(is_confirmed=True).exclude(status='cancelled')

        # Set proper date range based on period
        today = date.today()
        if not start and not end:
            if period == 'day':
                start = today
                end = today
            elif period == 'week':
                # Get start of current week (Monday)
                start = today - timedelta(days=today.weekday())
                end = start + timedelta(days=6)
            elif period == 'month':
                # Get start and end of current month
                start = today.replace(day=1)
                if today.month == 12:
                    end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            elif period == 'year':
                # Get start and end of current year
                start = today.replace(month=1, day=1)
                end = today.replace(month=12, day=31)

        if start: orders = orders.filter(order_date__date__gte=start)
        if end: orders = orders.filter(order_date__date__lte=end)

        # For single period, just calculate total for that period
        total_revenue = Decimal('0.00')
        top_selling = {}
        top_revenue = {}

        # Create period key based on the date range
        if period == 'day':
            period_key = start.strftime('%Y-%m-%d')
        elif period == 'week':
            period_key = f"{start.year}-W{start.strftime('%W')}"
        elif period == 'month':
            period_key = start.strftime('%Y-%m')
        else:  # year
            period_key = str(start.year)

        # Calculate total revenue for this specific period
        for o in orders:
            total_revenue += (o.total_amount or Decimal('0.00'))

            # items for top lists
            for item in getattr(o, 'items').all():
                name = getattr(item.product, 'name', f"#{item.product_id}")
                qty = Decimal(item.quantity or 0)
                price = item.price_at_purchase or getattr(item.product, 'discounted_price', Decimal('0.00'))
                revenue = (price or Decimal('0.00')) * qty
                top_selling[name] = (top_selling.get(name, Decimal('0')) + qty)
                top_revenue[name] = (top_revenue.get(name, Decimal('0.00')) + revenue)

        # For single period, create simple chart data
        labels = [period_key]
        series = [float(total_revenue)]

        # Debug: Check if revenue needs scaling
        debug_revenue = []
        for o in orders:
            debug_revenue.append({
                'order_id': o.id,
                'total_amount': float(o.total_amount or 0),
                'shipping_fee': float(o.shipping_fee or 0),
                'order_date': str(o.order_date.date())
            })

        # Check if revenue values seem too small (likely in thousands instead of VND)
        # If average revenue per order is less than 1000, assume it's in thousands
        needs_scaling = False
        if orders.exists():
            avg_revenue = total_revenue / orders.count()
            if avg_revenue < 1000:
                needs_scaling = True
                # Scale up revenue and series by 1000
                total_revenue = total_revenue * 1000
                series = [s * 1000 for s in series]

        # Scale up top_revenue if needed
        if needs_scaling:
            for name in top_revenue:
                top_revenue[name] = top_revenue[name] * 1000

        # Compute import cost and shipping fee totals
        import_total = Decimal('0.00')
        shipping_total = Decimal('0.00')
        voucher_discount_total = Decimal('0.00')
        shipping_by_order = {}
        import_by_order = {}
        debug_import = []

        for o in orders:
            # shipping fee may be None
            ship = Decimal(str(o.shipping_fee or 0))
            # Check if shipping fee seems too small (likely in thousands instead of VND)
            if ship > 0 and ship < 1000:
                ship = ship * 1000
            shipping_total += ship
            shipping_by_order[str(o.id)] = float(ship)
            # Sum voucher discount applied on this order
            try:
                disc = Decimal(str(o.discount_applied or 0))
            except Exception:
                disc = Decimal('0.00')
            if needs_scaling and disc > 0 and disc < 1000:
                disc = disc * 1000
            voucher_discount_total += disc
            # sum import costs for each item
            for item in getattr(o, 'items').all():
                # Check if import_price needs scaling (likely in thousands instead of VND)
                unit_import = getattr(item.product, 'import_price', 0) or 0
                if unit_import > 0 and unit_import < 1000:
                    # Scale up if seems too small
                    unit_import_vnd = Decimal(str(unit_import)) * Decimal('1000')
                else:
                    unit_import_vnd = Decimal(str(unit_import))
                qty = Decimal(str(item.quantity or 0))
                sub = (unit_import_vnd * qty)
                import_total += sub
                import_by_order[str(o.id)] = float(Decimal(str(import_by_order.get(str(o.id), 0))) + sub)

                # Debug info
                debug_import.append({
                    'order_id': o.id,
                    'product_name': getattr(item.product, 'name', f'#{item.product_id}'),
                    'unit_import_raw': float(unit_import),
                    'unit_import_vnd': float(unit_import_vnd),
                    'quantity': float(qty),
                    'subtotal': float(sub)
                })

        total_profit = float(Decimal(str(total_revenue)) - import_total - shipping_total)

        # Build top lists (convert to list of dicts and take top 10)
        ts_list = sorted(
            [{'name': n, 'qty': float(q)} for n, q in top_selling.items()],
            key=lambda x: x['qty'], reverse=True
        )[:10]

        # Ensure top_revenue is properly scaled
        tr_list = []
        for name, revenue in top_revenue.items():
            # If revenue seems too small (< 1000), scale it up
            if revenue < 1000:
                revenue = revenue * 1000
            tr_list.append({'name': name, 'revenue': float(revenue)})

        tr_list = sorted(tr_list, key=lambda x: x['revenue'], reverse=True)[:10]

        # Calculate additional analytics
        total_orders = orders.count()
        average_order_value = float(total_revenue / total_orders) if total_orders > 0 else 0

        # Top customers by revenue
        customer_revenue = {}
        customer_phone_revenue = {}
        for o in orders:
            customer_name = o.customer_name or 'Khách vãng lai'
            phone = o.phone_number or 'N/A'
            order_revenue = float(o.total_amount or 0)

            if needs_scaling and order_revenue < 1000:
                order_revenue = order_revenue * 1000

            customer_revenue[customer_name] = customer_revenue.get(customer_name, 0) + order_revenue
            customer_phone_revenue[phone] = customer_phone_revenue.get(phone, 0) + order_revenue

        top_customers = sorted(
            [{'name': name, 'revenue': float(revenue)} for name, revenue in customer_revenue.items()],
            key=lambda x: x['revenue'], reverse=True
        )[:10]

        top_customer_phone = max(customer_phone_revenue.items(), key=lambda x: x[1])[0] if customer_phone_revenue else '-'
        # Build phone list for aggregation on frontend
        top_customers_phone = sorted(
            [{'phone': phone, 'revenue': float(rev)} for phone, rev in customer_phone_revenue.items()],
            key=lambda x: x['revenue'], reverse=True
        )[:10]

        # Top products by profit
        product_profit = {}
        for o in orders:
            for item in getattr(o, 'items').all():
                product_name = getattr(item.product, 'name', f'#{item.product_id}')
                qty = float(item.quantity or 0)
                price = float(item.price_at_purchase or 0)
                import_price = float(getattr(item.product, 'import_price', 0) or 0)

                if needs_scaling:
                    if price < 1000:
                        price = price * 1000
                    if import_price < 1000:
                        import_price = import_price * 1000

                revenue = price * qty
                cost = import_price * qty
                profit = revenue - cost

                product_profit[product_name] = product_profit.get(product_name, 0) + profit

        top_profit_products = sorted(
            [{'name': name, 'profit': float(profit)} for name, profit in product_profit.items()],
            key=lambda x: x['profit'], reverse=True
        )[:10]

        # Revenue by region (province)
        region_revenue = {}
        for o in orders:
            region = o.province or 'Không xác định'
            order_revenue = float(o.total_amount or 0)
            if needs_scaling and order_revenue < 1000:
                order_revenue = order_revenue * 1000
            region_revenue[region] = region_revenue.get(region, 0) + order_revenue

        revenue_by_region = sorted(
            [{'region': region, 'revenue': float(revenue)} for region, revenue in region_revenue.items()],
            key=lambda x: x['revenue'], reverse=True
        )[:10]

        # Revenue and quantity by category
        category_revenue = {}
        category_qty = {}
        for o in orders:
            for item in getattr(o, 'items').all():
                category_name = getattr(item.product.category, 'name', 'Không phân loại')
                qty = float(item.quantity or 0)
                price = float(item.price_at_purchase or 0)

                if needs_scaling and price < 1000:
                    price = price * 1000

                revenue = price * qty
                category_revenue[category_name] = category_revenue.get(category_name, 0) + revenue
                category_qty[category_name] = category_qty.get(category_name, 0) + qty

        revenue_by_category = sorted(
            [{'category': category, 'revenue': float(revenue)} for category, revenue in category_revenue.items()],
            key=lambda x: x['revenue'], reverse=True
        )[:10]

        qty_by_category = sorted(
            [{'category': category, 'qty': float(qty)} for category, qty in category_qty.items()],
            key=lambda x: x['qty'], reverse=True
        )[:10]

        # Revenue and quantity by brand
        brand_revenue = {}
        brand_qty = {}
        for o in orders:
            for item in getattr(o, 'items').all():
                brand_name = getattr(item.product.brand, 'name', 'Không xác định')
                qty = float(item.quantity or 0)
                price = float(item.price_at_purchase or 0)

                if needs_scaling and price < 1000:
                    price = price * 1000

                revenue = price * qty
                brand_revenue[brand_name] = brand_revenue.get(brand_name, 0) + revenue
                brand_qty[brand_name] = brand_qty.get(brand_name, 0) + qty

        revenue_by_brand = sorted(
            [{'brand': brand, 'revenue': float(revenue)} for brand, revenue in brand_revenue.items()],
            key=lambda x: x['revenue'], reverse=True
        )[:10]

        qty_by_brand = sorted(
            [{'brand': brand, 'qty': float(qty)} for brand, qty in brand_qty.items()],
            key=lambda x: x['qty'], reverse=True
        )[:10]

        snapshot = AnalyticsSnapshot.objects.update_or_create(
            period=period,
            period_key=period_key,
            defaults={
                'total_revenue': Decimal(str(total_revenue)),
                'total_profit': Decimal(str(total_profit)),
                'data': {
                    'labels': labels,
                    'series': series,
                    'top_selling': ts_list,
                    'top_revenue': tr_list,
                    'import_total': float(import_total),
                    'shipping_total': float(shipping_total),
                    'voucher_discount_total': float(voucher_discount_total),
                    'import_by_order': import_by_order,
                    'shipping_by_order': shipping_by_order,
                    'debug_import': debug_import[:10],  # Limit to first 10 for debugging
                    'debug_revenue': debug_revenue[:10],  # Debug revenue data
                    # Additional analytics
                    'total_orders': total_orders,
                    'average_order_value': average_order_value,
                    'top_customers': top_customers,
                    'top_customer_phone': top_customer_phone,
                    'top_customers_phone': top_customers_phone,
                    'top_profit_products': top_profit_products,
                    'revenue_by_region': revenue_by_region,
                    'revenue_by_category': revenue_by_category,
                    'revenue_by_brand': revenue_by_brand,
                    # Quantities for charts
                    'qty_by_category': qty_by_category,
                    'qty_by_brand': qty_by_brand,
                }
            }
        )[0]

        return snapshot

# --- Order-related Serializers ---

class VoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        fields = (
            'id', 'code', 'discount_type', 'discount_value', 'is_active',
            'min_order_amount', 'max_order_amount', 'valid_from', 'valid_to',
            'max_uses', 'times_used'
        )


class OrderItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('product', 'quantity')


class OrderItemReadSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'quantity', 'price_at_purchase')


class OrderSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    items = OrderItemReadSerializer(many=True, read_only=True)
    items_data = OrderItemWriteSerializer(many=True, write_only=True)
    voucher_code = serializers.CharField(write_only=True, required=False)
    order_note = serializers.CharField(write_only=True, required=False, source='notes')
    # Thêm trường is_confirmed để admin xác nhận đã giao hàng
    is_confirmed = serializers.BooleanField(required=False)

    class Meta:
        model = Order
        fields = (
            'id', 'customer', 'customer_name', 'phone_number', 'email', 'street',
            'ward', 'district', 'province', 'notes', 'order_note', 'payment_method',
            'bank_transfer_image', 'order_date', 'total_amount', 'shipping_fee', 'collaborator_code',
            'discount_applied', 'items', 'items_data', 'voucher_code', 'is_confirmed', 'status'
        )
        read_only_fields = ('total_amount', 'discount_applied')

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items_data', [])
        voucher_code = validated_data.pop('voucher_code', None)
        # Loại bỏ trường is_confirmed khi tạo đơn hàng
        validated_data.pop('is_confirmed', None)

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['customer'] = request.user

        order_total = Decimal('0.00')
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            if product.stock_quantity < quantity:
                raise serializers.ValidationError({"detail": f"Sản phẩm {product.name} chỉ còn {product.stock_quantity} sản phẩm trong kho."})
            order_total += product.discounted_price * quantity

        discount_amount = Decimal('0.00')
        voucher = None
        if voucher_code:
            try:
                voucher = Voucher.objects.get(
                    code=voucher_code,
                    is_active=True,
                    valid_from__lte=timezone.now(),
                    valid_to__gte=timezone.now(),
                    max_uses__gt=F('times_used')
                )
            except Voucher.DoesNotExist:
                raise serializers.ValidationError({"voucher_code": "Mã voucher không hợp lệ hoặc đã hết hạn."})

            if voucher.min_order_amount > order_total:
                raise serializers.ValidationError({"voucher_code": f"Đơn hàng phải có giá trị tối thiểu là {voucher.min_order_amount} để sử dụng voucher này."})

            discount_amount = voucher.get_discount_amount(order_total)
            if voucher.discount_type == "percentage" and voucher.max_order_amount > 0 and discount_amount > voucher.max_order_amount:
                discount_amount = voucher.max_order_amount

        # Lấy phí ship từ request data
        shipping_fee = validated_data.get('shipping_fee', Decimal('0'))
        if shipping_fee is None:
            shipping_fee = Decimal('0')

        validated_data['total_amount'] = order_total - discount_amount + shipping_fee
        validated_data['shipping_fee'] = shipping_fee
        validated_data['discount_applied'] = discount_amount
        if voucher:
            validated_data['voucher'] = voucher

        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            price_at_purchase = product.discounted_price

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_purchase=price_at_purchase
            )

        if voucher:
            voucher.times_used = F('times_used') + 1
            voucher.save(update_fields=['times_used'])

        return order

    @transaction.atomic
    def update(self, instance, validated_data):
        # Lấy giá trị is_confirmed và status từ validated_data
        is_confirmed = validated_data.get('is_confirmed')
        status = validated_data.get('status')

        # Đảm bảo is_confirmed không thể thay đổi từ True về False
        if instance.is_confirmed and is_confirmed is False:
            validated_data['is_confirmed'] = True

        # Kiểm tra nếu đơn hàng được xác nhận và chưa được xác nhận trước đó
        if is_confirmed and not instance.is_confirmed:
            # Đảm bảo is_confirmed luôn là True khi xác nhận
            validated_data['is_confirmed'] = True
            # Cập nhật status thành 'processing' khi xác nhận
            if status is None:
                validated_data['status'] = 'processing'

            # Lặp qua các sản phẩm trong đơn hàng
            for item in instance.items.all():
                product = item.product
                quantity = item.quantity

                # Cập nhật số lượng tồn kho và đã bán
                product.stock_quantity = F('stock_quantity') - quantity
                product.sold_quantity = F('sold_quantity') + quantity
                product.save(update_fields=['stock_quantity', 'sold_quantity'])

        # Kiểm tra nếu đơn hàng bị hủy
        elif status == 'cancelled' and instance.status != 'cancelled':
            # Đảm bảo is_confirmed vẫn là True khi hủy đơn hàng
            validated_data['is_confirmed'] = True

            # Hoàn trả số lượng sản phẩm về kho
            for item in instance.items.all():
                product = item.product
                quantity = item.quantity

                # Hoàn trả số lượng tồn kho
                product.stock_quantity = F('stock_quantity') + quantity
                product.sold_quantity = F('sold_quantity') - quantity
                product.save(update_fields=['stock_quantity', 'sold_quantity'])

        # Gọi phương thức update mặc định để lưu các thay đổi khác
        return super().update(instance, validated_data)




class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True, source='product'
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity']
        read_only_fields = ['id', 'product']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items']
        read_only_fields = ['user']

class BlogSerializer(serializers.ModelSerializer):
    """
    Serializer cho model Blog
    """
    class Meta:
        model = Blog
        fields = '__all__'



# --- Lucky Event Serializers ---
class LuckyPrizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LuckyPrize
        fields = ['id', 'name', 'image', 'value', 'order']


class LuckyEventSerializer(serializers.ModelSerializer):
    prizes = LuckyPrizeSerializer(many=True, read_only=True)

    class Meta:
        model = LuckyEvent
        fields = ['id', 'title', 'description', 'start_at', 'end_at', 'is_active', 'lucky_number', 'prizes']


class LuckyParticipantCreateSerializer(serializers.ModelSerializer):
    chosen_number = serializers.RegexField(regex=r'^\d{2}$', max_length=2)

    class Meta:
        model = LuckyParticipant
        fields = ['event', 'chosen_number', 'name', 'zalo_phone', 'address', 'message']

    def validate(self, attrs):
        event = attrs.get('event')
        zalo_phone = attrs.get('zalo_phone')
        from django.utils import timezone
        now = timezone.now()
        
        if not (event.is_active and event.start_at <= now <= event.end_at):
            raise serializers.ValidationError('Sự kiện không trong thời gian tham gia.')
        
        # Kiểm tra số điện thoại đã tham gia chưa
        if LuckyParticipant.objects.filter(event=event, zalo_phone=zalo_phone).exists():
            raise serializers.ValidationError('Số điện thoại này đã tham gia sự kiện trước đó. Mỗi số điện thoại chỉ được tham gia 1 lần duy nhất!')
        
        return attrs

    def create(self, validated_data):
        # Tự động set thời gian gửi khi tạo mới
        from django.utils import timezone
        validated_data['submitted_at'] = timezone.now()
        return super().create(validated_data)


class LuckyParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = LuckyParticipant
        fields = ['id', 'chosen_number', 'name', 'zalo_phone', 'address', 'message', 'submitted_at']


class LuckyWinnerSerializer(serializers.ModelSerializer):
    participant = LuckyParticipantSerializer()
    prize = LuckyPrizeSerializer()

    class Meta:
        model = LuckyWinner
        fields = ['participant', 'prize', 'decided_at']


# --- CTV (Affiliate) Serializers ---
class CTVLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CTVLevel
        fields = ['id', 'name', 'commission_percent', 'description']


class CTVApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CTVApplication
        fields = [
            'id', 'full_name', 'phone', 'email', 'address',
            'bank_name', 'bank_number', 'bank_holder',
            'cccd_front_url', 'cccd_back_url', 'sales_plan',
            'agreed', 'status', 'created_at'
        ]

    def validate(self, attrs):
        required = ['full_name', 'phone', 'email', 'bank_name', 'bank_number', 'bank_holder', 'cccd_front_url', 'cccd_back_url']
        for f in required:
            if not attrs.get(f):
                raise serializers.ValidationError({f: 'Trường này là bắt buộc'})
        if not attrs.get('agreed', False):
            raise serializers.ValidationError({'agreed': 'Bạn phải đồng ý với quy định'})
        return attrs


class CTVSerializer(serializers.ModelSerializer):
    level = CTVLevelSerializer(read_only=True)

    class Meta:
        model = CTV
        fields = [
            'id', 'code', 'full_name', 'phone', 'email', 'address',
            'bank_name', 'bank_number', 'bank_holder', 'level', 'is_active', 'joined_at'
        ]


class CTVWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = CTVWallet
        fields = ['balance', 'pending', 'updated_at']


class CTVWithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CTVWithdrawal
        fields = ['id', 'amount', 'status', 'requested_at', 'processed_at', 'note']

