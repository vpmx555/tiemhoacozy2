from django.shortcuts import render, get_object_or_404, redirect
from .models import Flower
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Order, OrderItem
import json
from decimal import Decimal
from .emails import (
    send_order_confirmation_email,
    send_new_order_notify_admin
)
from .models import Flower, FlowerType
from django.db.models import Q
from shop_flower.services.vietqr_api import generate_vietqr_image_url

from django.db.models import Sum
from django.db.models.functions import Coalesce

from django.db.models import Sum
from django.db.models.functions import Coalesce

def home(request):
    base_flowers = (
        Flower.objects
        .filter(is_active=True)
        .annotate(
            stock=Coalesce(
                Sum("flowerbatch__remaining_quantity"),
                0
            )
        )
    )

    flowers_type_1 = (
        base_flowers
        .filter(flower_types__id=1)
        .order_by("id")   # id nhỏ nhất = tạo sớm nhất
        .distinct()[:8]
    )

    flowers_type_4 = (
        base_flowers
        .filter(flower_types__id=4)
        .distinct()
        [:8]
    )

    flowers_type_17 = (
        base_flowers
        .filter(flower_types__id=17)
        .distinct()
        [:8]
    )

    return render(request, "shop_flower/home.html", {
        "flowers_type_1": flowers_type_1,
        "flowers_type_4": flowers_type_4,
        "flowers_type_17": flowers_type_17,
    })



from django.db.models import Sum, Q
from .models import Flower, FlowerType

from django.db.models import Sum
from django.db.models.functions import Coalesce


def product_list(request):

    flowers = (
        Flower.objects
        .filter(is_active=True)
        .annotate(
            total_stock=Coalesce(
                Sum("flowerbatch__remaining_quantity"),
                0
            )
        )
    )

    flower_types = FlowerType.objects.all()

    keyword = request.GET.get("q")
    flower_type_id = request.GET.get("type")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    sort = request.GET.get("sort")

    # -------------------------
    # normalize params
    # -------------------------
    if keyword in ["", "None", None]:
        keyword = None

    if flower_type_id in ["", "None", None]:
        flower_type_id = None

    # -------------------------
    # 🔍 search
    # -------------------------
    if keyword:
        flowers = flowers.filter(
            name__icontains=keyword
        )

    # -------------------------
    # 🌸 lọc loại hoa (ManyToMany)
    # -------------------------
    if flower_type_id:
        flowers = flowers.filter(
            flower_types=flower_type_id
        ).distinct()

    # -------------------------
    # 💰 lọc giá
    # -------------------------
    if min_price:
        flowers = flowers.filter(
            sell_price__gte=min_price
        )

    if max_price:
        flowers = flowers.filter(
            sell_price__lte=max_price
        )

    # -------------------------
    # 🔃 sort
    # -------------------------
    if sort == "price_asc":
        flowers = flowers.order_by("sell_price")

    elif sort == "price_desc":
        flowers = flowers.order_by("-sell_price")

    elif sort == "name":
        flowers = flowers.order_by("name")

    elif sort == "new":
        flowers = flowers.order_by("-id")

    context = {
        "flowers": flowers,
        "flower_types": flower_types,

        "keyword": keyword,
        "selected_type": flower_type_id,

        "min_price": min_price,
        "max_price": max_price,
        "sort": sort,
    }

    return render(request, "shop_flower/product_list.html", context)



from django.shortcuts import render, get_object_or_404
from .models import Flower

from django.shortcuts import get_object_or_404, render
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from .models import Flower


def product_detail(request, id):
    # queryset cơ sở có annotate stock
    base_flowers = (
        Flower.objects
        .filter(is_active=True)
        .annotate(
            stock=Coalesce(
                Sum("flowerbatch__remaining_quantity"),
                0
            )
        )
        .prefetch_related("flower_types")
    )

    # lấy flower hiện tại (đã có stock)
    flower = get_object_or_404(base_flowers, id=id)

    # 🔥 related products: share ít nhất 1 flower_type
    related_products = base_flowers.filter(
        flower_types__in=flower.flower_types.all()
    ).exclude(
        id=flower.id
    ).distinct().order_by("?")[:8]

    context = {
        "flower": flower,
        "related_products": related_products,
    }
    return render(request, "shop_flower/product_detail.html", context)

def cart(request):
    return render(request, 'shop_flower/cart.html')

def add_to_cart(request, flower_id):
    cart = request.session.get("cart", {})
    cart[str(flower_id)] = cart.get(str(flower_id), 0) + 1
    request.session["cart"] = cart
    return JsonResponse({"success": True})

