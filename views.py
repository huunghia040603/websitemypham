from rest_framework import viewsets, mixins, status, filters, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from .filters import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.generics import GenericAPIView
from rest_framework import permissions
from rest_framework.decorators import action
import random
import string
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

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
            print(f"Lỗi khi gửi email: {e}")
            pass

        return Response(
            {"detail": "Một mã đặt lại mật khẩu đã được gửi đến email của bạn."},
            status=status.HTTP_200_OK
        )


class CollaboratorViewSet(viewsets.ModelViewSet):
    queryset = Collaborator.objects.all()
    serializer_class = CollaboratorSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


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


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('brand', 'category').prefetch_related('tags', 'gifts')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter

    # Thêm các trường tìm kiếm theo tên của brand, category và tags
    search_fields = ['name', 'brand__name', 'category__name', 'tags__name']

    # Thêm các trường sắp xếp
    ordering_fields = ['name', 'id', 'original_price', 'sold_quantity']


class LatestProductsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API endpoint to list the 10 latest products.
    """
    queryset = Product.objects.select_related('brand', 'category').prefetch_related('tags', 'gifts').order_by('-id')[:10]
    serializer_class = ProductSerializer


# --- Order-related ViewSets ---
class VoucherViewSet(viewsets.ModelViewSet):
    queryset = Voucher.objects.all()
    serializer_class = VoucherSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().select_related('customer', 'voucher').prefetch_related('items__product')
    serializer_class = OrderSerializer

    def get_permissions(self):
        """
        Set permissions based on action.
        - allow POST for unauthenticated users (for non-logged-in orders)
        - allow GET for unauthenticated users (for admin access)
        - allow PUT, PATCH, DELETE for unauthenticated users (for admin updates)
        """
        # Cho phép tất cả actions cho admin Flask app
        self.permission_classes = [AllowAny]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """
        Tạo đơn hàng mới với kiểm tra trùng lặp và đảm bảo trạng thái mặc định
        """
        from django.utils import timezone
        from datetime import timedelta
        from django.db import transaction

        # Kiểm tra trùng lặp dựa trên thông tin khách hàng và thời gian
        customer_name = request.data.get('customer_name')
        phone_number = request.data.get('phone_number')

        if customer_name and phone_number:
            # Kiểm tra xem có đơn hàng nào được tạo trong vòng 10 giây với cùng thông tin không
            recent_orders = Order.objects.filter(
                customer_name=customer_name,
                phone_number=phone_number,
                order_date__gte=timezone.now() - timedelta(seconds=10)
            )

            if recent_orders.exists():
                return Response(
                    {'detail': 'Đơn hàng đã được tạo gần đây. Vui lòng đợi một chút.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Đảm bảo trạng thái mặc định
        request.data['status'] = 'pending'
        request.data['is_confirmed'] = False

        # Sử dụng transaction để đảm bảo atomicity
        with transaction.atomic():
            return super().create(request, *args, **kwargs)

    def get_queryset(self):
        """
        Chỉ cho phép người dùng xem đơn hàng của chính họ.
        Cho phép admin Flask app xem tất cả đơn hàng.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:
                # Admin Django có thể xem tất cả đơn hàng
                return Order.objects.all().select_related('customer', 'voucher').prefetch_related('items__product')
            else:
                # User thường chỉ xem đơn hàng của chính họ
                return Order.objects.filter(customer=user).select_related('customer', 'voucher').prefetch_related('items__product')
        else:
            # Cho phép Flask admin app truy cập tất cả đơn hàng khi không có authentication
            return Order.objects.all().select_related('customer', 'voucher').prefetch_related('items__product')


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemReadSerializer


