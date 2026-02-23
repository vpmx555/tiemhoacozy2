
# Create your models here.
from django.db import models
from django.utils import timezone


class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=255)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    default_address = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    address = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.address


class FlowerType(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Flower(models.Model):
    name = models.CharField(max_length=100)
    flower_types = models.ManyToManyField(
        FlowerType,
        related_name="flowers",
        blank=True
    )
    sell_price = models.DecimalField(max_digits=12, decimal_places=2)
    image = models.ImageField(upload_to='flowers/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name



class FlowerBatch(models.Model):
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    import_date = models.DateField()
    expire_date = models.DateField(null=True, blank=True)
    import_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.IntegerField()
    remaining_quantity = models.IntegerField(editable=False)
    status = models.CharField(max_length=50, default="còn hàng")

    def __str__(self):
        return f"{self.flower.name} - {self.import_date}"


from decimal import Decimal

class Order(models.Model):
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    created_at = models.DateTimeField(
    auto_now_add=True,
    null=True,
    blank=True
    )

    customer_name = models.CharField(
        max_length=255,
        default="Unknown"
    )

    note = models.CharField(
        null=True,
        blank=True,
        max_length=1000
    )

    phone = models.CharField(
        max_length=20,
        default="Unknown"
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    delivery_address = models.CharField(
        max_length=255
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    status = models.CharField(
        max_length=50,
        default="chờ duyệt",
        choices=[
            ("chờ duyệt", "Chờ duyệt"),
            ("đang giao", "Đang giao"),
            ("hoàn tất", "Hoàn tất"),
            ("hủy", "Hủy"),
        ]
    )

    voucher = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    shipper_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    shipper_number = models.CharField(
        max_length=12,
        blank=True,
        null=True
    )

    sub_total = models.DecimalField(
    max_digits=12,
    decimal_places=2,
    default=Decimal("0.00")
    )

    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    shipping_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)


class FlowerSalesSummary(models.Model):
    flower = models.OneToOneField(Flower, on_delete=models.CASCADE, primary_key=True)
    total_sold = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)


class DailySales(models.Model):
    sale_date = models.DateField(primary_key=True)
    total_orders = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)


class Admin(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=255)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    role = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.username


class ProductFunnelLog(models.Model):
    session_id = models.CharField(max_length=100, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)

    view_count = models.IntegerField(default=0)
    view_duration = models.IntegerField(default=0)

    added_to_cart = models.BooleanField(default=False)
    ordered = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)

    first_view_time = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)


class FlowerImage(models.Model):
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE, related_name="images")
    image_url = models.CharField(max_length=255)
    is_cover = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

class Payment(models.Model):
    METHOD_CHOICES = [
        ("cash", "Tiền mặt"),
        ("bank", "Chuyển khoản"),
    ]

    STATUS_CHOICES = [
        ("pending", "Chờ thanh toán"),    # mới tạo, chưa user chọn
        ("initiated", "Đã bắt đầu thanh toán / chờ xác nhận"),  # user đã chọn phương thức (hoặc bấm 'Tôi đã chuyển khoản')
        ("confirmed", "Đã xác nhận"),     # admin xác nhận đã nhận tiền
        ("failed", "Thất bại"),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment"
    )

    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    # bằng chứng (optional) - upload proof image nếu user muốn
    proof = models.ImageField(
        upload_to="payments/proofs/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Payment for Order #{self.order_id} ({self.method} - {self.status})"