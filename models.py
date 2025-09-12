from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from ckeditor.fields import RichTextField
from django.contrib.auth.models import UserManager as BaseUserManager
from django.utils import timezone
import uuid
from django.db.models import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver

# Helper functions
def calculate_discount_rate(original_price, discounted_price):
    """
    Calculates the discount rate based on the original and discounted price.
    """
    if original_price is None or discounted_price is None or original_price == 0:
        return Decimal('0.00')

    original_price = Decimal(original_price)
    discounted_price = Decimal(discounted_price)

    if discounted_price >= original_price:
        return Decimal('0.00')

    discount_rate = ((original_price - discounted_price) / original_price) * 100
    return round(discount_rate, 2)


class UserManager(BaseUserManager):
    def create_user(self, email=None, phone_number=None, password=None, is_google_user=False, **extra_fields):
        # Normalize email
        if email:
            email = self.normalize_email(email)

        if not is_google_user and not (phone_number and password):
            raise ValueError('Đối với đăng ký thường, cần cung cấp số điện thoại và mật khẩu.')

        if is_google_user and not email:
            raise ValueError('Đăng ký bằng Google phải có email.')

        # Tạo đối tượng User
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        else:
            # Đặt mật khẩu không sử dụng được cho người dùng Google
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # Tạo superuser bằng email và mật khẩu
        return self.create_user(email=email, password=password, **extra_fields)


class User(AbstractUser):
    username = None
    name = models.CharField(max_length=40, blank=True, null=True, verbose_name="Họ tên")
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True, verbose_name="Số điện thoại")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Địa chỉ")
    email = models.CharField(max_length=255, unique=True, blank=True, null=True, verbose_name="Địa chỉ email")
    avatar = models.CharField(max_length=255, blank=True, null=True, verbose_name="ảnh đại diện")
    dob = models.DateField(blank=True, null=True, verbose_name="Ngày sinh")
    is_google_user = models.BooleanField(default=False, verbose_name="Đăng nhập bằng Google")


    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Tài khoản"
        verbose_name_plural = "Tài khoản người dùng"

    def __str__(self):
        if self.phone_number:
            return self.phone_number
        if self.email:
            return self.email
        return f"User ID: {self.id}"


class Admin(User):
    user_type = models.CharField(
        max_length=20,
        default="admin",
        editable=False,
        verbose_name="Loại tài khoản"
    )

    class Meta:
        verbose_name = "Quản trị viên"
        verbose_name_plural = "Quản trị viên"


class Collaborator(User):
    user_type = models.CharField(
        max_length=20,
        default="collaborator",
        editable=False,
        verbose_name="Loại tài khoản"
    )
    sales_code = models.CharField(max_length=20, unique=True, verbose_name="Mã bán hàng")
    points = models.PositiveIntegerField(default=0, verbose_name="Điểm bán hàng tháng này")
    level = models.PositiveIntegerField(default=1, verbose_name="Cấp độ")

    class Meta:
        verbose_name = "Cộng tác viên"
        verbose_name_plural = "Cộng tác viên"

    def __str__(self):
        return f"CTV: {self.phone_number or self.email}"

    def update_level(self):
        """Cập nhật cấp độ dựa trên số điểm trong tháng."""
        if self.points >= 2000:
            self.level = 5
        elif self.points >= 1000:
            self.level = 4
        elif self.points >= 500:
            self.level = 3
        elif self.points >= 100:
            self.level = 2
        else:
            self.level = 1
        self.save(update_fields=['level'])


class Staff(User):
    user_type = models.CharField(
        max_length=20,
        default="staff",
        editable=False,
        verbose_name="Loại tài khoản"
    )

    class Meta:
        verbose_name = "Nhân viên"
        verbose_name_plural = "Nhân viên"


class Customer(User):
    user_type = models.CharField(
        max_length=20,
        default="customer",
        editable=False,
        verbose_name="Loại tài khoản"
    )
    points = models.PositiveIntegerField(default=0, verbose_name="Điểm tích lũy")
    level = models.PositiveIntegerField(default=1, verbose_name="Cấp độ")

    class Meta:
        verbose_name = "Khách hàng"
        verbose_name_plural = "Khách hàng"

    def update_level(self):
        """Cập nhật cấp độ dựa trên số điểm."""
        if self.points >= 1000:
            self.level = 5
        elif self.points >= 400:
            self.level = 4
        elif self.points >= 100:
            self.level = 3
        elif self.points >= 30:
            self.level = 2
        else:
            self.level = 1
        self.save(update_fields=['level'])


