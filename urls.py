
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import *
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.contrib import admin

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
r.register(r'admin-products', views.ProductViewSet, basename='admin-product')
r.register(r'vouchers', views.VoucherViewSet)
r.register(r'orders', views.OrderViewSet)
r.register(r'order-items', views.OrderItemViewSet)
r.register(r'latest-products', views.LatestProductsViewSet, basename='latest-product')
r.register(r'carts', CartViewSet, basename='cart')
# Blog API (sửa lỗi: dùng ViewSet duy nhất BlogAPIView)
r.register(r'blog', views.BlogAPIView, basename='blog')
r.register(r'pythonanywhere/admin', views.AdminViewSet, basename='admin')
r.register(r'analytics', views.AnalyticsViewSet, basename='analytics')
r.register(r'lucky-events', views.LuckyEventViewSet, basename='lucky-event')
r.register(r'lucky-participants', views.LuckyParticipantViewSet, basename='lucky-participant')
r.register(r'lucky-winners', views.LuckyWinnerViewSet, basename='lucky-winner')
r.register(r'ctv-applications', views.CTVApplicationViewSet, basename='ctv-application')
r.register(r'ctv-levels', views.CTVLevelViewSet, basename='ctv-level')
r.register(r'ctvs', views.CTVViewSet, basename='ctv')
r.register(r'ctv-withdrawals', views.CTVWithdrawalViewSet, basename='ctv-withdrawal')
r.register(r'customer-leads', views.CustomerLeadViewSet, basename='customer-lead')
r.register(r'users', views.UserViewSet, basename='user')
r.register(r'marketing-resources', views.MarketingResourceViewSet, basename='marketing-resource')


# Cấu hình urlpatterns cho ứng dụng
urlpatterns = [
    # Django Admin with custom path (must be before router)
    path('pythonanywhere/admin/', admin.site.urls),
    
    # Router URLs
    path('', include(r.urls)),

    # Authentication and User URLs
    path('auth/register/', RegistrationView.as_view(), name='register'),
    # path('auth/login/', PhoneNumberLoginView.as_view(), name='login'),
    path('auth/google/', GoogleSocialAuthView.as_view(), name='google-auth'),
    path('auth/me/', CurrentUserView.as_view(), name='current-user'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    # path('auth/forgot-password/', UserViewSet.as_view({'post': 'forgot_password'}), name='forgot-password'),
    path('api/user_info/', UserInfoAPIView.as_view(), name='user-info'),
    # Other URLs
    path('orders/by-code/<str:order_code>/', OrderByCodeView.as_view(), name='order-by-code'),
    path('api/product-stock/<int:product_id>/', views.product_stock, name='product-stock'),
    path('api/orders/auto-complete/', views.auto_complete_orders, name='auto-complete-orders'),
    path('api/send-new-order-notification/', views.send_new_order_notification, name='send-new-order-notification'),
    path('api/orders/<int:order_id>/invoice/email/', views.send_invoice_email, name='send-invoice-email'),
    path('api/upload-bank-transfer/', views.upload_bank_transfer, name='upload-bank-transfer'),
    path('api/upload-marketing-resource/', views.upload_marketing_resource, name='upload-marketing-resource'),
    path('api/upload-marketing-resources-bulk/', views.upload_marketing_resources_bulk, name='upload-marketing-resources-bulk'),
    path('upload-cccd/', views.upload_cccd_image, name='upload-cccd'),
    path('ctvs/<int:ctv_id>/send-welcome-email/', views.send_ctv_welcome_email, name='send-ctv-welcome-email'),
    path('login/', LoginView.as_view(), name='login'),
    # CTV Pages
    path('ctv/login/', views.ctv_login_page, name='ctv-login-page'),
    path('ctv/dashboard/', views.ctv_dashboard_page, name='ctv-dashboard-page'),
    path('ctv/wallet/', views.ctv_wallet_page, name='ctv-wallet-page'),
    path('ctv/orders/', views.ctv_orders_page, name='ctv-orders-page'),
    path('ctv/profile/', views.ctv_profile_page, name='ctv-profile-page'),
    path('ctv/place-order/', views.ctv_place_order_page, name='ctv-place-order-page'),
    path('ctv/resources/', views.ctv_resources_page, name='ctv-resources-page'),

    # Admin Pages
    path('admin/resources/', views.admin_resources_page, name='admin-resources-page'),

    # Product Images API (không bị pagination)
    path('product-images/', views.ProductImagesAPIView.as_view(), name='product-images'),
    
    # Download Image API
    path('download-image/', views.download_image, name='download-image'),
    # Test endpoint for debugging
    path('test-download/', views.test_download, name='test-download'),
    
    # Bank transfer image upload
    path('upload-bank-transfer/', views.upload_bank_transfer, name='upload-bank-transfer'),
    
    # API Documentation
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('swagger.json', SpectacularAPIView.as_view(), name='schema'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]