class AnalyticsViewSet(viewsets.GenericViewSet):
    queryset = AnalyticsSnapshot.objects.all()
    serializer_class = AnalyticsSnapshotSerializer
    permission_classes = [AllowAny]

    def list(self, request):
        period = request.query_params.get('period', 'month')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Get all unique periods from orders
        from .models import Order
        from datetime import date, timedelta
        from django.db.models import Min, Max

        # Get all confirmed orders
        orders = Order.objects.filter(is_confirmed=True).exclude(status='cancelled')
        
        # Apply custom date range if provided
        if start_date and end_date:
            try:
                start_date_obj = date.fromisoformat(start_date)
                end_date_obj = date.fromisoformat(end_date)
                orders = orders.filter(order_date__date__gte=start_date_obj, order_date__date__lte=end_date_obj)
                print(f"🔍 Custom date range: {start_date_obj} to {end_date_obj}")
                print(f"📊 Orders found: {orders.count()}")
            except ValueError:
                return Response({'error': 'Invalid date format'}, status=400)

        if not orders.exists():
            return Response([])

        # For custom date range, create a single period
        if start_date and end_date:
            periods_to_compute = [{
                'period': 'custom',
                'start': start_date_obj,
                'end': end_date_obj,
                'key': f"{start_date_obj.strftime('%Y-%m-%d')} to {end_date_obj.strftime('%Y-%m-%d')}"
            }]
            # For custom range, don't delete existing snapshots, just compute new one
            period_to_delete = 'custom'
        else:
            # Get date range from orders
            date_range = orders.aggregate(
                min_date=Min('order_date__date'),
                max_date=Max('order_date__date')
            )

            min_date = date_range['min_date']
            max_date = date_range['max_date']

            if not min_date or not max_date:
                return Response([])

            # Generate periods based on actual order dates, not date range
            periods_to_compute = []

            # Get unique dates from orders
            order_dates = orders.values_list('order_date__date', flat=True).distinct().order_by('order_date__date')

            if period == 'day':
                # Create one period for each day that has orders
                for order_date in order_dates:
                    periods_to_compute.append({
                        'period': 'day',
                        'start': order_date,
                        'end': order_date,
                        'key': order_date.strftime('%Y-%m-%d')
                    })

            elif period == 'week':
                # Group orders by week
                week_groups = {}
                for order_date in order_dates:
                    # Get start of week (Monday)
                    week_start = order_date - timedelta(days=order_date.weekday())
                    week_key = f"{week_start.year}-W{week_start.strftime('%W')}"
                    if week_key not in week_groups:
                        week_groups[week_key] = {
                            'start': week_start,
                            'end': week_start + timedelta(days=6)
                        }

                for week_key, week_data in week_groups.items():
                    periods_to_compute.append({
                        'period': 'week',
                        'start': week_data['start'],
                        'end': week_data['end'],
                        'key': week_key
                    })

            elif period == 'month':
                # Group orders by month
                month_groups = {}
                for order_date in order_dates:
                    month_key = order_date.strftime('%Y-%m')
                    if month_key not in month_groups:
                        month_start = order_date.replace(day=1)
                        if order_date.month == 12:
                            month_end = order_date.replace(year=order_date.year + 1, month=1, day=1) - timedelta(days=1)
                        else:
                            month_end = order_date.replace(month=order_date.month + 1, day=1) - timedelta(days=1)
                        month_groups[month_key] = {
                            'start': month_start,
                            'end': month_end
                        }

                for month_key, month_data in month_groups.items():
                    periods_to_compute.append({
                        'period': 'month',
                        'start': month_data['start'],
                        'end': month_data['end'],
                        'key': month_key
                    })

            elif period == 'year':
                # Group orders by year
                year_groups = {}
                for order_date in order_dates:
                    year_key = str(order_date.year)
                    if year_key not in year_groups:
                        year_groups[year_key] = {
                            'start': date(order_date.year, 1, 1),
                            'end': date(order_date.year, 12, 31)
                        }

                for year_key, year_data in year_groups.items():
                    periods_to_compute.append({
                        'period': 'year',
                        'start': year_data['start'],
                        'end': year_data['end'],
                        'key': year_key
                    })
            
            # For regular periods, delete existing snapshots
            period_to_delete = period

        # Delete all existing snapshots for this period type to avoid confusion
        AnalyticsSnapshot.objects.filter(period=period_to_delete).delete()

        # Compute snapshots for all periods
        snapshots = []
        for period_data in periods_to_compute:
            # Create new snapshot
            serializer = ComputeAnalyticsSerializer(data=period_data)
            if serializer.is_valid():
                snapshot = serializer.save()
                snapshots.append(snapshot)

        # Return snapshots sorted by period_key descending (newest first)
        snapshots.sort(key=lambda x: x.period_key, reverse=True)
        data = AnalyticsSnapshotSerializer(snapshots, many=True).data
        
        # Debug: Log the snapshots being returned
        print(f"📊 Returning {len(data)} snapshots for period {period}")
        for snap in data:
            print(f"  - {snap['period']} {snap['period_key']}: {snap['total_revenue']}đ")
        
        return Response(data)

    @action(detail=False, methods=['post'], url_path='compute')
    def compute(self, request):
        serializer = ComputeAnalyticsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        snapshot = serializer.save()
        return Response(AnalyticsSnapshotSerializer(snapshot).data, status=status.HTTP_201_CREATED)

