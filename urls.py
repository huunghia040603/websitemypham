from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import *

# Tạo router cho API của BuddyApp
r = DefaultRouter()

# Đăng ký các ViewSet với router
r.register(r'users', views.UserViewSet)
r.register(r'collaborators', views.CollaboratorViewSet)
r.register(r'brands', views.BrandViewSet)
r.register(r'category', views.CategoryViewSet)
r.register(r'tags', views.TagViewSet)
r.register(r'gifts', views.GiftViewSet)
r.register(r'albums', views.AlbumViewSet)
r.register(r'images', views.ImageViewSet)
r.register(r'products', views.ProductViewSet)
r.register(r'vouchers', views.VoucherViewSet)
r.register(r'orders', views.OrderViewSet)
r.register(r'order-items', views.OrderItemViewSet)
r.register(r'latest-products', views.LatestProductsViewSet, basename='latest-product')
r.register(r'carts', CartViewSet, basename='cart')

# Cấu hình urlpatterns cho ứng dụng
urlpatterns = [
    # path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('', include(r.urls)),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    # path('auth/', include('rest_framework_social_oauth2.urls')),
    # path('auth/register/', registration_view, name='register'),
    # path('auth/login/', PhoneNumberLoginView.as_view(), name='login'),
    # path('api/auth/google/', GoogleSocialAuthView.as_view(), name='google-auth')
]

