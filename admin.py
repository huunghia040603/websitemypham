from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import models
from ckeditor.widgets import CKEditorWidget
from .models import *


# Tạo một trang admin tùy chỉnh
class MyAdminSite(admin.AdminSite):
    site_header = "Hệ thống quản lý Buddy Skincare"
    site_title = "Buddy Skincare Admin Portal"
    index_title = "Chào mừng đến với trang quản trị"

admin_site = MyAdminSite(name='myadmin')

# --- User Admin ---
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('name', 'email', 'phone_number', 'is_staff', 'is_active', 'date_joined', 'avatar')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('name', 'email', 'phone_number')
    filter_horizontal = ('groups', 'user_permissions',)

    fieldsets = (
        (None, {'fields': ('email', 'phone_number', 'password')}),
        ('Thông tin cá nhân', {'fields': ('name', 'dob', 'address', 'avatar')}),
        ('Phân quyền', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Ngày quan trọng', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {'fields': ('email', 'phone_number', 'password', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    ordering = ('email',)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'points', 'level')
    search_fields = ('name', 'email', 'phone_number')
    list_filter = ('level',)
    fieldsets = (
        ('Thông tin cơ bản', {'fields': ('name', 'email', 'phone_number', 'address', 'dob', 'avatar')}),
        ('Điểm và Cấp độ', {'fields': ('points', 'level')}),
        ('Ngày quan trọng', {'fields': ('date_joined', 'last_login')}),
    )
    readonly_fields = ('points', 'level', 'date_joined', 'last_login')


class CollaboratorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'sales_code', 'points', 'level')
    search_fields = ('name', 'email', 'phone_number', 'sales_code')
    list_filter = ('level',)
    fieldsets = (
        ('Thông tin cơ bản', {'fields': ('name', 'email', 'phone_number', 'address', 'dob', 'avatar')}),
        ('Mã CTV', {'fields': ('sales_code',)}),
        ('Điểm và Cấp độ', {'fields': ('points', 'level')}),
        ('Ngày quan trọng', {'fields': ('date_joined', 'last_login')}),
    )
    readonly_fields = ('points', 'level', 'date_joined', 'last_login')


# --- Product-related Admin ---
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'status', 'start_date', 'end_date', 'discounted_price_reduction')
    search_fields = ('name', 'code')
    list_filter = ('status', 'start_date', 'end_date')

    def save_model(self, request, obj, form, change):
        # Tự động cập nhật trạng thái tag khi lưu
        now = timezone.now()
        if obj.start_date <= now and obj.end_date >= now:
            obj.status = 'active'
        elif obj.start_date > now:
            obj.status = 'upcoming'
        else:
            obj.status = 'expired'
        super().save_model(request, obj, form, change)


class GiftAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'brand', 'rating', 'display_tags', 'category', 'stock_quantity',
        'original_price', 'discounted_price', 'discount_rate', 'status'
    )
    list_filter = ('brand', 'category', 'tags', 'status')
    search_fields = ('name', 'brand__name', 'status')
    filter_horizontal = ('tags', 'gifts')
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }
    fieldsets = (
        (None, {'fields': ('name', 'image', 'brand', 'category')}),
        ('Mô tả', {'fields': ('description',)}),
        ('Thông tin giá và kho', {'fields': ('import_price', 'original_price', 'discounted_price', 'stock_quantity', 'sold_quantity')}),
        ('Thuộc tính khác', {'fields': ('tags', 'gifts', 'rating', 'status')}),
    )
    readonly_fields = ('discount_rate', 'savings_price')

    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    display_tags.short_description = "Tags"


