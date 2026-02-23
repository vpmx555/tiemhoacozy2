# shop_flower/emails.py
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def send_order_confirmation_email(order, items, payment_url=None):
    subject = f"[Tiệm Hoa Cozy] Xác nhận đơn hàng #{order.id}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [order.email] if order.email else []

    context = {
        "order": order,
        "items": items,
        "payment_url": payment_url,
    }

    html_content = render_to_string("shop_flower/order_confirmation.html", context)
    text_content = render_to_string("shop_flower/order_confirmation_text.txt", context) if False else ""

    if to_email:
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)