# --- Product-related Models ---
class Brand(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tên hãng")
    country = models.CharField(max_length=100, verbose_name="Quốc gia")
    introduction = models.TextField(verbose_name="Giới thiệu")

    class Meta:
        verbose_name = "Hãng mỹ phẩm"
        verbose_name_plural = "Hãng mỹ phẩm"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")


    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"

    def __str__(self):
        return self.name


class AnalyticsSnapshot(models.Model):
    PERIOD_DAY = 'day'
    PERIOD_WEEK = 'week'
    PERIOD_MONTH = 'month'
    PERIOD_YEAR = 'year'

    PERIOD_CHOICES = [
        (PERIOD_DAY, 'Day'),
        (PERIOD_WEEK, 'Week'),
        (PERIOD_MONTH, 'Month'),
        (PERIOD_YEAR, 'Year'),
    ]

    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    period_key = models.CharField(max_length=32, help_text="Key of the period, e.g. 2025-09-07 or 2025-09 or 2025W36 or 2025")
    total_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    total_profit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    data = JSONField(default=dict, help_text="Arbitrary analytics payload: labels, series, top lists")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Analytics Snapshot"
        verbose_name_plural = "Analytics Snapshots"
        unique_together = ('period', 'period_key')

    def __str__(self):
        return f"Analytics {self.period}:{self.period_key} - {self.total_revenue}"


class Tag(models.Model):
    TAG_STATUS_CHOICES = [
        ('active', 'Đang hoạt động'),
        ('upcoming', 'Sắp diễn ra'),
        ('expired', 'Đã hết hạn'),
    ]

    code = models.CharField(max_length=50, unique=True, verbose_name="Mã tag")
    name = models.CharField(max_length=100, verbose_name="Tên tag")
    description = models.CharField(max_length=255, verbose_name="Mô tả")
    # Thêm giá trị mặc định cho các trường mới
    start_date = models.DateTimeField(verbose_name="Ngày giờ bắt đầu", default=timezone.now)
    end_date = models.DateTimeField(verbose_name="Ngày giờ kết thúc", default=timezone.now)
    status = models.CharField(max_length=20, choices=TAG_STATUS_CHOICES, default='upcoming', verbose_name="Trạng thái tag")
    discounted_price_reduction = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Giá giảm tiếp tục (nghìn đồng)"
    )

    class Meta:
        verbose_name = "Tag khuyến mãi"
        verbose_name_plural = "Tags khuyến mãi"

    def __str__(self):
        return self.name


