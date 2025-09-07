from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from .google_social_auth import Google
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import F
from decimal import Decimal
from django.utils import timezone


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
        read_only_fields = ['id', 'phone_number']

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
        min_length=8
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


# class OrderSerializer(serializers.ModelSerializer):
#     customer = UserSerializer(read_only=True)
#     items = OrderItemReadSerializer(many=True, read_only=True)
#     items_data = OrderItemWriteSerializer(many=True, write_only=True)
#     voucher_code = serializers.CharField(write_only=True, required=False)

#     class Meta:
#         model = Order
#         fields = (
#             'id', 'customer', 'customer_name', 'phone_number', 'email', 'street',
#             'ward', 'district', 'province', 'notes', 'payment_method',
#             'bank_transfer_image', 'order_date', 'total_amount', 'collaborator_code',
#             'discount_applied', 'items', 'items_data', 'voucher_code'
#         )
#         read_only_fields = ('total_amount', 'discount_applied')

#     @transaction.atomic
#     def create(self, validated_data):
#         items_data = validated_data.pop('items_data', [])
#         voucher_code = validated_data.pop('voucher_code', None)

#         request = self.context.get('request')
#         if request and request.user.is_authenticated:
#             validated_data['customer'] = request.user

#         # Lấy voucher và tính toán tổng tiền tạm thời trước khi tạo đơn hàng
#         order_total = Decimal('0.00')
#         for item_data in items_data:
#             product = item_data['product']
#             quantity = item_data['quantity']
#             if product.stock_quantity < quantity:
#                 raise serializers.ValidationError({"detail": f"Sản phẩm {product.name} chỉ còn {product.stock_quantity} sản phẩm trong kho."})
#             order_total += product.discounted_price * quantity

#         discount_amount = Decimal('0.00')
#         voucher = None
#         if voucher_code:
#             try:
#                 voucher = Voucher.objects.get(
#                     code=voucher_code,
#                     is_active=True,
#                     valid_from__lte=timezone.now(),
#                     valid_to__gte=timezone.now(),
#                     max_uses__gt=F('times_used')
#                 )
#             except Voucher.DoesNotExist:
#                 raise serializers.ValidationError({"voucher_code": "Mã voucher không hợp lệ hoặc đã hết hạn."})

#             if voucher.min_order_amount > order_total:
#                 raise serializers.ValidationError({"voucher_code": f"Đơn hàng phải có giá trị tối thiểu là {voucher.min_order_amount} để sử dụng voucher này."})

#             discount_amount = voucher.get_discount_amount(order_total)
#             if voucher.discount_type == "percentage" and voucher.max_order_amount > 0 and discount_amount > voucher.max_order_amount:
#                 discount_amount = voucher.max_order_amount

#         # Gán giá trị ban đầu cho total_amount và discount_applied trước khi tạo Order
#         validated_data['total_amount'] = order_total - discount_amount
#         validated_data['discount_applied'] = discount_amount
#         if voucher:
#             validated_data['voucher'] = voucher

#         # Tạo đối tượng Order ban đầu
#         order = Order.objects.create(**validated_data)

#         # Tạo OrderItems và cập nhật số lượng tồn kho
#         for item_data in items_data:
#             product = item_data['product']
#             quantity = item_data['quantity']
#             price_at_purchase = product.discounted_price

#             OrderItem.objects.create(
#                 order=order,
#                 product=product,
#                 quantity=quantity,
#                 price_at_purchase=price_at_purchase
#             )

#             product.stock_quantity = F('stock_quantity') - quantity
#             product.sold_quantity = F('sold_quantity') + quantity
#             product.save(update_fields=['stock_quantity', 'sold_quantity'])

#         # Cập nhật số lần sử dụng của voucher
#         if voucher:
#             voucher.times_used = F('times_used') + 1
#             voucher.save(update_fields=['times_used'])

#         # Do đã tính toán và gán giá trị trước, nên không cần cập nhật lại
#         return order


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


