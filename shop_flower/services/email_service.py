from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def send_order_confirmation_email(order, order_items, payment_url=None):
    # Không gửi nếu không có email
    if not order.email:
        return
    try:
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
                "payment_url": payment_url,  # ⭐ QUAN TRỌNG
                "logo_url": f"{settings.SITE_URL}/static/shop_flower/banners/banner_3.webp",
                "banner_url": f"{settings.SITE_URL}/static/shop_flower/logo.jpg",
            }
        )

        email = EmailMultiAlternatives(
            subject=subject,
            body=f"Xác nhận đơn hàng #{order.id}",
            from_email=settings.EMAIL_HOST_USER,
            to=[order.email],
        )

        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=True)   # => không raise exception
    except Exception as e:
        # log lỗi, không raise để worker không bị kill
        import logging
        logging.exception("Failed to send order confirmation email (non-fatal).")
