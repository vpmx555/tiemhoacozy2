# shop_flower/emails.py
import os
from django.template.loader import render_to_string
from django.conf import settings

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_order_confirmation_email(order, items, payment_url=None):
    """
    Gửi email xác nhận đơn hàng bằng SendGrid Web API
    (không dùng SMTP -> Railway không bị timeout)
    """

    if not order.email:
        return

    subject = f"[Tiệm Hoa Cozy] Xác nhận đơn hàng #{order.id}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = order.email

    print("đã gửi")

    context = {
        "order": order,
        "items": items,
        "payment_url": payment_url,
    }

    html_content = render_to_string(
        "email/order_confirmation.html",
        context,
    )

    try:
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
        )

        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)

        # debug nhẹ
        print("SendGrid status:", response.status_code)

    except Exception as e:
        # không crash production
        print("SENDGRID ERROR:", e)
def send_new_order_notify_admin(order, items):
    """
    Gửi email báo admin có đơn hàng mới (ngay khi khách đặt)
    """

    admin_email = getattr(settings, "ADMIN_EMAIL", None)

    if not admin_email:
        print("ADMIN_EMAIL not set")
        return

    subject = f"[Tiệm Hoa Cozy] Đơn hàng mới #{order.id}"

    context = {
        "order": order,
        "items": items,
    }

    html_content = render_to_string(
        "email/new_order_admin.html",
        context,
    )

    try:
        message = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=admin_email,
            subject=subject,
            html_content=html_content,
        )

        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)

        print("New order admin mail:", response.status_code)

    except Exception as e:
        print("NEW ORDER ADMIN MAIL ERROR:", e)