# from rest_framework import serializers
# from .models import *
# from rest_framework_simplejwt.tokens import RefreshToken
# from .google_social_auth import Google
# from django.contrib.auth import authenticate
# from django.db import transaction
# from django.db.models import F

# # --- User Serializers ---

# class UserSerializer(serializers.ModelSerializer):
#     """
#     Serializer để hiển thị và cập nhật thông tin người dùng.
#     Bao gồm các trường điểm và cấp độ.
#     """
#     points = serializers.SerializerMethodField()
#     level = serializers.SerializerMethodField()

#     class Meta:
#         model = User
#         fields = ('id', 'name', 'email', 'phone_number', 'address', 'dob', 'avatar', 'points', 'level')

#     def get_points(self, obj):
#         if isinstance(obj, (Customer, Collaborator)):
#             return obj.points
#         return 0

#     def get_level(self, obj):
#         if isinstance(obj, (Customer, Collaborator)):
#             return obj.level
#         return 1


# class UserProfileSerializer(serializers.ModelSerializer):
#     """
#     Serializer để hiển thị và chỉnh sửa thông tin hồ sơ người dùng.
#     """
#     points = serializers.SerializerMethodField()
#     level = serializers.SerializerMethodField()

#     class Meta:
#         model = User
#         fields = [
#             'id',
#             'phone_number',
#             'email',
#             'name',
#             'address',
#             'dob',
#             'avatar',
#             'points',
#             'level'
#         ]
#         read_only_fields = ['id', 'phone_number']

#     def validate_email(self, value):
#         if value and self.instance and User.objects.exclude(id=self.instance.id).filter(email=value).exists():
#             raise serializers.ValidationError("Email này đã được sử dụng. Vui lòng chọn một email khác.")
#         return value

#     def get_points(self, obj):
#         try:
#             if isinstance(obj, Customer):
#                 return obj.customer.points
#             elif isinstance(obj, Collaborator):
#                 return obj.collaborator.points
#         except (Customer.DoesNotExist, Collaborator.DoesNotExist):
#             pass
#         return 0

#     def get_level(self, obj):
#         try:
#             if isinstance(obj, Customer):
#                 return obj.customer.level
#             elif isinstance(obj, Collaborator):
#                 return obj.collaborator.level
#         except (Customer.DoesNotExist, Collaborator.DoesNotExist):
#             pass
#         return 1


# class CollaboratorSerializer(serializers.ModelSerializer):
#     """
#     Serializer cho mô hình Collaborator.
#     """
#     # Không cần UserSerializer lồng vào vì thông tin đã có trong mô hình Collaborator
#     class Meta:
#         model = Collaborator
#         fields = ('id', 'name', 'email', 'phone_number', 'sales_code', 'points', 'level')
#         read_only_fields = ('id', 'name', 'email', 'phone_number', 'points', 'level')


# class PhoneNumberLoginSerializer(serializers.Serializer):
#     """
#     Serializer để xử lý đăng nhập bằng số điện thoại và mật khẩu.
#     """
#     phone_number = serializers.CharField(max_length=15)
#     password = serializers.CharField(write_only=True)
#     user_info = serializers.SerializerMethodField()

#     def validate(self, data):
#         phone_number = data.get('phone_number')
#         password = data.get('password')

#         if not phone_number or not password:
#             raise serializers.ValidationError('Vui lòng cung cấp cả số điện thoại và mật khẩu.')

#         user = authenticate(request=self.context.get('request'),
#                             phone_number=phone_number, password=password)

#         if not user:
#             raise serializers.ValidationError('Số điện thoại hoặc mật khẩu không đúng.')

#         if not user.is_active:
#             raise serializers.ValidationError('Tài khoản đã bị vô hiệu hóa.')

#         self.user = user  # Lưu người dùng vào self để sử dụng trong get_user_info
#         return data

#     def get_user_info(self, data):
#         if self.user:
#             return UserSerializer(self.user).data
#         return None

#     def to_representation(self, instance):
#         representation = super().to_representation(instance)

