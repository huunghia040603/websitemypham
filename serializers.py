
# /home/buddyskincare/BuddySkincare/BuddyApp/serializers.py
from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from .google_social_auth import Google
from django.contrib.auth import authenticate
from django.db import transaction

# --- User Serializers ---

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer to display and update user profile information.
    """
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'phone_number', 'address', 'dob', 'avatar', 'user_type')
        read_only_fields = ('user_type',)


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer to display and edit user profile information.
    """
    class Meta:
        model = User
        fields = [
            'id',
            'phone_number',
            'email',
            'name',
            'address',
            'dob',
            'avatar'
        ]
        read_only_fields = ['id', 'phone_number']

    def validate_email(self, value):
        if value and self.instance and User.objects.exclude(id=self.instance.id).filter(email=value).exists():
            raise serializers.ValidationError("Email này đã được sử dụng. Vui lòng chọn một email khác.")
        return value


class CollaboratorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Collaborator model.
    """
    user = UserSerializer()

    class Meta:
        model = Collaborator
        fields = ('user', 'sales_code')


class PhoneNumberLoginSerializer(serializers.Serializer):
    """
    Serializer to handle login with phone number and password,
    and return user info and JWT tokens.
    """
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)

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

        # Get JWT tokens
        refresh = RefreshToken.for_user(user)
        data['access_token'] = str(refresh.access_token)
        data['refresh_token'] = str(refresh)

        # Add user data to the validated data
        for field in ['name', 'address', 'dob', 'email', 'avatar', 'user_type']:
            data[field] = getattr(user, field, None)

        return data


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
            user = User.objects.get(email=email)
            if not user.name:
                user.name = name
            if not user.avatar:
                user.avatar = avatar
            user.save()
        except User.DoesNotExist:
            with transaction.atomic():
                user = User.objects.create_user(
                    phone_number=None,
                    password=None,
                    email=email,
                    name=name,
                    avatar=avatar,
                    is_active=True
                )
                Customer.objects.create(user_ptr=user, name=name, email=email, avatar=avatar)
                user.is_staff = False
                user.is_superuser = False
                user.save()

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

    class Meta:
        model = User
        fields = ('name', 'phone_number', 'password', 'email', 'avatar')
        extra_kwargs = {
            'phone_number': {'required': False},
            'email': {'required': False},
            'name': {'required': False},
            'avatar': {'required': False}
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
        with transaction.atomic():
            user = User.objects.create_user(
                phone_number=validated_data.get('phone_number', None),
                email=validated_data.get('email', None),
                password=validated_data.get('password', None),
                name=validated_data.get('name', None),
                avatar=validated_data.get('avatar', None)
            )
            Customer.objects.create(
                user_ptr=user,
                name=user.name,
                email=user.email,
                phone_number=user.phone_number,
                avatar=user.avatar
            )
            user.is_staff = False
            user.is_superuser = False
            user.save()
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
        fields = ('id', 'code', 'name', 'description')


class GiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gift
        fields = ('id', 'name', 'description', 'image')


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'image', 'is_thumbnail')


class AlbumSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = ('id', 'name', 'images')


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model after removing ProductVariant.
    """
    brand = BrandSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    gifts = GiftSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'description', 'ingredients', 'volume', 'unit',
            'image', 'brand','tags', 'gifts', 'stock_quantity', 'sold_quantity', 'rating',
            'market_price', 'savings_price', 'import_price', 'original_price',
            'discount_rate', 'discounted_price','status'
        )
        read_only_fields = ('savings_price', 'discount_rate')


# --- Order-related Serializers ---

class VoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        fields = (
            'id', 'code', 'discount_type', 'discount_value', 'is_active',
            'min_order_amount', 'max_order_amount', 'valid_from', 'valid_to',
            'max_uses', 'times_used'
        )


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'quantity', 'price_at_purchase')


class OrderSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    voucher = VoucherSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'customer', 'order_date', 'total_amount', 'collaborator_code',
            'discount_applied', 'items', 'voucher'
        )


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