def cart_detail(request):
    cart = request.session.get('cart', {})
    flowers = []
    total = 0

    for flower_id, quantity in cart.items():
        flower = Flower.objects.get(id=flower_id)
        flower.quantity = quantity
        flower.subtotal = flower.sell_price * quantity
        total += flower.subtotal
        flowers.append(flower)

    return render(request, 'cart.html', {
        'cart_flowers': flowers,
        'total': total
    })

def get_cart(request):
    cart = request.session.get("cart", {})
    items = []
    total = 0

    for fid, qty in cart.items():
        flower = Flower.objects.get(id=fid)
        subtotal = flower.sell_price * qty
        total += subtotal

        items.append({
            "id": flower.id,
            "name": flower.name,
            "price": float(flower.sell_price),
            "qty": qty,
            "image": flower.image.url,
            "subtotal": float(subtotal)
        })

    return JsonResponse({
        "items": items,
        "total": float(total)
    })

def update_cart(request):
    cart = request.session.get("cart", {})
    fid = request.POST.get("id")
    qty = int(request.POST.get("qty", 1))

    if qty <= 0:
        cart.pop(fid, None)
    else:
        cart[fid] = qty

    request.session["cart"] = cart
    return JsonResponse({"success": True})

def remove_cart(request):
    cart = request.session.get("cart", {})
    fid = request.POST.get("id")
    cart.pop(fid, None)
    request.session["cart"] = cart
    return JsonResponse({"success": True})

#check out
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.core.mail import send_mail

from .models import Order, OrderItem, Flower, Payment
from shop_flower.services.payment_token import generate_payment_token


import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.mail import send_mail

from .models import Order, OrderItem, Flower


from decimal import Decimal
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem, Flower
from .emails import send_order_confirmation_email
from django.urls import reverse

def checkout(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))

        cart = data.get("cart", [])
        voucher = data.get("voucher")
        customer = data.get("customer", {})

        name = customer.get("name") or "Unknown"
        phone = customer.get("phone") or "Unknown"
        email = customer.get("email") or ""
        address = customer.get("address") or ""
        note = customer.get("note") or ""

        if not cart:
            return JsonResponse({
                "success": False,
                "message": "Giỏ hàng trống"
            })

        # 1) CREATE ORDER
        order = Order.objects.create(
            user=None,
            customer_name=name,
            phone=phone,
            email=email,
            delivery_address=address,
            note=note,
            sub_total=0,
            discount_amount=0,
            shipping_fee=0,
            total_amount=0,
            status="chờ duyệt"
        )

        total = Decimal("0")
        order_items = []

        # 2) CREATE ORDER ITEMS
        for item in cart:
            flower_id = item["flower_id"]
            qty = max(1, int(item.get("quantity", 1)))
            flower = get_object_or_404(Flower, id=flower_id)
            price = Decimal(flower.sell_price)

            item_total = price * qty  # TÍNH TOTAL TỪNG ITEM

            order_item = OrderItem.objects.create(
                order=order,
                flower=flower,
                quantity=qty,
                price=price,
                total=item_total
            )

            order_items.append(order_item)
            total += item_total

        # 3) VOUCHER
        discount = Decimal("0")
        shipping_fee = Decimal("30000")

        if voucher == "FREESHIP":
            shipping_fee = Decimal("0")
        elif voucher == "DISCOUNT10":
            discount = total * Decimal("0.10")

        final_total = total - discount + shipping_fee

        # 4) UPDATE ORDER
        order.sub_total = total
        order.discount_amount = discount
        order.shipping_fee = shipping_fee
        order.total_amount = final_total
        order.save()

        # 5) CREATE PAYMENT (pending)
        payment = Payment.objects.create(
            order=order,
            amount=final_total,
            status="pending"
        )

        # 6) GENERATE PAYMENT TOKEN
        payment_token = generate_payment_token(order.id)

        # --- Kiểm tra bắt buộc có email (theo yêu cầu): nếu không có, rollback/cleanup và trả lỗi ---
        if not email:
            # Xoá payment (nếu cần) và order (các order_items sẽ bị cascade nếu FK on_delete=CASCADE)
            try:
                payment.delete()
            except Exception:
                pass
            try:
                order.delete()
            except Exception:
                pass

            return JsonResponse({
                "success": False,
                "message": "Đơn hàng thất bại: không tìm thấy địa chỉ email"
            })

        # 7) SEND EMAIL (gửi link payment)
        email_sent = False
        admin_notified = False
        payment_url = request.build_absolute_uri(
            reverse('payment', args=[payment_token])
        )

        try:
            email_sent = send_order_confirmation_email(order, order_items, payment_url=payment_url)
        except Exception as e:
            print("Error when sending order confirmation email:", e)
            email_sent = False

        try:
            admin_notified = send_new_order_notify_admin(order, order_items)
        except Exception as e:
            print("Error when sending admin notification:", e)
            admin_notified = False

        # 8) SAVE SESSION
        request.session["order_id"] = order.id

        # 9) Trả về kết quả chi tiết (order tạo xong; báo kết quả gửi email)
        if email_sent:
            return JsonResponse({
                "success": True,
                "order_id": order.id,
                "email_sent": True,
                "message": "Đặt hàng thành công. Email xác nhận đã được gửi."
            })
        else:
            return JsonResponse({
                "success": True,
                "order_id": order.id,
                "email_sent": False,
                "message": "Đặt hàng thành công nhưng không thể gửi email xác nhận. Shop sẽ xử lý thủ công."
            })

    return render(request, "shop_flower/checkout.html")