#         # Lấy người dùng từ validated data
#         user = self.user

#         # Lấy JWT tokens
#         refresh = RefreshToken.for_user(user)
#         representation['access_token'] = str(refresh.access_token)
#         representation['refresh_token'] = str(refresh)

#         # Trả về thông tin người dùng chi tiết
#         representation['user'] = UserSerializer(user).data

#         return representation


# class GoogleSocialAuthSerializer(serializers.Serializer):
#     """
#     Serializer để xử lý xác thực xã hội bằng Google.
#     """
#     auth_token = serializers.CharField()

#     def validate_auth_token(self, auth_token):
#         try:
#             user_data = Google.validate(auth_token)
#         except ValueError as e:
#             raise serializers.ValidationError(str(e))
#         except Exception as e:
#             raise serializers.ValidationError(f"Google token validation failed: {str(e)}")

#         email = user_data.get('email', '')
#         name = user_data.get('name', '')
#         avatar = user_data.get('picture', None)

#         if not email:
#             raise serializers.ValidationError("Email is not provided in Google token.")

#         try:
#             with transaction.atomic():
#                 user, created = User.objects.get_or_create(
#                     email=email,
#                     defaults={
#                         'name': name,
#                         'avatar': avatar,
#                         'is_google_user': True,
#                         'is_active': True,
#                     }
#                 )
#                 if created:
#                     # Gán user_type='customer' và tạo Customer object liên quan
#                     Customer.objects.create(
#                         user_ptr=user,
#                         name=name,
#                         email=email,
#                         avatar=avatar,
#                         is_google_user=True,
#                     )
#                 else:
#                     # Nếu người dùng đã tồn tại, cập nhật thông tin nếu cần
#                     if not user.name:
#                         user.name = name
#                     if not user.avatar:
#                         user.avatar = avatar
#                     user.is_google_user = True
#                     user.save()
#         except Exception as e:
#             print(f"Lỗi khi xử lý người dùng Google: {e}")
#             raise serializers.ValidationError(f"Lỗi khi xử lý dữ liệu người dùng: {str(e)}")

#         return user


# class RegistrationSerializer(serializers.ModelSerializer):
#     """
#     Serializer cho đăng ký người dùng.
#     """
#     password = serializers.CharField(
#         write_only=True,
#         required=True,
#         style={'input_type': 'password'},
#         min_length=8
#     )
#     user_type = serializers.CharField(write_only=True, required=False, default='customer')


#     class Meta:
#         model = User
#         fields = ('name', 'phone_number', 'password', 'email', 'avatar', 'user_type')
#         extra_kwargs = {
#             'phone_number': {'required': False},
#             'email': {'required': False},
#             'name': {'required': False},
#             'avatar': {'required': False},
#         }

#     def validate(self, data):
#         phone_number = data.get('phone_number')
#         email = data.get('email')

#         if not phone_number and not email:
#             raise serializers.ValidationError("Phải cung cấp số điện thoại hoặc email.")

#         if phone_number and User.objects.filter(phone_number=phone_number).exists():
#             raise serializers.ValidationError("Số điện thoại này đã được đăng ký.")

#         if email and User.objects.filter(email=email).exists():
#             raise serializers.ValidationError("Email này đã được đăng ký.")

#         return data

#     def create(self, validated_data):
#         user_type = validated_data.pop('user_type', 'customer')
#         password = validated_data.pop('password')

#         with transaction.atomic():
#             user = User.objects.create_user(
#                 password=password,
#                 **validated_data
#             )

#             # Sau khi user được tạo, tạo đối tượng con tương ứng
#             if user_type == 'customer':
#                 Customer.objects.create(user_ptr=user, **validated_data)
#             elif user_type == 'collaborator':
#                 Collaborator.objects.create(user_ptr=user, **validated_data)
#             elif user_type == 'staff':
#                 Staff.objects.create(user_ptr=user, **validated_data)

#             return user