class Gift(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tên quà tặng")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    image = models.CharField(max_length=255, verbose_name="URL ảnh")

    class Meta:
        verbose_name = "Quà tặng"
        verbose_name_plural = "Quà tặng"

    def __str__(self):
        return self.name


PRODUCT_STATUS_CHOICES = [
    ('new', 'Mới'),
    ('30', 'Dung tích còn 30%'),
    ('80', 'Dung tích còn 80%'),
    ('75', 'Dung tích còn 75%'),
    ('70', 'Dung tích còn 70%'),
    ('60', 'Dung tích còn 60%'),
    ('50', 'Dung tích còn 50%'),
    ('90', 'Dung tích còn 90%'),
    ('85', 'Dung tích còn 85%'),
    ('95', 'Dung tích còn 95%'),
    ('test', 'Test 1-2 lần'),
    ('newmh', 'Sản phẩm mới nhưng mất hộp'),
    ('newm', 'Sản phẩm mới nhưng hộp bị móp'),
    ('newrt', 'Sản phẩm mới nhưng rách tem'),
    ('newmn', 'Sản phẩm mới nhưng hộp bị móp nhẹ'),
    ('newx', 'Sản phẩm mới nhưng hộp bị xước'),
    ('newspx', 'Sản phẩm mới, mất hộp, bị xước'),
    ('chiet', 'Sản phẩm chiết'),
]


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tên sản phẩm")
    status = models.CharField(max_length=10, choices=PRODUCT_STATUS_CHOICES, default='new', verbose_name="Trạng thái sản phẩm")
    description = RichTextField(verbose_name="Mô tả sản phẩm")
    ingredients = RichTextField(verbose_name="Thành phần", blank=True, null=True)
    image = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ảnh")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, verbose_name="Hãng mỹ phẩm")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Danh mục")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Tag")
    gifts = models.ManyToManyField(Gift, blank=True, verbose_name="Quà tặng kèm")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="Số lượng còn trong kho")
    sold_quantity = models.PositiveIntegerField(default=0, verbose_name="Số lượng đã bán")
    rating = models.DecimalField(verbose_name="Lượt đánh giá trung bình", max_digits=3, decimal_places=1, default=4.2)
    savings_price = models.IntegerField(blank=True, null=True, verbose_name="Giá tiết kiệm (nghìn đồng)")
    import_price = models.IntegerField(verbose_name="Giá nhập kho (nghìn đồng)", default=0)
    original_price = models.IntegerField(verbose_name="Giá bán gốc (nghìn đồng)", default=0)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name="Mức giảm giá (%)")
    discounted_price = models.IntegerField(blank=True, null=True, verbose_name="Giá sau giảm (nghìn đồng)")

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"

    def __str__(self):
        return f"{self.name}"

# --- Order-related Models ---
class Voucher(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ("amount", "Giảm theo số tiền"),
        ("percentage", "Giảm theo phần trăm"),
    )

    code = models.CharField(max_length=20, unique=True, verbose_name="Mã voucher")
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default="amount", verbose_name="Loại giảm giá")
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá trị giảm giá")
    min_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Giá trị đơn hàng tối thiểu"
    )
    max_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Giá trị giảm tối đa"
    )
    is_active = models.BooleanField(default=True, verbose_name="Trạng thái kích hoạt")
    valid_from = models.DateTimeField(verbose_name="Có hiệu lực từ")
    valid_to = models.DateTimeField(verbose_name="Có hiệu lực đến")
    max_uses = models.PositiveIntegerField(default=0, verbose_name="Số lượt sử dụng tối đa")
    times_used = models.PositiveIntegerField(default=0, verbose_name="Số lượt đã sử dụng")

    class Meta:
        verbose_name = "Voucher"
        verbose_name_plural = "Vouchers"

    def __str__(self):
        return self.code

    def get_discount_amount(self, order_total):
        if self.discount_type == "amount":
            return self.discount_value
        elif self.discount_type == "percentage":
            return order_total * (self.discount_value / 100)
        return 0