class OrderByCodeView(APIView):
    """
    API để tra cứu đơn hàng bằng mã đơn hàng.
    """
    permission_classes = [AllowAny] # Cho phép bất kỳ ai cũng có thể truy cập

    def get(self, request, order_code, format=None):
        """
        Lấy thông tin đơn hàng dựa trên mã đơn hàng.
        """
        try:
            order = Order.objects.get(order_code=order_code)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Mã đơn hàng không tồn tại hoặc không hợp lệ."},
                status=status.HTTP_404_NOT_FOUND
            )


# --- View Đăng Ký và Đăng Nhập Xã Hội ---
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

        # Corrected line: Get the user object directly from the validated data
        # of the 'auth_token' field.
        user = serializer.validated_data['auth_token']

        # Now 'user' is the correct User model instance.
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
            return Response(serializer.to_representation(serializer.validated_data), status=status.HTTP_200_OK)
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
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({"detail": "Giỏ hàng hoặc sản phẩm không được tìm thấy."}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)

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
    View để lấy và cập nhật hồ sơ của người dùng đã đăng nhập.
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



# from rest_framework import viewsets, mixins, status, filters, generics
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from django_filters.rest_framework import DjangoFilterBackend
# from .models import *
# from .serializers import *
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from .filters import *
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.generics import GenericAPIView
# from rest_framework import permissions
# from rest_framework.decorators import action
# import random
# import string
# from django.template.loader import render_to_string
# from django.core.mail import EmailMessage, get_connection
# from django.conf import settings
# from django.contrib.auth import get_user_model
# from rest_framework_simplejwt.tokens import RefreshToken

# User = get_user_model()


# class CurrentUserView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         serializer = UserSerializer(request.user)
#         return Response(serializer.data)


# # --- User ViewSets ---
# class UserViewSet(viewsets.GenericViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

#     @action(detail=False, methods=['post'], url_path='forgot-password', serializer_class=ForgotPasswordSerializer)
#     def forgot_password(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         email = serializer.validated_data['email']

#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response(
#                 {"detail": "Nếu email của bạn tồn tại trong hệ thống, chúng tôi đã gửi một mã đặt lại mật khẩu."},
#                 status=status.HTTP_200_OK
#             )

#         chars = string.ascii_letters + string.digits
#         new_password = ''.join(random.choice(chars) for _ in range(8))
#         user.set_password(new_password)
#         user.save()

#         context = {
#             'new_password': new_password,
#         }
#         html_content = render_to_string('emails/forgot_password_email.html', context)
#         subject = 'Mã Đặt Lại Mật Khẩu Của Bạn'
#         from_email = settings.DEFAULT_FROM_EMAIL
#         recipient_list = [email]

#         try:
#             with get_connection() as connection:
#                 msg = EmailMessage(
#                     subject,
#                     html_content,
#                     from_email,
#                     recipient_list,
#                     connection=connection,
#                 )
#                 msg.content_subtype = "html"
#                 msg.send()
#         except Exception as e:
#             print(f"Lỗi khi gửi email: {e}")
#             pass

#         return Response(
#             {"detail": "Một mã đặt lại mật khẩu đã được gửi đến email của bạn."},
#             status=status.HTTP_200_OK
#         )


# class CollaboratorViewSet(viewsets.ModelViewSet):
#     queryset = Collaborator.objects.all()
#     serializer_class = CollaboratorSerializer