# class ForgotPasswordSerializer(serializers.Serializer):
#     """
#     Serializer để xử lý yêu cầu quên mật khẩu.
#     """
#     email = serializers.EmailField(required=True)


# # --- Product-related Serializers ---

# class BrandSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Brand
#         fields = ('id', 'name', 'country', 'introduction')


# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ('id', 'name')


# class TagSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tag
#         fields = ['id', 'code', 'name', 'description', 'start_date', 'end_date', 'status', 'discounted_price_reduction']


# class GiftSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Gift
#         fields = ('id', 'name', 'description', 'image')


# # Sửa lại ProductSerializer
# class ProductSerializer(serializers.ModelSerializer):
#     """
#     Serializer cho Product, hiển thị tên hãng và tên tags
#     """
#     brand_name = serializers.CharField(source='brand.name', read_only=True)
#     category_name = serializers.CharField(source='category.name', read_only=True)
#     brand_id = serializers.PrimaryKeyRelatedField(
#         queryset=Brand.objects.all(),
#         source='brand',
#         write_only=True
#     )
#     # Thay đổi StringRelatedField thành SlugRelatedField
#     tags = serializers.SlugRelatedField(
#         many=True,
#         read_only=True,
#         slug_field='name' # Chỉ định trường 'name' để hiển thị
#     )

#     class Meta:
#         model = Product
#         fields = (
#             'id', 'name', 'description',
#             'image', 'brand_name', 'brand_id', 'tags', 'gifts', 'stock_quantity', 'sold_quantity',
#             'rating', 'savings_price', 'import_price', 'original_price',
#             'discount_rate', 'discounted_price', 'status','category_name'
#         )
#         read_only_fields = ('savings_price', 'discount_rate')


# # --- Order-related Serializers ---

# class VoucherSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Voucher
#         fields = (
#             'id', 'code', 'discount_type', 'discount_value', 'is_active',
#             'min_order_amount', 'max_order_amount', 'valid_from', 'valid_to',
#             'max_uses', 'times_used'
#         )


# class OrderItemWriteSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OrderItem
#         fields = ('product', 'quantity')

# # Serializer cho việc hiển thị (read-only) OrderItem
# class OrderItemReadSerializer(serializers.ModelSerializer):
#     product = ProductSerializer(read_only=True)

#     class Meta:
#         model = OrderItem
#         fields = ('id', 'product', 'quantity', 'price_at_purchase')

# # Order Serializer
# class OrderSerializer(serializers.ModelSerializer):
#     customer = UserSerializer(read_only=True)
#     # Sử dụng serializer đọc cho hiển thị
#     items = OrderItemReadSerializer(many=True, read_only=True)
#     # Thêm trường để nhận danh sách items khi tạo/cập nhật
#     items_data = OrderItemWriteSerializer(many=True, write_only=True, required=False)
#     voucher_code = serializers.CharField(write_only=True, required=False)

#     class Meta:
#         model = Order
#         fields = (
#             'id', 'customer', 'customer_name', 'phone_number', 'email', 'street',
#             'ward', 'district', 'province', 'notes', 'payment_method',
#             'bank_transfer_image', 'order_date', 'total_amount', 'collaborator_code',
#             'discount_applied', 'items', 'items_data', 'voucher_code'
#         )
#         read_only_fields = ('total_amount', 'discount_applied')

#     @transaction.atomic
#     def create(self, validated_data):
#         items_data = validated_data.pop('items_data', [])
#         voucher_code = validated_data.pop('voucher_code', None)

#         request = self.context.get('request')
#         if request and request.user.is_authenticated:
#             validated_data['customer'] = request.user

#         # Lưu thông tin voucher_id và discount_applied để xử lý sau
#         voucher = None
#         if voucher_code:
#             try:
#                 voucher = Voucher.objects.get(
#                     code=voucher_code,
#                     is_active=True,
#                     valid_from__lte=timezone.now(),
#                     valid_to__gte=timezone.now(),
#                     max_uses__gt=F('times_used')
#                 )
#                 validated_data['voucher'] = voucher
#             except Voucher.DoesNotExist:
#                 raise serializers.ValidationError({"voucher_code": "Mã voucher không hợp lệ hoặc đã hết hạn."})

