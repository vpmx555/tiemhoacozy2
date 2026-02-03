from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def send_order_confirmation_email(order, order_items):

    subject = f"Xác nhận đơn hàng #{order.id}"

    items = []
    for item in order_items:
        items.append({
            "flower": item.flower,
            "quantity": item.quantity,
            "total": item.price * item.quantity
        })

    html_content = render_to_string(
        "email/order_confirmation.html",
        {
            "order": order,
            "items": items,
            "logo_url": f"{settings.SITE_URL}/static/shop_flower/banners/banner_3.webp",
            "banner_url": f"{settings.SITE_URL}/static/shop_flower/logo.jpg",
        }
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body="HolaFlower Order Confirmation",
        from_email=settings.EMAIL_HOST_USER,
        to=[order.email]
    )

    email.attach_alternative(html_content, "text/html")
    email.send()
