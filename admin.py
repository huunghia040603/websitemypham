from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import models
from ckeditor.widgets import CKEditorWidget
from .models import *
from django import forms
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q


# Tạo một trang admin tùy chỉnh
class MyAdminSite(admin.AdminSite):
    site_header = "Hệ thống quản lý Buddy Skincare"
    site_title = "Buddy Skincare Admin Portal"
    index_title = "Chào mừng đến với trang quản trị"

admin_site = MyAdminSite(name='myadmin')

# Custom filter for image count
class ImageCountFilter(admin.SimpleListFilter):
    title = 'Số lượng ảnh'
    parameter_name = 'image_count'

    def lookups(self, request, model_admin):
        return (
            ('0', '❌ Không có ảnh'),
            ('1', '🖼️ 1 ảnh'),
            ('2', '🖼️ 2 ảnh'),
            ('3', '🖼️ 3 ảnh'),
            ('4', '🖼️ 4 ảnh'),
        )

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(
                Q(image__isnull=True) | Q(image=''),
                Q(image_2__isnull=True) | Q(image_2=''),
                Q(image_3__isnull=True) | Q(image_3=''),
                Q(image_4__isnull=True) | Q(image_4='')
            )
        elif self.value() == '1':
            return queryset.filter(
                ~Q(image__isnull=True) & ~Q(image=''),
                Q(image_2__isnull=True) | Q(image_2=''),
                Q(image_3__isnull=True) | Q(image_3=''),
                Q(image_4__isnull=True) | Q(image_4='')
            )
        elif self.value() == '2':
            return queryset.filter(
                ~Q(image__isnull=True) & ~Q(image=''),
                ~Q(image_2__isnull=True) & ~Q(image_2=''),
                Q(image_3__isnull=True) | Q(image_3=''),
                Q(image_4__isnull=True) | Q(image_4='')
            )
        elif self.value() == '3':
            return queryset.filter(
                ~Q(image__isnull=True) & ~Q(image=''),
                ~Q(image_2__isnull=True) & ~Q(image_2=''),
                ~Q(image_3__isnull=True) & ~Q(image_3=''),
                Q(image_4__isnull=True) | Q(image_4='')
            )
        elif self.value() == '4':
            return queryset.filter(
                ~Q(image__isnull=True) & ~Q(image=''),
                ~Q(image_2__isnull=True) & ~Q(image_2=''),
                ~Q(image_3__isnull=True) & ~Q(image_3=''),
                ~Q(image_4__isnull=True) & ~Q(image_4='')
            )

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
        'id', 'display_image_preview', 'name', 'brand', 'rating', 'display_tags', 'category',
        'display_image_count', 'stock_quantity', 'import_price', 'original_price', 'discounted_price',
        'discount_rate', 'status', 'is_visible'
    )

    # Chỉ giữ lại các trường có thể chỉnh sửa được
    list_editable = (
        'name', 'brand', 'stock_quantity', 'import_price',
        'original_price', 'discounted_price', 'status', 'is_visible'
    )

    list_filter = ('brand', 'category', 'tags', 'status', 'is_visible', ImageCountFilter)
    search_fields = ('name', 'brand__name', 'status')

    # Sử dụng filter_horizontal để chọn tags và gifts
    filter_horizontal = ('tags', 'gifts')

    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }

    fieldsets = (
        (None, {'fields': ('name', 'brand', 'category')}),
        ('Ảnh sản phẩm', {'fields': ('image', 'image_2', 'image_3', 'image_4')}),
        ('Mô tả', {'fields': ('description', 'ingredients')}),
        ('Thông tin giá và kho', {'fields': ('import_price', 'original_price', 'discounted_price', 'stock_quantity', 'sold_quantity')}),
        # Bỏ tags và gifts khỏi fieldsets để chúng được hiển thị bởi filter_horizontal
        ('Thuộc tính khác', {'fields': ('rating', 'status', 'is_visible')}),
        ('Tags và Quà tặng', {'fields': ('tags', 'gifts')}),
    )

    readonly_fields = ('discount_rate', 'savings_price')

    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    display_tags.short_description = "Tags"
    
    def display_image_count(self, obj):
        count = obj.get_image_count()
        if count == 0:
            return "❌ Không có ảnh"
        elif count == 1:
            return "🖼️ 1 ảnh"
        else:
            return f"🖼️ {count} ảnh"

    display_image_count.short_description = "Số ảnh"
    
    def display_image_preview(self, obj):
        """Hiển thị preview ảnh chính"""
        if obj.image:
            return f'<img src="{obj.image}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />'
        return "❌ Không có ảnh"
    
    display_image_preview.short_description = "Ảnh chính"
    display_image_preview.allow_tags = True


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
    list_display = ('id','order_code', 'customer_name', 'phone_number', 'order_date', 'total_amount', 'shipping_fee', 'collaborator_code', 'voucher', 'status', 'is_confirmed')
    list_filter = ('order_date', 'status', 'payment_method', 'is_confirmed')
    search_fields = ('customer_name', 'phone_number', 'collaborator_code', 'order_code')
    readonly_fields = ('total_amount', 'discount_applied', 'shipping_fee', 'order_date')
    list_editable = ('status', 'is_confirmed')
    actions = ['confirm_orders', 'ship_orders', 'cancel_orders']
    fieldsets = (
        (None, {'fields': ('order_code', 'customer', 'status', 'is_confirmed')}),
        ('Thông tin khách hàng', {'fields': ('customer_name', 'phone_number', 'zalo_phone_number', 'email')}),
        ('Địa chỉ giao hàng', {'fields': ('street', 'ward', 'district', 'province')}),
        ('Thanh toán và Khuyến mãi', {'fields': ('payment_method', 'bank_transfer_image', 'notes', 'voucher', 'collaborator_code')}),
        ('Chi tiết đơn hàng', {'fields': ('total_amount', 'shipping_fee', 'discount_applied')}),
    )

    def confirm_orders(self, request, queryset):
        """Xác nhận các đơn hàng được chọn"""
        updated = 0
        for order in queryset.filter(status='pending'):
            order.status = 'processing'
            order.is_confirmed = True
            order.save()
            updated += 1

        self.message_user(request, f'Đã xác nhận {updated} đơn hàng.')
    confirm_orders.short_description = "Xác nhận các đơn hàng được chọn"

    def ship_orders(self, request, queryset):
        """Đánh dấu các đơn hàng đã giao"""
        updated = 0
        for order in queryset.filter(status='processing'):
            order.status = 'shipped'
            order.save()
            updated += 1

        self.message_user(request, f'Đã đánh dấu {updated} đơn hàng đã giao.')
    ship_orders.short_description = "Đánh dấu các đơn hàng đã giao"

    def cancel_orders(self, request, queryset):
        """Hủy các đơn hàng được chọn"""
        updated = 0
        for order in queryset.exclude(status='cancelled'):
            order.status = 'cancelled'
            order.save()
            updated += 1

        self.message_user(request, f'Đã hủy {updated} đơn hàng.')
    cancel_orders.short_description = "Hủy các đơn hàng được chọn"

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
    list_editable = ('status',)
    actions = ['approve_applications', 'reject_applications']

    def approve_applications(self, request, queryset):
        """Duyệt các đơn đăng ký CTV được chọn"""
        approved = 0
        for app in queryset.filter(status='pending'):
            # Kiểm tra xem đã có CTV với SĐT này chưa
            if CTV.objects.filter(phone=app.phone).exists():
                self.message_user(request, f'CTV với SĐT {app.phone} đã tồn tại!', level=messages.WARNING)
                continue

            # Tạo CTV mới
            level = CTVLevel.objects.order_by('id').first()
            code = app.desired_code or f"CTV{app.phone[-4:] if app.phone else ''}"
            base = code or 'CTV'
            candidate = base
            suffix = 1
            while CTV.objects.filter(code__iexact=candidate).exists():
                candidate = f"{base}{suffix}"
                suffix += 1

            ctv = CTV.objects.create(
                code=candidate,
                desired_code=app.desired_code,
                full_name=app.full_name,
                phone=app.phone,
                email=app.email,
                address=app.address,
                bank_name=app.bank_name,
                bank_number=app.bank_number,
                bank_holder=app.bank_holder,
                cccd_front_url=app.cccd_front_url,
                cccd_back_url=app.cccd_back_url,
                level=level,
                is_active=True,
            )
            CTVWallet.objects.get_or_create(ctv=ctv)

            app.status = 'approved'
            app.agreed = True
            app.save()
            approved += 1

        self.message_user(request, f'Đã duyệt {approved} đơn đăng ký CTV.')
    approve_applications.short_description = "Duyệt các đơn đăng ký CTV được chọn"

    def reject_applications(self, request, queryset):
        """Từ chối các đơn đăng ký CTV được chọn"""
        updated = 0
        for app in queryset.filter(status='pending'):
            app.status = 'rejected'
            app.save()
            updated += 1

        self.message_user(request, f'Đã từ chối {updated} đơn đăng ký CTV.')
    reject_applications.short_description = "Từ chối các đơn đăng ký CTV được chọn"


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
    list_display = ('id', 'ctv', 'amount', 'status', 'requested_at', 'processed_at', 'note')
    list_filter = ('status', 'requested_at')
    search_fields = ('ctv__code', 'ctv__full_name', 'ctv__phone')
    readonly_fields = ('requested_at',)
    list_editable = ('status', 'note')
    actions = ['approve_withdrawals', 'reject_withdrawals']

    def approve_withdrawals(self, request, queryset):
        """Duyệt các yêu cầu rút tiền được chọn"""
        from django.utils import timezone
        updated = 0
        for withdrawal in queryset.filter(status='pending'):
            withdrawal.status = 'approved'
            withdrawal.processed_at = timezone.now()
            withdrawal.save()

            # Cập nhật ví CTV: chuyển từ pending sang withdrawn
            wallet = withdrawal.ctv.wallet
            wallet.pending = float(wallet.pending) - float(withdrawal.amount)
            wallet.save()
            updated += 1

        self.message_user(request, f'Đã duyệt {updated} yêu cầu rút tiền.')
    approve_withdrawals.short_description = "Duyệt các yêu cầu rút tiền được chọn"

    def reject_withdrawals(self, request, queryset):
        """Từ chối các yêu cầu rút tiền được chọn"""
        from django.utils import timezone
        updated = 0
        for withdrawal in queryset.filter(status='pending'):
            withdrawal.status = 'rejected'
            withdrawal.processed_at = timezone.now()
            withdrawal.save()

            # Hoàn lại tiền vào ví CTV: chuyển từ pending về balance
            wallet = withdrawal.ctv.wallet
            wallet.pending = float(wallet.pending) - float(withdrawal.amount)
            wallet.balance = float(wallet.balance) + float(withdrawal.amount)
            wallet.save()
            updated += 1

        self.message_user(request, f'Đã từ chối {updated} yêu cầu rút tiền.')
    reject_withdrawals.short_description = "Từ chối các yêu cầu rút tiền được chọn"


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

# Cart Admin
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    search_fields = ('user__name', 'user__email', 'user__phone_number')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity')
    search_fields = ('cart__user__name', 'product__name')

class LuckyPrizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'name', 'value', 'order')
    search_fields = ('name', 'event__title')
    list_filter = ('event',)
    ordering = ('event', 'order', 'id')

class MarketingResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'resource_type', 'file_url', 'download_count', 'is_active', 'created_at')
    list_filter = ('resource_type', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)
    readonly_fields = ('download_count', 'created_at', 'updated_at')
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'description', 'resource_type', 'is_active')
        }),
        ('File', {
            'fields': ('file_url', 'thumbnail_url', 'file_size')
        }),
        ('Liên kết', {
            'fields': ('product',),
            'classes': ('collapse',)
        }),
        ('Thống kê', {
            'fields': ('download_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Đăng ký các model còn thiếu
admin_site.register(Cart, CartAdmin)
admin_site.register(CartItem, CartItemAdmin)
admin_site.register(LuckyPrize, LuckyPrizeAdmin)
admin_site.register(MarketingResource, MarketingResourceAdmin)