# --- Order-related Admin ---
class VoucherAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'is_active', 'valid_from', 'valid_to', 'times_used')
    list_filter = ('discount_type', 'is_active')
    search_fields = ('code',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    raw_id_fields = ('product',)


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('id','order_code', 'customer_name', 'phone_number', 'order_date', 'total_amount', 'shipping_fee', 'collaborator_code', 'voucher')
    list_filter = ('order_date', 'status', 'payment_method', 'is_confirmed')
    search_fields = ('customer_name', 'phone_number', 'collaborator_code', 'order_code')
    readonly_fields = ('total_amount', 'discount_applied', 'shipping_fee', 'order_date')
    fieldsets = (
        (None, {'fields': ('order_code', 'customer', 'status', 'is_confirmed')}),
        ('Thông tin khách hàng', {'fields': ('customer_name', 'phone_number', 'zalo_phone_number', 'email')}),
        ('Địa chỉ giao hàng', {'fields': ('street', 'ward', 'district', 'province')}),
        ('Thanh toán và Khuyến mãi', {'fields': ('payment_method', 'bank_transfer_image', 'notes', 'voucher', 'collaborator_code')}),
        ('Chi tiết đơn hàng', {'fields': ('total_amount', 'shipping_fee', 'discount_applied')}),
    )

    def customer_name(self, obj):
        return obj.customer_name

    def phone_number(self, obj):
        return obj.phone_number

    customer_name.short_description = 'Tên Khách Hàng'
    phone_number.short_description = 'Số điện thoại'


# --- Đăng ký các models với admin_site tùy chỉnh ---
admin_site.register(User, CustomUserAdmin)
admin_site.register(Admin)
admin_site.register(Collaborator, CollaboratorAdmin)
admin_site.register(Staff)
admin_site.register(Customer, CustomerAdmin)
admin_site.register(Brand, BrandAdmin)
admin_site.register(Category)
admin_site.register(Tag, TagAdmin)
admin_site.register(Gift, GiftAdmin)
admin_site.register(Product, ProductAdmin)
admin_site.register(Voucher, VoucherAdmin)
admin_site.register(Order, OrderAdmin)
admin_site.register(OrderItem)




# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.db import models
# from ckeditor.widgets import CKEditorWidget
# from .models import *


# # Tạo một trang admin tùy chỉnh
# class MyAdminSite(admin.AdminSite):
#     site_header = "Hệ thống quản lý Buddy Skincare"
#     site_title = "Buddy Skincare Admin Portal"
#     index_title = "Chào mừng đến với trang quản trị"

# admin_site = MyAdminSite(name='myadmin')

# # --- User Admin ---
# class CustomUserAdmin(BaseUserAdmin):
#     list_display = ('name', 'email', 'phone_number', 'is_staff', 'is_active', 'date_joined', 'avatar')
#     list_filter = ('is_staff', 'is_active')
#     search_fields = ('name', 'email', 'phone_number')
#     filter_horizontal = ('groups', 'user_permissions',)

#     fieldsets = (
#         (None, {'fields': ('email', 'phone_number', 'password')}),
#         ('Thông tin cá nhân', {'fields': ('name', 'dob', 'address', 'avatar')}),
#         ('Phân quyền', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#         ('Ngày quan trọng', {'fields': ('last_login', 'date_joined')}),
#     )

#     add_fieldsets = (
#         (None, {'fields': ('email', 'phone_number', 'password', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#     )

#     ordering = ('email',)

# # --- Product-related Admin ---
# class BrandAdmin(admin.ModelAdmin):
#     list_display = ('name', 'country')
#     search_fields = ('name',)



# class TagAdmin(admin.ModelAdmin):
#     list_display = ('code', 'name', 'status', 'start_date', 'end_date', 'discounted_price_reduction')
#     search_fields = ('name', 'code')
#     list_filter = ('status', 'start_date', 'end_date')


#     def save_model(self, request, obj, form, change):
#         # Tự động cập nhật trạng thái tag khi lưu
#         now = timezone.now()
#         if obj.start_date <= now and obj.end_date >= now:
#             obj.status = 'active'
#         elif obj.start_date > now:
#             obj.status = 'upcoming'
#         else:
#             obj.status = 'expired'
#         super().save_model(request, obj, form, change)

# class GiftAdmin(admin.ModelAdmin):
#     list_display = ('name',)
#     search_fields = ('name',)



# class ProductAdmin(admin.ModelAdmin):
#     list_display = (
#         'id', 'name', 'brand', 'rating', 'display_tags', 'category', 'stock_quantity',
#         'original_price', 'discounted_price', 'discount_rate', 'status'
#     )
#     list_filter = ('brand', 'category', 'tags', 'status')
#     search_fields = ('name', 'brand__name', 'status')
#     filter_horizontal = ('tags', 'gifts')
#     formfield_overrides = {
#         models.TextField: {'widget': CKEditorWidget},
#     }
#     fieldsets = (
#         (None, {'fields': ('name', 'image', 'brand', 'category')}),
#         ('Mô tả', {'fields': ('description',)}),
#         ('Thông tin giá và kho', {'fields': ('import_price', 'original_price', 'discounted_price', 'stock_quantity', 'sold_quantity')}),
#         ('Thuộc tính khác', {'fields': ('tags', 'gifts', 'rating', 'status')}),
#     )
#     readonly_fields = ('discount_rate', 'savings_price')

#     def display_tags(self, obj):
#         return ", ".join([tag.name for tag in obj.tags.all()])

#     display_tags.short_description = "Tags"

# # --- Order-related Admin ---
# class VoucherAdmin(admin.ModelAdmin):
#     list_display = ('code', 'discount_type', 'discount_value', 'is_active', 'valid_from', 'valid_to', 'times_used')
#     list_filter = ('discount_type', 'is_active')
#     search_fields = ('code',)

# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     extra = 1
#     # Để hiển thị sản phẩm, bạn có thể thêm product vào list_display
#     raw_id_fields = ('product',) # Sử dụng raw_id_fields để chọn sản phẩm dễ dàng hơn nếu có nhiều sản phẩm

# class OrderAdmin(admin.ModelAdmin):
#     inlines = [OrderItemInline]
#     list_display = ('id', 'customer', 'order_date', 'total_amount', 'collaborator_code', 'voucher')
#     list_filter = ('order_date', 'customer')
#     search_fields = ('customer__email', 'collaborator_code', 'voucher__code')
#     readonly_fields = ('total_amount',)

# # --- Đăng ký các models với admin_site tùy chỉnh ---
# admin_site.register(User, CustomUserAdmin)
# admin_site.register(Admin)
# admin_site.register(Collaborator)
# admin_site.register(Staff)
# admin_site.register(Customer)
# admin_site.register(Brand, BrandAdmin)
# admin_site.register(Category)
# admin_site.register(Tag, TagAdmin)
# admin_site.register(Gift, GiftAdmin)

# admin_site.register(Product, ProductAdmin)
# admin_site.register(Voucher, VoucherAdmin)
# admin_site.register(Order, OrderAdmin)
# admin_site.register(OrderItem)