def order_pending(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    return render(
        request,
        "shop_flower/order_pending.html",
        {
            "order": order
        }
    )

def blog(request):
    return render(request, "shop_flower/blog.html")

def about(request):
    return render(request, "shop_flower/about.html")

def contact(request):
    return render(request, "shop_flower/contact.html")

def policy(request):
    return render(request, "shop_flower/policy.html")

# shop_flower/views.py (thêm phần imports ở đầu file)
import base64
from io import BytesIO
import qrcode
from django.conf import settings
from django.shortcuts import render, redirect
from .services.payment_token import verify_payment_token

from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .models import Order, Payment
from .services.vietqr_api import generate_vietqr  # dùng API
# nếu bạn vẫn muốn dùng local QR thì đổi lại import

@require_http_methods(["GET", "POST"])
def payment(request, token):
    # =========================
    # VERIFY TOKEN
    # =========================
    order_id = verify_payment_token(token)
    if not order_id:
        return render(request, "shop_flower/payment_invalid.html", status=400)

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return render(request, "shop_flower/payment_invalid.html", status=404)

    # =========================
    # GET OR CREATE PAYMENT
    # =========================
    payment, _ = Payment.objects.get_or_create(
        order=order,
        defaults={
            "amount": order.total_amount,
            "status": "pending",
        },
    )

    context = {
        "order": order,
        "payment": payment,
        "token": token,
    }

    # =========================================================
    # POST HANDLE
    # =========================================================
    if request.method == "POST":
        method = request.POST.get("method")
        action = request.POST.get("action")
        proof_file = request.FILES.get("proof")

        # ---------- chọn phương thức ----------
        if method:
            if method not in ("cash", "bank"):
                context["error"] = "Phương thức không hợp lệ."
                return render(request, "shop_flower/payment_page.html", context)

            payment.method = method
            payment.status = "initiated"

            if proof_file:
                payment.proof = proof_file

            payment.save()

            # ===== CASH =====
            if method == "cash":
                context["message"] = (
                    "Bạn đã chọn Thanh toán tiền mặt. "
                    "Admin sẽ liên hệ để xác nhận."
                )
                return render(request, "shop_flower/payment_page.html", context)

            # ===== BANK =====
            if method == "bank":
                return redirect(f"{reverse('payment', args=[token])}?show_bank=1")

        # ---------- user báo đã chuyển ----------
        if action == "i_have_transferred":
            if proof_file:
                payment.proof = proof_file

            payment.status = "initiated"
            payment.save()

            context["message"] = (
                "Cảm ơn. Chúng tôi đã nhận thông báo. "
                "Admin sẽ kiểm tra và xác nhận sớm."
            )
            return render(request, "shop_flower/payment_page.html", context)

    # =========================================================
    # GET → GENERATE VIETQR (CHỈ KHI BANK)
    # =========================================================
    print("PAYMENT METHOD:", payment.method)
    if payment.method == "bank":
        try:
            print("QR BLOCK ENTERED")
            qr_url = generate_vietqr_image_url(order)

            context.update({
                "qr_data_uri": qr_url,
                "bank_account": settings.VIETQR_ACCOUNT_NO,
                "beneficiary": settings.VIETQR_ACCOUNT_NAME,
                "bank_name": getattr(settings, "VIETQR_BANK_NAME", "Ngân hàng"),
            })

        except Exception as e:
            # ⚠️ tránh crash production
            context["error"] = "Không thể tạo mã QR. Vui lòng thử lại sau."
            print("VIETQR ERROR:", e)

    return render(request, "shop_flower/payment_page.html", context)