class Order(models.Model):
    # Trạng thái đơn hàng
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('processing', 'Đang xử lý'),
        ('shipped', 'Đã giao hàng'),
        ('delivered', 'Đã nhận hàng'),
        ('cancelled', 'Đã hủy'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Ship COD'),
        ('bank', 'Chuyển khoản'),
        ('cash', 'Tiền mặt'),
    ]

    # Thêm trường mã đơn hàng
    order_code = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Mã đơn hàng")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Trạng thái đơn hàng"
    )
    is_confirmed = models.BooleanField(default=False, verbose_name="Xác nhận đơn hàng")
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders", verbose_name="Khách hàng")
    customer_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tên khách hàng")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại")
    zalo_phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại Zalo")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Địa chỉ")

    # Thông tin địa chỉ chi tiết
    street = models.CharField(max_length=100, blank=True, null=True, verbose_name="Số nhà/Tên đường")
    ward = models.CharField(max_length=100, blank=True, null=True, verbose_name="Phường/Xã")
    district = models.CharField(max_length=100, blank=True, null=True, verbose_name="Quận/Huyện")
    province = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tỉnh/Thành phố")

    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cod',
        verbose_name="Phương thức thanh toán"
    )
    bank_transfer_image = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ảnh chuyển khoản")

    # Các trường đã có
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đặt hàng")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Tổng tiền")
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Phí ship")
    collaborator_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="Mã CTV")
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Giảm giá áp dụng")
    voucher = models.ForeignKey(Voucher, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Voucher đã dùng")


    class Meta:
        verbose_name = "Hóa đơn"
        verbose_name_plural = "Hóa đơn mua hàng"


    def save(self, *args, **kwargs):
        is_new_order = self.pk is None # Kiểm tra xem đây có phải là đơn hàng mới hay không

        # Tạo mã đơn hàng tự động nếu chưa có
        if not self.order_code:
             # Lấy ngày tháng hiện tại (DDMM)
            date_str = timezone.now().strftime("%d%m")
            random_chars = str(uuid.uuid4())[:4]
            self.order_code = f"B-{date_str}{random_chars}"
        super().save(*args, **kwargs)

        # Cập nhật điểm và cấp độ sau khi lưu đơn hàng
        if is_new_order and self.status == 'delivered':
            # Chỉ cập nhật khi đơn hàng mới và đã được giao thành công
            self.update_points()

    def update_points(self):
        """Cập nhật điểm cho khách hàng và cộng tác viên."""
        order_points = int(self.total_amount / 100000)

        # Cập nhật điểm cho khách hàng
        if self.customer and isinstance(self.customer, Customer):
            self.customer.points += order_points
            self.customer.save(update_fields=['points'])
            self.customer.update_level()

        # Cập nhật điểm cho cộng tác viên
        if self.collaborator_code:
            try:
                collaborator = Collaborator.objects.get(sales_code=self.collaborator_code)
                collaborator.points += order_points
                collaborator.save(update_fields=['points'])
                collaborator.update_level()
            except Collaborator.DoesNotExist:
                # Xử lý trường hợp không tìm thấy cộng tác viên
                pass

    def __str__(self):
        if self.customer:
            return f"{self.customer.username} - {self.order_code}"
        else:
            return f"{self.customer_name} - {self.order_code}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Hóa đơn")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Sản phẩm")
    quantity = models.PositiveIntegerField(verbose_name="Số lượng")
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá tại thời điểm mua")

    class Meta:
        verbose_name = "Sản phẩm hóa đơn"
        verbose_name_plural = "Sản phẩm hóa đơn"

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart', verbose_name="Người dùng")

    class Meta:
        verbose_name = "Giỏ hàng"
        verbose_name_plural = "Giỏ hàng"

    def __str__(self):
        return f"Giỏ hàng của {self.user.name or self.user.phone_number}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Giỏ hàng"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Sản phẩm"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Số lượng"
    )

    class Meta:
        verbose_name = "Sản phẩm trong giỏ"
        verbose_name_plural = "Sản phẩm trong giỏ hàng"
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name} trong giỏ hàng của {self.cart.user.name or self.cart.user.phone_number}"



class Blog(models.Model):
    """
    Model Blog
    """
    BLOG_TAG_CHOICES = [
        ('HD', 'Hướng dẫn'),
        ('UD', 'Ưu đãi'),
        ('MLD', 'Mẹo làm đẹp'),
    ]
    tag = models.CharField(max_length=20, choices=BLOG_TAG_CHOICES,default='HD',verbose_name="Nhãn blog")
    title = models.CharField(max_length=255, verbose_name="Tiêu đề bài viết")
    short_description = models.TextField(verbose_name="Mô tả ngắn")
    post_date = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo blog")
    content = RichTextField(null=True, blank=True,verbose_name="Nội dung bài blog")
    link = models.CharField(max_length=255,null=True, blank=True, verbose_name="Link bài viết")
    img_thumbnail = models.CharField(max_length=255, verbose_name="Ảnh bìa blog")
    views = models.PositiveIntegerField(default=0, verbose_name="Lượt xem")
    is_active = models.BooleanField(default=True, verbose_name="Tình trạng hoạt động")

    class Meta:
        verbose_name = "Blog làm đẹp"
        verbose_name_plural = "Các Bài Blog"
        ordering = ['-post_date']


    def __str__(self):
        return f"{self.tag} x {self.title} {self.post_date} {self.is_active} {self.views}"