# # --- Product-related ViewSets ---
# class BrandViewSet(viewsets.ModelViewSet):
#     queryset = Brand.objects.all()
#     serializer_class = BrandSerializer


# class CategoryViewSet(viewsets.ModelViewSet):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer


# class TagViewSet(viewsets.ModelViewSet):
#     queryset = Tag.objects.all()
#     serializer_class = TagSerializer


# class GiftViewSet(viewsets.ModelViewSet):
#     queryset = Gift.objects.all()
#     serializer_class = GiftSerializer


# class ProductViewSet(viewsets.ModelViewSet):
#     queryset = Product.objects.select_related('brand', 'category').prefetch_related('tags', 'gifts')
#     serializer_class = ProductSerializer
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_class = ProductFilter
#     search_fields = ['name', 'brand__name']
#     ordering_fields = ['name', 'id']


# class LatestProductsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     """
#     API endpoint to list the 10 latest products.
#     """
#     queryset = Product.objects.select_related('brand', 'category').prefetch_related('tags', 'gifts').order_by('-id')[:10]
#     serializer_class = ProductSerializer


# # --- Order-related ViewSets ---
# class VoucherViewSet(viewsets.ModelViewSet):
#     queryset = Voucher.objects.all()
#     serializer_class = VoucherSerializer


# class OrderViewSet(viewsets.ModelViewSet):
#     queryset = Order.objects.all().select_related('customer', 'voucher').prefetch_related('items__product')
#     serializer_class = OrderSerializer

#     def get_permissions(self):
#         """
#         Set permissions based on action.
#         - allow POST for unauthenticated users (for non-logged-in orders)
#         - allow GET, PUT, DELETE for authenticated users
#         """
#         if self.action == 'create':
#             # Cho phép mọi người tạo đơn hàng (kể cả khách không đăng nhập)
#             self.permission_classes = [AllowAny]
#         else:
#             # Các hành động khác yêu cầu đăng nhập (ví dụ: xem lịch sử đơn hàng)
#             self.permission_classes = [IsAuthenticated]
#         return super().get_permissions()

#     def get_queryset(self):
#         """
#         Chỉ cho phép người dùng xem đơn hàng của chính họ.
#         """
#         user = self.request.user
#         if user.is_authenticated:
#             return Order.objects.filter(customer=user).select_related('customer', 'voucher').prefetch_related('items__product')
#         # Admin có thể xem tất cả đơn hàng
#         elif user.is_staff:
#             return Order.objects.all().select_related('customer', 'voucher').prefetch_related('items__product')
#         return Order.objects.none() # Trả về queryset rỗng cho người dùng không đăng nhập


# class OrderItemViewSet(viewsets.ModelViewSet):
#     queryset = OrderItem.objects.all()
#     serializer_class = OrderItemReadSerializer


# class OrderByCodeView(APIView):
#     """
#     API để tra cứu đơn hàng bằng mã đơn hàng.
#     """
#     permission_classes = [AllowAny] # Cho phép bất kỳ ai cũng có thể truy cập

#     def get(self, request, order_code, format=None):
#         """
#         Lấy thông tin đơn hàng dựa trên mã đơn hàng.
#         """
#         try:
#             order = Order.objects.get(order_code=order_code)
#             serializer = OrderSerializer(order)
#             return Response(serializer.data)
#         except Order.DoesNotExist:
#             return Response(
#                 {"detail": "Mã đơn hàng không tồn tại hoặc không hợp lệ."},
#                 status=status.HTTP_404_NOT_FOUND
#             )


# # --- View Đăng Ký và Đăng Nhập Xã Hội ---
# class RegistrationView(generics.CreateAPIView):
#     """
#     Registration endpoint to create a new user.
#     """
#     serializer_class = RegistrationSerializer
#     permission_classes = [AllowAny]

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         refresh = RefreshToken.for_user(user)
#         return Response({
#             'message': 'Đăng ký thành công',
#             'access_token': str(refresh.access_token),
#             'refresh_token': str(refresh),
#             'user': UserSerializer(user).data
#         }, status=status.HTTP_201_CREATED)