#         # Tạm thời đặt total_amount và discount_applied về 0 để tạo đối tượng
#         # Sau đó sẽ cập nhật lại sau khi tính toán
#         validated_data['total_amount'] = Decimal('0.00')
#         validated_data['discount_applied'] = Decimal('0.00')

#         # Tạo đối tượng Order ban đầu
#         order = Order.objects.create(**validated_data)

#         # Tạo OrderItems và tính toán tổng tiền
#         order_total = Decimal('0.00')
#         for item_data in items_data:
#             product = item_data['product']
#             quantity = item_data['quantity']
#             price_at_purchase = product.discounted_price

#             OrderItem.objects.create(
#                 order=order,
#                 product=product,
#                 quantity=quantity,
#                 price_at_purchase=price_at_purchase
#             )
#             order_total += price_at_purchase * quantity

#         # Tính toán giảm giá và tổng tiền cuối cùng
#         discount_amount = Decimal('0.00')
#         if voucher:
#             # Kiểm tra giá trị đơn hàng tối thiểu
#             if voucher.min_order_amount > order_total:
#                 raise serializers.ValidationError({"voucher_code": f"Đơn hàng phải có giá trị tối thiểu là {voucher.min_order_amount} để sử dụng voucher này."})

#             discount_amount = voucher.get_discount_amount(order_total)
#             if voucher.discount_type == "percentage" and voucher.max_order_amount > 0 and discount_amount > voucher.max_order_amount:
#                 discount_amount = voucher.max_order_amount

#             # Tăng số lần sử dụng của voucher
#             voucher.times_used = F('times_used') + 1
#             voucher.save(update_fields=['times_used'])

#         # Cập nhật lại tổng tiền và giảm giá sau khi đã tính toán
#         order.discount_applied = discount_amount
#         order.total_amount = order_total - discount_amount
#         order.save(update_fields=['total_amount', 'discount_applied'])

#         return order


# class CartItemSerializer(serializers.ModelSerializer):
#     product = ProductSerializer(read_only=True)
#     product_id = serializers.PrimaryKeyRelatedField(
#         queryset=Product.objects.all(), write_only=True, source='product'
#     )

#     class Meta:
#         model = CartItem
#         fields = ['id', 'product', 'product_id', 'quantity']
#         read_only_fields = ['id', 'product']


# class CartSerializer(serializers.ModelSerializer):
#     items = CartItemSerializer(many=True, read_only=True)

#     class Meta:
#         model = Cart
#         fields = ['id', 'user', 'items']
#         read_only_fields = ['user']





# from rest_framework import serializers
# from .models import *
# from rest_framework_simplejwt.tokens import RefreshToken
# from .google_social_auth import Google
# from django.contrib.auth import authenticate
# from django.db import transaction
# from django.db.models import F

# # --- User Serializers ---

# class UserSerializer(serializers.ModelSerializer):
#     """
#     Serializer to display and update user profile information.
#     """
#     class Meta:
#         model = User
#         fields = ('id', 'name', 'email', 'phone_number', 'address', 'dob', 'avatar')


# class UserProfileSerializer(serializers.ModelSerializer):
#     """
#     Serializer to display and edit user profile information.
#     """
#     class Meta:
#         model = User
#         fields = [
#             'id',
#             'phone_number',
#             'email',
#             'name',
#             'address',
#             'dob',
#             'avatar'
#         ]
#         read_only_fields = ['id', 'phone_number']

#     def validate_email(self, value):
#         if value and self.instance and User.objects.exclude(id=self.instance.id).filter(email=value).exists():
#             raise serializers.ValidationError("Email này đã được sử dụng. Vui lòng chọn một email khác.")
#         return value


# class CollaboratorSerializer(serializers.ModelSerializer):
#     """
#     Serializer for the Collaborator model.
#     """
#     user = UserSerializer()

