from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import models
from ckeditor.widgets import CKEditorWidget
from .models import *
from django import forms
from django.utils import timezone
from django.contrib import messages


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
    list_display = ('id','name', 'country')
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



# Sửa lại class ProductAdmin
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'brand', 'rating', 'display_tags', 'category',
        'stock_quantity', 'import_price', 'original_price', 'discounted_price',
        'discount_rate', 'status'
    )

    # Chỉ giữ lại các trường có thể chỉnh sửa được
    list_editable = (
        'name', 'brand', 'stock_quantity', 'import_price',
        'original_price', 'discounted_price', 'status'
    )

    list_filter = ('brand', 'category', 'tags', 'status')
    search_fields = ('name', 'brand__name', 'status')

    # Sử dụng filter_horizontal để chọn tags và gifts
    filter_horizontal = ('tags', 'gifts')

    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }

    fieldsets = (
        (None, {'fields': ('name', 'image', 'brand', 'category')}),
        ('Mô tả', {'fields': ('description',)}),
        ('Thông tin giá và kho', {'fields': ('import_price', 'original_price', 'discounted_price', 'stock_quantity', 'sold_quantity')}),
        # Bỏ tags và gifts khỏi fieldsets để chúng được hiển thị bởi filter_horizontal
        ('Thuộc tính khác', {'fields': ('rating', 'status')}),
        ('Tags và Quà tặng', {'fields': ('tags', 'gifts')}),
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


class BlogAdmin(admin.ModelAdmin):
    """
    Tùy chỉnh giao diện quản trị cho model Blog
    """
    # Các trường hiển thị trên trang danh sách Blog
    list_display = ('title', 'tag', 'post_date', 'views', 'is_active')

    list_filter = ('tag', 'post_date', 'is_active')

    # Thêm thanh tìm kiếm dựa trên các trường
    search_fields = ('title', 'short_description', 'content')
    fieldsets = (
        (None, {
            'fields': ('title', 'short_description', 'content', 'link', 'img_thumbnail')
        }),
        ('Thông tin chi tiết', {
            'fields': ('tag', 'is_active', 'views'),
            'classes': ('collapse',) # Ẩn phần này, có thể mở rộng
        }),
    )

    # Chỉ cho phép chỉnh sửa các trường này trong trang quản trị
    readonly_fields = (
        'post_date',
        'views'
    )


# --- Đăng ký các models với admin_site tùy chỉnh ---
admin_site.register(User, CustomUserAdmin)
admin_site.register(Admin)
# Ẩn model Collaborator cũ để tránh nhầm lẫn
# admin_site.register(Collaborator, CollaboratorAdmin)
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
admin_site.register(Blog, BlogAdmin)

# --- Analytics ---
class AnalyticsSnapshotAdmin(admin.ModelAdmin):
    list_display = ('period', 'period_key', 'total_revenue', 'total_profit', 'created_at')
    list_filter = ('period', 'created_at')
    search_fields = ('period_key',)
    readonly_fields = ('created_at',)

admin_site.register(AnalyticsSnapshot, AnalyticsSnapshotAdmin)


# --- Lucky Number Event Admin ---
class LuckyPrizeInline(admin.TabularInline):
    model = LuckyPrize
    extra = 1
    fields = ('name', 'image', 'value', 'order')


class LuckyEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'start_at', 'end_at', 'is_active', 'lucky_number')
    list_filter = ('is_active',)
    search_fields = ('title',)
    inlines = [LuckyPrizeInline]
    fieldsets = (
        (None, {'fields': ('title', 'description')}),
        ('Thời gian', {'fields': ('start_at', 'end_at', 'is_active')}),
        ('Kết quả', {'fields': ('lucky_number',)}),
    )


class LuckyParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'name', 'zalo_phone', 'email', 'chosen_number', 'submitted_at')
    list_filter = ('event', 'chosen_number')
    search_fields = ('name', 'zalo_phone', 'email', 'address', 'message')
    readonly_fields = ('submitted_at',)
    fieldsets = (
        ('Thông tin cơ bản', {'fields': ('event', 'chosen_number', 'name', 'zalo_phone', 'email', 'address')}),
        ('Thông tin khác', {'fields': ('message', 'submitted_at')}),
    )


class LuckyWinnerAdmin(admin.ModelAdmin):
    list_display = ('event', 'participant', 'get_number', 'prize', 'decided_at')
    readonly_fields = ('decided_at',)

    def get_number(self, obj):
        try:
            return obj.participant.chosen_number
        except Exception:
            return '-'
    get_number.short_description = 'Số may mắn'


admin_site.register(LuckyEvent, LuckyEventAdmin)
admin_site.register(LuckyParticipant, LuckyParticipantAdmin)
admin_site.register(LuckyWinner, LuckyWinnerAdmin)