# class GoogleSocialAuthView(GenericAPIView):
#     serializer_class = GoogleSocialAuthSerializer
#     permission_classes = (AllowAny,)

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         # Corrected line: Get the user object directly from the validated data
#         # of the 'auth_token' field.
#         user = serializer.validated_data['auth_token']

#         # Now 'user' is the correct User model instance.
#         refresh = RefreshToken.for_user(user)
#         response_data = {
#             'user': UserSerializer(user).data,
#             'access_token': str(refresh.access_token),
#             'refresh_token': str(refresh),
#         }
#         return Response(response_data, status=status.HTTP_200_OK)


# class PhoneNumberLoginView(APIView):
#     """
#     API View to handle login requests with phone number and password.
#     Returns user info and JWT tokens upon successful login.
#     """
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         serializer = PhoneNumberLoginSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid():
#             return Response(serializer.to_representation(serializer.validated_data), status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class CartViewSet(viewsets.GenericViewSet):
#     queryset = Cart.objects.all()
#     serializer_class = CartSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Cart.objects.filter(user=self.request.user)

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset().prefetch_related('items__product')
#         cart_instance = queryset.first()
#         if not cart_instance:
#             cart_instance = Cart.objects.create(user=request.user)
#             serializer = self.get_serializer(cart_instance)
#         else:
#             serializer = self.get_serializer(cart_instance)
#         return Response(serializer.data)

#     @action(detail=False, methods=['post'], url_path='add-item', serializer_class=CartItemSerializer)
#     def add_item_to_cart(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         product_id = serializer.validated_data['product'].id
#         quantity = serializer.validated_data['quantity']

#         cart, created = Cart.objects.get_or_create(user=self.request.user)

#         cart_item, created = CartItem.objects.get_or_create(
#             cart=cart,
#             product_id=product_id,
#             defaults={'quantity': quantity}
#         )
#         if not created:
#             cart_item.quantity += quantity
#             cart_item.save()

#         return Response(CartItemSerializer(cart_item).data, status=status.HTTP_200_OK)

#     @action(detail=False, methods=['put'], url_path='update-item', serializer_class=CartItemSerializer)
#     def update_cart_item_quantity(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         cart = Cart.objects.get(user=self.request.user)
#         product_id = serializer.validated_data['product'].id
#         quantity = serializer.validated_data['quantity']

#         try:
#             cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
#             cart_item.quantity = quantity
#             cart_item.save()
#             return Response(CartItemSerializer(cart_item).data, status=status.HTTP_200_OK)
#         except CartItem.DoesNotExist:
#             return Response({"detail": "Sản phẩm không có trong giỏ hàng."}, status=status.HTTP_404_NOT_FOUND)

#     @action(detail=False, methods=['delete'], url_path='remove-item')
#     def remove_cart_item(self, request):
#         product_id = request.data.get('product_id')

#         try:
#             cart = Cart.objects.get(user=self.request.user)
#             cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
#             cart_item.delete()
#         except (Cart.DoesNotExist, CartItem.DoesNotExist):
#             return Response({"detail": "Giỏ hàng hoặc sản phẩm không được tìm thấy."}, status=status.HTTP_404_NOT_FOUND)

#         return Response(status=status.HTTP_204_NO_CONTENT)

#     @action(detail=False, methods=['get'], url_path='item-count')
#     def get_cart_item_count(self, request):
#         try:
#             cart = Cart.objects.get(user=self.request.user)
#             total_items = CartItem.objects.filter(cart=cart).count()
#             return Response({'item_count': total_items}, status=status.HTTP_200_OK)
#         except Cart.DoesNotExist:
#             return Response({'item_count': 0}, status=status.HTTP_200_OK)


# class UserProfileView(generics.RetrieveUpdateAPIView):
#     """
#     View to retrieve and update the profile of the logged-in user.
#     """
#     serializer_class = UserProfileSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_object(self):
#         return self.request.user

#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)

#         if getattr(instance, '_prefetched_objects_cache', None):
#             instance._prefetched_objects_cache = {}

#         return Response({
#             "message": "Thông tin cá nhân đã được cập nhật thành công.",
#             "user": serializer.data
#         })


# --- Admin ViewSet ---
class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'phone_number']