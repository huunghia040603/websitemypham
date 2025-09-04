from rest_framework import viewsets, mixins, status, filters, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from .filters import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import GenericAPIView
from rest_framework import permissions
from rest_framework.decorators import action
import random
import string
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


# --- User ViewSets ---
class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'], url_path='forgot-password', serializer_class=ForgotPasswordSerializer)
    def forgot_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Nếu email của bạn tồn tại trong hệ thống, chúng tôi đã gửi một mã đặt lại mật khẩu."},
                status=status.HTTP_200_OK
            )

        chars = string.ascii_letters + string.digits
        new_password = ''.join(random.choice(chars) for _ in range(8))
        user.set_password(new_password)
        user.save()

        # Tạo nội dung email từ template
        context = {
            'new_password': new_password,
        }
        html_content = render_to_string('emails/forgot_password_email.html', context)
        subject = 'Mã Đặt Lại Mật Khẩu Của Bạn'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        try:
            with get_connection() as connection:
                msg = EmailMessage(
                    subject,
                    html_content,
                    from_email,
                    recipient_list,
                    connection=connection,
                )
                msg.content_subtype = "html"
                msg.send()
        except Exception as e:
            # Ghi log lỗi tại đây để tiện debug
            print(f"Lỗi khi gửi email: {e}")
            pass

        return Response(
            {"detail": "Một mã đặt lại mật khẩu đã được gửi đến email của bạn."},
            status=status.HTTP_200_OK
        )


class CollaboratorViewSet(viewsets.ModelViewSet):
    queryset = Collaborator.objects.all()
    serializer_class = CollaboratorSerializer


# --- Product-related ViewSets ---
class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class GiftViewSet(viewsets.ModelViewSet):
    queryset = Gift.objects.all()
    serializer_class = GiftSerializer


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class ProductViewSet(viewsets.ModelViewSet):
    # Sửa lỗi thiếu dấu phẩy, đồng thời tối ưu: select_related cho FK, prefetch_related cho M2M
    queryset = Product.objects.all().select_related('brand', 'category').prefetch_related('tags', 'gifts')
    serializer_class = ProductSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'brand__name']
    ordering_fields = ['name', 'id']


class LatestProductsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API endpoint to list the 10 latest products.
    """
    queryset = Product.objects.all().order_by('-id')[:10].prefetch_related('tags','category', 'gifts')
    serializer_class = ProductSerializer


# --- Order-related ViewSets ---
class VoucherViewSet(viewsets.ModelViewSet):
    queryset = Voucher.objects.all()
    serializer_class = VoucherSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().select_related('customer', 'voucher').prefetch_related('items__product')
    serializer_class = OrderSerializer


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


# --- View Đăng Ký và Đăng Nhập Xã Hội (Đã sửa lại) ---
class RegistrationView(generics.CreateAPIView):
    """
    Registration endpoint to create a new user.
    """
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Đăng ký thành công',
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class GoogleSocialAuthView(GenericAPIView):
    serializer_class = GoogleSocialAuthSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data
        if not isinstance(user, User):
            return Response({'error': 'Dữ liệu người dùng không hợp lệ.'}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        response_data = {
            'user': UserSerializer(user).data,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }
        return Response(response_data, status=status.HTTP_200_OK)


class PhoneNumberLoginView(APIView):
    """
    API View to handle login requests with phone number and password.
    Returns user info and JWT tokens upon successful login.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PhoneNumberLoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartViewSet(viewsets.GenericViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().prefetch_related('items__product')
        cart_instance = queryset.first()
        if not cart_instance:
            cart_instance = Cart.objects.create(user=request.user)
            serializer = self.get_serializer(cart_instance)
        else:
            serializer = self.get_serializer(cart_instance)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='add-item', serializer_class=CartItemSerializer)
    def add_item_to_cart(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product'].id
        quantity = serializer.validated_data['quantity']

        cart, created = Cart.objects.get_or_create(user=self.request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=product_id,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'], url_path='update-item', serializer_class=CartItemSerializer)
    def update_cart_item_quantity(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = Cart.objects.get(user=self.request.user)
        product_id = serializer.validated_data['product'].id
        quantity = serializer.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.quantity = quantity
            cart_item.save()
            return Response(CartItemSerializer(cart_item).data, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({"detail": "Sản phẩm không có trong giỏ hàng."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['delete'], url_path='remove-item')
    def remove_cart_item(self, request):
        product_id = request.data.get('product_id')

        try:
            cart = Cart.objects.get(user=self.request.user)
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({"detail": "Giỏ hàng hoặc sản phẩm không được tìm thấy."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='item-count')
    def get_cart_item_count(self, request):
        try:
            cart = Cart.objects.get(user=self.request.user)
            total_items = CartItem.objects.filter(cart=cart).count()
            return Response({'item_count': total_items}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({'item_count': 0}, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    View to retrieve and update the profile of the logged-in user.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response({
            "message": "Thông tin cá nhân đã được cập nhật thành công.",
            "user": serializer.data
        })