# --- CTV (Affiliate) Admin ---
class CTVLevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'commission_percent')
    search_fields = ('name',)


class CTVApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'email', 'desired_code', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'phone', 'email', 'desired_code')
    readonly_fields = ('created_at',)


class CTVAdminForm(forms.ModelForm):
    class Meta:
        model = CTV
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hiển thị mật khẩu text đã lưu
        if self.instance and self.instance.pk and self.instance.password_text:
            self.fields['password_text'].help_text = 'Mật khẩu hiện tại (có thể sửa).'
        else:
            self.fields['password_text'].help_text = 'Nhập mật khẩu để tạo/cập nhật tài khoản đăng nhập.'


class CTVAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'full_name', 'phone', 'email', 'level', 'total_revenue', 'is_active', 'joined_at')
    list_filter = ('is_active', 'level')
    search_fields = ('code', 'full_name', 'phone', 'email')
    readonly_fields = ('joined_at',)
    form = CTVAdminForm
    fieldsets = (
        ('Thông tin Cộng tác viên', {'fields': ('code', 'full_name', 'phone', 'email', 'is_active', 'level')}),
        ('Thông tin liên hệ', {'fields': ('address',)}),
        ('Tài khoản nhận hoa hồng', {'fields': ('bank_name', 'bank_number', 'bank_holder')}),
        ('Xác minh danh tính', {'fields': ('cccd_front_url', 'cccd_back_url')}),
        ('Chỉ số kinh doanh', {'fields': ('total_revenue',)}),
        ('Tài khoản đăng nhập', {'fields': ('password_text',)}),
        ('Khác', {'fields': ('joined_at',)}),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Nếu admin nhập mật khẩu, tạo/cập nhật tài khoản User đăng nhập bằng SĐT
        pwd = obj.password_text
        # Lấy mật khẩu cũ để so sánh
        old_password_text = obj.password_text if change else ''
        
        # Chỉ xử lý nếu có mật khẩu mới
        if pwd:
            try:
                # Tìm hoặc tạo User theo số điện thoại
                user = User.objects.filter(phone_number=obj.phone).first()
                if not user:
                    user = User.objects.create_user(
                        phone_number=obj.phone,
                        email=obj.email or None,
                        password=pwd,
                        is_google_user=False,
                        name=obj.full_name,
                        is_active=True,
                    )
                    messages.success(request, f"✅ Đã tạo tài khoản đăng nhập cho CTV {obj.code} bằng SĐT {obj.phone}.")
                else:
                    user.name = user.name or obj.full_name
                    if obj.email and not user.email:
                        user.email = obj.email
                    user.is_active = True
                    user.set_password(pwd)
                    user.save()
                    messages.success(request, f"✅ Đã cập nhật mật khẩu cho CTV {obj.code} (SĐT: {obj.phone}).")
            except Exception as e:
                messages.error(request, f"❌ Không thể tạo/cập nhật tài khoản đăng nhập: {e}")
        else:
            # Kiểm tra xem CTV đã có tài khoản đăng nhập chưa
            try:
                user = User.objects.get(phone_number=obj.phone)
                if user.has_usable_password():
                    messages.info(request, f"ℹ️ CTV {obj.code} đã có tài khoản đăng nhập (SĐT: {obj.phone}).")
                else:
                    messages.warning(request, f"⚠️ CTV {obj.code} chưa có mật khẩu đăng nhập. Nhập mật khẩu để thiết lập.")
            except User.DoesNotExist:
                messages.warning(request, f"⚠️ CTV {obj.code} chưa có tài khoản đăng nhập. Nhập mật khẩu để tạo.")


class CTVWalletAdmin(admin.ModelAdmin):
    list_display = ('ctv', 'balance', 'pending', 'updated_at')
    search_fields = ('ctv__code', 'ctv__full_name', 'ctv__phone')
    readonly_fields = ('updated_at',)


class CTVWithdrawalAdmin(admin.ModelAdmin):
    list_display = ('id', 'ctv', 'amount', 'status', 'requested_at', 'processed_at')
    list_filter = ('status',)
    search_fields = ('ctv__code', 'ctv__full_name', 'ctv__phone')
    readonly_fields = ('requested_at',)


admin_site.register(CTVLevel, CTVLevelAdmin)
admin_site.register(CTVApplication, CTVApplicationAdmin)
admin_site.register(CTV, CTVAdmin)
admin_site.register(CTVWallet, CTVWalletAdmin)
admin_site.register(CTVWithdrawal, CTVWithdrawalAdmin)

# CustomerLead admin
from .models import CustomerLead

class CustomerLeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'address', 'updated_at')
    search_fields = ('name', 'phone', 'email', 'address')
    list_filter = ('updated_at',)
    readonly_fields = ('created_at', 'updated_at')

admin_site.register(CustomerLead, CustomerLeadAdmin)