#     class Meta:
#         model = Collaborator
#         fields = ('user', 'sales_code')


# class PhoneNumberLoginSerializer(serializers.Serializer):
#     """
#     Serializer to handle login with phone number and password,
#     and return user info and JWT tokens.
#     """
#     phone_number = serializers.CharField(max_length=15)
#     password = serializers.CharField(write_only=True)
#     user_info = serializers.SerializerMethodField()

#     def validate(self, data):
#         phone_number = data.get('phone_number')
#         password = data.get('password')

#         if not phone_number or not password:
#             raise serializers.ValidationError('Vui lòng cung cấp cả số điện thoại và mật khẩu.')

#         user = authenticate(request=self.context.get('request'),
#                             phone_number=phone_number, password=password)

#         if not user:
#             raise serializers.ValidationError('Số điện thoại hoặc mật khẩu không đúng.')

#         if not user.is_active:
#             raise serializers.ValidationError('Tài khoản đã bị vô hiệu hóa.')

#         self.user = user  # Lưu người dùng vào self để sử dụng trong get_user_info
#         return data

#     def get_user_info(self, data):
#         if self.user:
#             return UserSerializer(self.user).data
#         return None

#     def to_representation(self, instance):
#         representation = super().to_representation(instance)

#         # Lấy người dùng từ validated data
#         user = self.user

#         # Lấy JWT tokens
#         refresh = RefreshToken.for_user(user)
#         representation['access_token'] = str(refresh.access_token)
#         representation['refresh_token'] = str(refresh)

#         # Trả về thông tin người dùng chi tiết
#         representation['user'] = UserSerializer(user).data

#         return representation


# class GoogleSocialAuthSerializer(serializers.Serializer):
#     """
#     Serializer to handle Google social authentication.
#     """
#     auth_token = serializers.CharField()

#     def validate_auth_token(self, auth_token):
#         try:
#             user_data = Google.validate(auth_token)
#         except ValueError as e:
#             raise serializers.ValidationError(str(e))
#         except Exception as e:
#             raise serializers.ValidationError(f"Google token validation failed: {str(e)}")

#         email = user_data.get('email', '')
#         name = user_data.get('name', '')
#         avatar = user_data.get('picture', None)

#         if not email:
#             raise serializers.ValidationError("Email is not provided in Google token.")

#         try:
#             # Sử dụng get_or_create để tìm hoặc tạo người dùng
#             user, created = User.objects.get_or_create(
#                 email=email,
#                 defaults={
#                     'name': name,
#                     'avatar': avatar,
#                     'is_google_user': True,
#                     'is_active': True,
#                 }
#             )
#             if created:
#                 # Gán user_type='customer' và tạo Customer object liên quan
#                 Customer.objects.create(user_ptr=user, name=name, email=email, avatar=avatar, is_google_user=True)
#             else:
#                 # Nếu người dùng đã tồn tại, cập nhật thông tin nếu cần
#                 if not user.name:
#                     user.name = name
#                 if not user.avatar:
#                     user.avatar = avatar
#                 user.is_google_user = True  # Đánh dấu là người dùng Google
#                 user.save()

#         except Exception as e:
#             print(f"Lỗi khi xử lý người dùng Google: {e}")
#             raise serializers.ValidationError(f"Lỗi khi xử lý dữ liệu người dùng: {str(e)}")

#         return user


# class RegistrationSerializer(serializers.ModelSerializer):
#     """
#     Serializer for user registration.
#     """
#     password = serializers.CharField(
#         write_only=True,
#         required=True,
#         style={'input_type': 'password'},
#         min_length=8
#     )
#     user_type = serializers.CharField(write_only=True, required=False, default='customer')


#     class Meta:
#         model = User
#         fields = ('name', 'phone_number', 'password', 'email', 'avatar', 'user_type')
#         extra_kwargs = {
#             'phone_number': {'required': False},
#             'email': {'required': False},
#             'name': {'required': False},
#             'avatar': {'required': False},
#         }

