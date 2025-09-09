# Cập nhật file urls.py - thêm dòng này vào phần đăng ký ViewSet

# Thêm vào phần đăng ký ViewSet với router:
r.register(r'admin', views.AdminViewSet, basename='admin')

# Thêm vào urlpatterns (nếu cần):
# path('admin/create/', AdminCreateView.as_view(), name='admin-create'),
 
 
 
 