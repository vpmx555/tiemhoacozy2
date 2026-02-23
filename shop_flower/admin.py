from django.contrib import admin
from .models import Flower
from .models import FlowerType
from .models import FlowerBatch

# Register your models here.

@admin.register(FlowerType)
class FlowerTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(FlowerBatch)
class FlowerBatchAdmin(admin.ModelAdmin):

    list_display = (
        'flower',
        'import_date',
        'expire_date',
        'import_price',
        'quantity',
        'remaining_quantity',
        'status',
    )

    list_filter = (
        'status',
        'import_date',
        'expire_date',
        'flower',
    )

    search_fields = ('flower__name',)

    date_hierarchy = 'import_date'

    exclude = ('remaining_quantity',)

    def save_model(self, request, obj, form, change):

        # ✅ chỉ khi nhập kho lần đầu
        if not change:
            obj.remaining_quantity = obj.quantity

        # ✅ auto status
        obj.status = (
            "hết hàng" if obj.remaining_quantity <= 0 else "còn hàng"
        )

        super().save_model(request, obj, form, change)


from django.db.models import Sum


@admin.register(Flower)
class FlowerAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'get_flower_types',   # ✅ thay flower_type
        'sell_price',
        'is_active',
        'stock',
    )

    list_filter = ('flower_types',)
    search_fields = ('name',)
    filter_horizontal = ('flower_types',)

    def get_flower_types(self, obj):
        return ", ".join(
            t.name for t in obj.flower_types.all()
        )

    get_flower_types.short_description = "Loại hoa"

    def stock(self, obj):
        return obj.flowerbatch_set.aggregate(
            total=Sum('remaining_quantity')
        )['total'] or 0

    stock.short_description = "Tồn kho"

from django.core.mail import send_mail
from .models import Order, Payment

@admin.action(description="Xác nhận thanh toán và chuyển đơn sang 'đang giao'")
def confirm_payment_and_ship(modeladmin, request, queryset):
    # queryset sẽ là set of Payment
    for payment in queryset:
        payment.status = "confirmed"
        payment.save()
        order = payment.order
        order.status = "đang giao"
        order.save()
        # gửi mail cho khách
        subject = f"[HolaFlower] Đơn hàng #{order.id} đang được vận chuyển"
        message = f"Xin chào {order.customer_name},\n\nĐơn hàng #{order.id} của bạn đã được xác nhận và đang trong quá trình vận chuyển."
        if order.email:
            send_mail(subject, message, None, [order.email], fail_silently=True)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "method", "status", "amount", "created_at")
    actions = [confirm_payment_and_ship]

admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order)