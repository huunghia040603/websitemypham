from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from ckeditor.fields import RichTextField
from django.contrib.auth.models import UserManager as BaseUserManager


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
    def create_user(self, phone_number, password, **extra_fields):
        if not phone_number:
            raise ValueError('Số điện thoại phải được cung cấp.')

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number=phone_number, password=password, **extra_fields)


class User(AbstractUser):
    username = None
    name = models.CharField(max_length=40, blank=True, null=True, verbose_name="Họ tên")
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True, verbose_name="Số điện thoại")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Địa chỉ")
    email = models.CharField(max_length=255, blank=True, null=True, verbose_name="Địa chỉ email")
    avatar = models.CharField(max_length=255, blank=True, null=True, verbose_name="ảnh đại diện")
    dob = models.DateField(blank=True, null=True, verbose_name="Ngày sinh")

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

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

    class Meta:
        verbose_name = "Cộng tác viên"
        verbose_name_plural = "Cộng tác viên"

    def __str__(self):
        return f"CTV: {self.phone_number or self.email}"


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

    class Meta:
        verbose_name = "Khách hàng"
        verbose_name_plural = "Khách hàng"


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


class Tag(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã tag")
    name = models.CharField(max_length=100, verbose_name="Tên tag")
    description = models.CharField(max_length=255, verbose_name="Mô tả")

    class Meta:
        verbose_name = "Tag sản phẩm"
        verbose_name_plural = "Tag sản phẩm"

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


class Album(models.Model):
    name = models.CharField(max_length=255, blank=True, verbose_name="Tên album")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    class Meta:
        verbose_name = "Album ảnh"
        verbose_name_plural = "Album ảnh"

    def __str__(self):
        return f"Album {self.id}"


class Image(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='images', verbose_name="Album")
    image = models.CharField(max_length=255, verbose_name="URL ảnh")
    is_thumbnail = models.BooleanField(default=False, verbose_name="Ảnh đại diện")

    class Meta:
        verbose_name = "Hình ảnh"
        verbose_name_plural = "Hình ảnh sản phẩm"

    def __str__(self):
        return f"Image for Album {self.album.id}"

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
    ingredients = RichTextField(verbose_name="Thành phần",blank=True, null=True,)
    volume = models.CharField(max_length=50, blank=True, null=True, verbose_name="Dung tích")
    unit = models.CharField(max_length=50, blank=True, null=True, verbose_name="Đơn vị")
    image = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ảnh")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, verbose_name="Hãng mỹ phẩm")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Danh mục")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Tag")
    gifts = models.ManyToManyField(Gift, blank=True, verbose_name="Quà tặng kèm")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="Số lượng còn trong kho")
    sold_quantity = models.PositiveIntegerField(default=0, verbose_name="Số lượng đã bán")
    rating = models.DecimalField(verbose_name="Lượt đánh giá trung bình", max_digits=3, decimal_places=1, default=3.2)
    market_price = models.IntegerField(blank=True, null=True, verbose_name="Giá thị trường")
    savings_price = models.IntegerField(blank=True, null=True, verbose_name="Giá tiết kiệm (nghìn đồng)")
    import_price = models.IntegerField(verbose_name="Giá nhập kho (nghìn đồng)", default=0)
    original_price = models.IntegerField(verbose_name="Giá bán gốc (nghìn đồng)", default=0)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name="Mức giảm giá (%)")
    discounted_price = models.IntegerField(blank=True, null=True, verbose_name="Giá sau giảm (nghìn đồng)")

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"

    def save(self, *args, **kwargs):
        # Tính discount_rate dựa trên giá gốc và giá sau giảm
        if self.original_price is not None and self.discounted_price is not None:
            self.discount_rate = calculate_discount_rate(self.original_price, self.discounted_price)
        else:
            self.discount_rate = Decimal('0.00')

        # Tính savings_price dựa trên giá thị trường và giá sau giảm
        if self.market_price is not None and self.discounted_price is not None:
            self.savings_price = self.market_price - self.discounted_price
        else:
            self.savings_price = None

        super().save(*args, **kwargs)

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
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", verbose_name="Khách hàng")
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đặt hàng")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Tổng tiền")
    collaborator_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="Mã CTV")
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Giảm giá áp dụng")
    voucher = models.ForeignKey(Voucher, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Voucher đã dùng")

    class Meta:
        verbose_name = "Hóa đơn"
        verbose_name_plural = "Hóa đơn mua hàng"

    def __str__(self):
        return f"Order #{self.id} by {self.customer.username}"


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