#     def validate(self, data):
#         phone_number = data.get('phone_number')
#         email = data.get('email')

#         if not phone_number and not email:
#             raise serializers.ValidationError("Phải cung cấp số điện thoại hoặc email.")

#         if phone_number and User.objects.filter(phone_number=phone_number).exists():
#             raise serializers.ValidationError("Số điện thoại này đã được đăng ký.")

#         if email and User.objects.filter(email=email).exists():
#             raise serializers.ValidationError("Email này đã được đăng ký.")

#         return data

#     def create(self, validated_data):
#         user_type = validated_data.pop('user_type', 'customer')
#         password = validated_data.pop('password')

#         with transaction.atomic():
#             user = User.objects.create_user(
#                 password=password,
#                 **validated_data
#             )

#             # Sau khi user được tạo, tạo đối tượng con tương ứng
#             if user_type == 'customer':
#                 Customer.objects.create(user_ptr=user)
#             elif user_type == 'collaborator':
#                 Collaborator.objects.create(user_ptr=user)
#             elif user_type == 'staff':
#                 Staff.objects.create(user_ptr=user)
#             # Bạn có thể thêm các loại user khác ở đây

#             user.save()
#             return user


# class ForgotPasswordSerializer(serializers.Serializer):
#     """
#     Serializer to handle forgot password requests.
#     """
#     email = serializers.EmailField(required=True)


# # --- Product-related Serializers ---

# class BrandSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Brand
#         fields = ('id', 'name', 'country', 'introduction')


# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ('id', 'name')


# class TagSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tag
#         fields = ['id', 'code', 'name', 'description', 'start_date', 'end_date', 'status', 'discounted_price_reduction']

# class GiftSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Gift
#         fields = ('id', 'name', 'description', 'image')


# # Sửa lại ProductSerializer
# class ProductSerializer(serializers.ModelSerializer):
#     """
#     Serializer cho Product, hiển thị tên hãng và tên tags
#     """
#     brand_name = serializers.CharField(source='brand.name', read_only=True)
#     category_name = serializers.CharField(source='category.name', read_only=True)
#     brand_id = serializers.PrimaryKeyRelatedField(
#         queryset=Brand.objects.all(),
#         source='brand',
#         write_only=True
#     )
#     # Thay đổi StringRelatedField thành SlugRelatedField
#     tags = serializers.SlugRelatedField(
#         many=True,
#         read_only=True,
#         slug_field='name' # Chỉ định trường 'name' để hiển thị
#     )

#     class Meta:
#         model = Product
#         fields = (
#             'id', 'name', 'description',
#             'image', 'brand_name', 'brand_id', 'tags', 'gifts', 'stock_quantity', 'sold_quantity',
#             'rating', 'savings_price', 'import_price', 'original_price',
#             'discount_rate', 'discounted_price', 'status','category_name'
#         )
#         read_only_fields = ('savings_price', 'discount_rate')
# # --- Order-related Serializers ---

# class VoucherSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Voucher
#         fields = (
#             'id', 'code', 'discount_type', 'discount_value', 'is_active',
#             'min_order_amount', 'max_order_amount', 'valid_from', 'valid_to',
#             'max_uses', 'times_used'
#         )


# class OrderItemWriteSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OrderItem
#         fields = ('product', 'quantity')

# # Serializer cho việc hiển thị (read-only) OrderItem
# class OrderItemReadSerializer(serializers.ModelSerializer):
#     product = ProductSerializer(read_only=True)

#     class Meta:
#         model = OrderItem
#         fields = ('id', 'product', 'quantity', 'price_at_purchase')

# # Order Serializer
# class OrderSerializer(serializers.ModelSerializer):
#     customer = UserSerializer(read_only=True)
#     # Sử dụng serializer đọc cho hiển thị
#     items = OrderItemReadSerializer(many=True, read_only=True)
#     # Thêm trường để nhận danh sách items khi tạo/cập nhật
#     items_data = OrderItemWriteSerializer(many=True, write_only=True, required=False)
#     voucher_code = serializers.CharField(write_only=True, required=False)

