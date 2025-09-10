
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import *

# Tạo router cho API của BuddyApp
r = DefaultRouter()

# Đăng ký các ViewSet với router
r.register(r'collaborators', views.CollaboratorViewSet)
r.register(r'customer', CustomerViewSet, basename='customer')
r.register(r'brands', views.BrandViewSet)
r.register(r'category', views.CategoryViewSet)
r.register(r'tags', views.TagViewSet)
r.register(r'gifts', views.GiftViewSet)
r.register(r'products', views.ProductViewSet)
r.register(r'vouchers', views.VoucherViewSet)
r.register(r'orders', views.OrderViewSet)
r.register(r'order-items', views.OrderItemViewSet)
r.register(r'latest-products', views.LatestProductsViewSet, basename='latest-product')
r.register(r'carts', CartViewSet, basename='cart')
# Blog API (sửa lỗi: dùng ViewSet duy nhất BlogAPIView)
r.register(r'blog', views.BlogAPIView, basename='blog')
r.register(r'admin', views.AdminViewSet, basename='admin')
r.register(r'analytics', views.AnalyticsViewSet, basename='analytics')
r.register(r'lucky-events', views.LuckyEventViewSet, basename='lucky-event')
r.register(r'lucky-participants', views.LuckyParticipantViewSet, basename='lucky-participant')
r.register(r'lucky-winners', views.LuckyWinnerViewSet, basename='lucky-winner')
r.register(r'ctv-applications', views.CTVApplicationViewSet, basename='ctv-application')
r.register(r'ctv-levels', views.CTVLevelViewSet, basename='ctv-level')
r.register(r'ctvs', views.CTVViewSet, basename='ctv')



# Cấu hình urlpatterns cho ứng dụng
urlpatterns = [
    # Router URLs
    path('', include(r.urls)),

    # Authentication and User URLs
    path('auth/register/', RegistrationView.as_view(), name='register'),
    path('auth/login/', PhoneNumberLoginView.as_view(), name='login'),
    path('auth/google/', GoogleSocialAuthView.as_view(), name='google-auth'),
    path('auth/me/', CurrentUserView.as_view(), name='current-user'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('auth/forgot-password/', UserViewSet.as_view({'post': 'forgot_password'}), name='forgot-password'),

    # Other URLs
    path('orders/by-code/<str:order_code>/', OrderByCodeView.as_view(), name='order-by-code'),
]