# --- Lucky Number Event Models ---
class LuckyEvent(models.Model):
    title = models.CharField(max_length=255, default="Sự kiện Số may mắn", verbose_name="Tiêu đề")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    start_at = models.DateTimeField(verbose_name="Bắt đầu")
    end_at = models.DateTimeField(verbose_name="Kết thúc")
    is_active = models.BooleanField(default=True, verbose_name="Đang diễn ra")
    lucky_number = models.CharField(max_length=2, blank=True, null=True, verbose_name="Số may mắn (2 số)")

    class Meta:
        verbose_name = "Sự kiện Số may mắn"
        verbose_name_plural = "Các Sự kiện Số may mắn"

    def __str__(self):
        return f"LuckyEvent {self.id} {self.title}"


class LuckyPrize(models.Model):
    event = models.ForeignKey(LuckyEvent, on_delete=models.CASCADE, related_name='prizes')
    name = models.CharField(max_length=255, verbose_name="Tên phần thưởng")
    image = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ảnh phần thưởng")
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Giá trị sản phẩm (nghìn đồng)")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự")

    class Meta:
        verbose_name = "Phần thưởng"
        verbose_name_plural = "Phần thưởng"
        ordering = ['order', 'id']

    def __str__(self):
        return f"Prize {self.name}"


class LuckyParticipant(models.Model):
    event = models.ForeignKey(LuckyEvent, on_delete=models.CASCADE, related_name='participants')
    chosen_number = models.CharField(max_length=2, verbose_name="Số chọn (00-99)")
    name = models.CharField(max_length=100, verbose_name="Tên")
    zalo_phone = models.CharField(max_length=20, verbose_name="SĐT Zalo")
    email = models.EmailField(verbose_name="Email")
    address = models.CharField(max_length=255, verbose_name="Địa chỉ")
    message = models.CharField(max_length=255, blank=True, null=True, verbose_name="Lời chúc")
    submitted_at = models.DateTimeField(default=timezone.now, verbose_name="Thời gian gửi")

    class Meta:
        verbose_name = "Người tham gia"
        verbose_name_plural = "Người tham gia"
        indexes = [
            models.Index(fields=['event', 'chosen_number', 'submitted_at'])
        ]

    def __str__(self):
        return f"{self.name} - {self.chosen_number}"


class LuckyWinner(models.Model):
    event = models.ForeignKey(LuckyEvent, on_delete=models.CASCADE, related_name='winners', verbose_name="Sự kiện")
    participant = models.ForeignKey(LuckyParticipant, on_delete=models.CASCADE, related_name='won_records', verbose_name="Người trúng")
    prize = models.ForeignKey(LuckyPrize, on_delete=models.SET_NULL, null=True, blank=True, related_name='winners', verbose_name="Phần thưởng")
    decided_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời điểm xác định")

    class Meta:
        verbose_name = "Người trúng thưởng"
        verbose_name_plural = "Người trúng thưởng"
        constraints = [
            models.UniqueConstraint(fields=['event', 'prize'], name='unique_event_prize_winner')
        ]

    def __str__(self):
        return f"Winner {self.participant.name} ({self.participant.chosen_number})"