#     class Meta:
#         model = Order
#         fields = (
#             'id', 'customer', 'customer_name', 'phone_number', 'email', 'street',
#             'ward', 'district', 'province', 'notes', 'payment_method',
#             'bank_transfer_image', 'order_date', 'total_amount', 'collaborator_code',
#             'discount_applied', 'items', 'items_data', 'voucher_code'
#         )
#         read_only_fields = ('total_amount', 'discount_applied')

#     @transaction.atomic
#     def create(self, validated_data):
#         items_data = validated_data.pop('items_data', [])
#         voucher_code = validated_data.pop('voucher_code', None)

#         request = self.context.get('request')
#         if request and request.user.is_authenticated:
#             validated_data['customer'] = request.user

#         # Lưu thông tin voucher_id và discount_applied để xử lý sau
#         voucher = None
#         if voucher_code:
#             try:
#                 voucher = Voucher.objects.get(
#                     code=voucher_code,
#                     is_active=True,
#                     valid_from__lte=timezone.now(),
#                     valid_to__gte=timezone.now(),
#                     max_uses__gt=F('times_used')
#                 )
#                 validated_data['voucher'] = voucher
#             except Voucher.DoesNotExist:
#                 raise serializers.ValidationError({"voucher_code": "Mã voucher không hợp lệ hoặc đã hết hạn."})

#         # Tạm thời đặt total_amount và discount_applied về 0 để tạo đối tượng
#         # Sau đó sẽ cập nhật lại sau khi tính toán
#         validated_data['total_amount'] = Decimal('0.00')
#         validated_data['discount_applied'] = Decimal('0.00')

#         # Tạo đối tượng Order ban đầu
#         order = Order.objects.create(**validated_data)

#         # Tạo OrderItems và tính toán tổng tiền
#         order_total = Decimal('0.00')
#         for item_data in items_data:
#             product = item_data['product']
#             quantity = item_data['quantity']
#             price_at_purchase = product.discounted_price

#             OrderItem.objects.create(
#                 order=order,
#                 product=product,
#                 quantity=quantity,
#                 price_at_purchase=price_at_purchase
#             )
#             order_total += price_at_purchase * quantity

#         # Tính toán giảm giá và tổng tiền cuối cùng
#         discount_amount = Decimal('0.00')
#         if voucher:
#             # Kiểm tra giá trị đơn hàng tối thiểu
#             if voucher.min_order_amount > order_total:
#                 raise serializers.ValidationError({"voucher_code": f"Đơn hàng phải có giá trị tối thiểu là {voucher.min_order_amount} để sử dụng voucher này."})

#             discount_amount = voucher.get_discount_amount(order_total)
#             if voucher.discount_type == "percentage" and voucher.max_order_amount > 0 and discount_amount > voucher.max_order_amount:
#                 discount_amount = voucher.max_order_amount

#             # Tăng số lần sử dụng của voucher
#             voucher.times_used = F('times_used') + 1
#             voucher.save(update_fields=['times_used'])

#         # Cập nhật lại tổng tiền và giảm giá sau khi đã tính toán
#         order.discount_applied = discount_amount
#         order.total_amount = order_total - discount_amount
#         order.save(update_fields=['total_amount', 'discount_applied'])

#         return order

# class CartItemSerializer(serializers.ModelSerializer):
#     product = ProductSerializer(read_only=True)
#     product_id = serializers.PrimaryKeyRelatedField(
#         queryset=Product.objects.all(), write_only=True, source='product'
#     )

#     class Meta:
#         model = CartItem
#         fields = ['id', 'product', 'product_id', 'quantity']
#         read_only_fields = ['id', 'product']


# class CartSerializer(serializers.ModelSerializer):
#     items = CartItemSerializer(many=True, read_only=True)

#     class Meta:
#         model = Cart
#         fields = ['id', 'user', 'items']
#         read_only_fields = ['user']



