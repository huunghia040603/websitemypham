# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from . import views
# from .views import *

# # Tạo router cho API của BuddyApp
# r = DefaultRouter()

# # Đăng ký các ViewSet với router
# r.register(r'users', views.UserViewSet)
# r.register(r'collaborators', views.CollaboratorViewSet)
# r.register(r'brands', views.BrandViewSet)
# r.register(r'category', views.CategoryViewSet)
# r.register(r'tags', views.TagViewSet)
# r.register(r'gifts', views.GiftViewSet)
# r.register(r'products', views.ProductViewSet)
# r.register(r'vouchers', views.VoucherViewSet)
# r.register(r'orders', views.OrderViewSet)
# r.register(r'order-items', views.OrderItemViewSet)
# r.register(r'latest-products', views.LatestProductsViewSet, basename='latest-product')
# r.register(r'carts', CartViewSet, basename='cart')

# # Cấu hình urlpatterns cho ứng dụng
# urlpatterns = [
#     path('', include(r.urls)),
#     path('profile/', UserProfileView.as_view(), name='user-profile'),

#     # URL cho đăng ký và đăng nhập
#     path('auth/register/', RegistrationView.as_view(), name='register'),
#     path('auth/login/', PhoneNumberLoginView.as_view(), name='login'),
#     path('auth/google/', GoogleSocialAuthView.as_view(), name='google-auth'),
#     path('auth/me/', CurrentUserView.as_view(), name='current-user'),
#     path('orders/by-code/<str:order_code>/', OrderByCodeView.as_view(), name='order-by-code'),
# ]


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
r.register(r'admin', views.AdminViewSet, basename='admin')
r.register(r'analytics', views.AnalyticsViewSet, basename='analytics')



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