class CustomerLead(models.Model):
    """Kho dữ liệu tiệp khách hàng (4 trường theo yêu cầu)."""
    name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Tên")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="SĐT")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Địa chỉ")
    # Mặc định là thời điểm hiện tại nếu để trống
    created_at = models.DateTimeField(default=timezone.now, blank=True, null=True)
    # Tự động cập nhật khi lưu
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tiệp khách hàng"
        verbose_name_plural = "Tiệp khách hàng"
        indexes = [
            models.Index(fields=["phone"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.name or ''} - {self.phone or self.email or ''}".strip()

    @staticmethod
    def upsert(name: str = None, phone: str = None, email: str = None, address: str = None) -> "CustomerLead":
        """Upsert theo số điện thoại.

        - Có số điện thoại: tạo mới hoặc cập nhật điền khuyết theo phone.
        - Không có số điện thoại: KHÔNG lưu (bỏ qua).
        """
        key_phone = (phone or "").strip()
        key_email = (email or "").strip()

        try:
            if not key_phone:
                # Yêu cầu mới: Không lưu bản ghi nếu không có SĐT
                return None

            lead = CustomerLead.objects.filter(phone=key_phone).first()
            if not lead:
                return CustomerLead.objects.create(
                    name=(name or "").strip() or None,
                    phone=key_phone,
                    email=key_email or None,
                    address=(address or "").strip() or None,
                )

            # Cập nhật điền khuyết cho lead cùng số điện thoại
            changed = False
            if (not lead.name) and name:
                lead.name = name.strip(); changed = True
            if (not lead.email) and key_email:
                lead.email = key_email; changed = True
            if (not lead.address) and address:
                lead.address = address.strip(); changed = True
            if changed:
                lead.save(update_fields=["name","email","address","updated_at"])
            return lead
        except Exception:
            return None






# --- CTV (Affiliate) Models ---
class CTVLevel(models.Model):
    name = models.CharField(max_length=100)
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Cấp CTV"
        verbose_name_plural = "Cấp CTV"

    def __str__(self):
        return f"{self.name} ({self.commission_percent}%)"


class CTVApplication(models.Model):
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.CharField(max_length=255, blank=True, null=True)
    desired_code = models.CharField(max_length=20, blank=True, null=True)
    bank_name = models.CharField(max_length=120)
    bank_number = models.CharField(max_length=50)
    bank_holder = models.CharField(max_length=150)
    cccd_front_url = models.CharField(max_length=500)
    cccd_back_url = models.CharField(max_length=500)
    sales_plan = models.TextField(blank=True, null=True)
    agreed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='pending')  # pending/approved/rejected
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Đơn đăng ký CTV"
        verbose_name_plural = "Đơn đăng ký CTV"
        ordering = ['-created_at']

    def __str__(self):
        return f"CTVApplication {self.full_name} - {self.phone} ({self.status})"


class CTV(models.Model):
    code = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.CharField(max_length=255, blank=True, null=True)
    bank_name = models.CharField(max_length=120)
    bank_number = models.CharField(max_length=50)
    bank_holder = models.CharField(max_length=150)
    cccd_front_url = models.CharField(max_length=500, blank=True, null=True, verbose_name="Ảnh CCCD mặt trước")
    cccd_back_url = models.CharField(max_length=500, blank=True, null=True, verbose_name="Ảnh CCCD mặt sau")
    password_text = models.CharField(max_length=255, blank=True, null=True, verbose_name="Mật khẩu đăng nhập")
    total_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name="Tổng doanh thu bán được (VND)")
    level = models.ForeignKey(CTVLevel, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cộng tác viên"
        verbose_name_plural = "Cộng tác viên"

    def __str__(self):
        return f"{self.code} - {self.full_name}"


class CTVWallet(models.Model):
    ctv = models.OneToOneField(CTV, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # VND
    pending = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ví CTV"
        verbose_name_plural = "Ví CTV"

    def __str__(self):
        return f"Wallet {self.ctv.code}: {self.balance}"


class CTVWithdrawal(models.Model):
    ctv = models.ForeignKey(CTV, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')  # pending/approved/rejected
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Yêu cầu rút ví CTV"
        verbose_name_plural = "Yêu cầu rút ví CTV"
        ordering = ['-requested_at']

    def __str__(self):
        return f"Withdraw {self.ctv.code} {self.amount} ({self.status})"


# --- Signals to keep CustomerLead in sync ---
@receiver(post_save, sender=Order)
def _lead_upsert_from_order(sender, instance, created, **kwargs):
    try:
        name = instance.customer_name
        phone = instance.phone_number
        email = instance.email
        address = ', '.join(filter(None, [instance.street, instance.ward, instance.district, instance.province]))
        CustomerLead.upsert(name=name, phone=phone, email=email, address=address)
    except Exception:
        pass


@receiver(post_save, sender=LuckyParticipant)
def _lead_upsert_from_participant(sender, instance, created, **kwargs):
    try:
        CustomerLead.upsert(
            name=instance.name,
            phone=instance.zalo_phone,
            email=instance.email,
            address=instance.address,
        )
    except Exception:
        pass


@receiver(post_save, sender=Customer)
def _lead_upsert_from_customer(sender, instance, created, **kwargs):
    try:
        CustomerLead.upsert(
            name=getattr(instance, 'name', None),
            phone=getattr(instance, 'phone_number', None),
            email=getattr(instance, 'email', None),
            address=getattr(instance, 'address', None),
        )
    except Exception:
        pass
