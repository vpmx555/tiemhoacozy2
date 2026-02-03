from django.shortcuts import render, get_object_or_404, redirect
from .models import Flower
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Order, OrderItem
import json
from decimal import Decimal
from .services.email_service import send_order_confirmation_email
from .models import Flower, FlowerType
from django.db.models import Q

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
        .filter(flower_types__id=1)   # ✔ M2M: trong list có id=1
        .distinct()                  # ✔ tránh duplicate do JOIN
        [:8]                          # ✔ tối đa 8
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



def product_detail(request, id):
    flower = get_object_or_404(Flower, id=id)

    return render(request, 'shop_flower/product_detail.html', {
        'flower': flower
    })

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

from .models import Order, OrderItem, Flower


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
from .services.email_service import send_order_confirmation_email


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

        # =========================
        # 1️⃣ CREATE ORDER
        # =========================
        order = Order.objects.create(
            user=None,
            customer_name=name,
            phone=phone,
            email=email,
            delivery_address=address,
            note=note,
            total_amount=0,
            status="pending"
        )

        total = Decimal("0")
        order_items = []

        # =========================
        # 2️⃣ CREATE ORDER ITEMS
        # =========================
        for item in cart:

            flower_id = item["flower_id"]
            qty = max(1, int(item.get("quantity", 1)))

            flower = get_object_or_404(Flower, id=flower_id)
            price = Decimal(flower.sell_price)

            order_item = OrderItem.objects.create(
                order=order,
                flower=flower,
                quantity=qty,
                price=price
            )

            order_items.append(order_item)
            total += price * qty

        # =========================
        # 3️⃣ VOUCHER
        # =========================
        discount = Decimal("0")
        shipping_fee = Decimal("30000")

        if voucher == "FREESHIP":
            shipping_fee = Decimal("0")
        elif voucher == "DISCOUNT10":
            discount = total * Decimal("0.10")

        final_total = total - discount + shipping_fee

        # =========================
        # 4️⃣ UPDATE ORDER
        # =========================
        order.sub_total = total
        order.discount_amount = discount
        order.total_amount = final_total
        order.save()

        # =========================
        # 5️⃣ SEND EMAIL
        # =========================
        if email:
            send_order_confirmation_email(order, order_items)

        # =========================
        # 6️⃣ SAVE SESSION
        # =========================
        request.session["order_id"] = order.id

        return JsonResponse({
            "success": True,
            "order_id": order.id
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