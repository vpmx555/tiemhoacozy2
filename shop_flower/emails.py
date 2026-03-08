import json
import os
from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.template.loader import render_to_string
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from backend import settings

# ... các import model: Order, OrderItem, Flower, Payment, settings, etc.

def send_order_confirmation_email(order, items, payment_url=None):
    """
    Gửi email xác nhận đơn hàng bằng SendGrid Web API
    Trả về True nếu gửi thành công (status_code 2xx), False nếu lỗi hoặc không có email.
    """
    if not order.email:
        return False

    subject = f"[Tiệm Hoa Cozy] Xác nhận đơn hàng #{order.id}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = order.email

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

        # Nếu status code 2xx -> thành công
        if 200 <= getattr(response, "status_code", 0) < 300:
            print("SendGrid status (order confirmation):", response.status_code)
            return True
        else:
            print("SendGrid returned non-2xx for order confirmation:", getattr(response, "status_code", None))
            return False

    except Exception as e:
        # không crash production, log và trả False
        print("SENDGRID ERROR (order confirmation):", e)
        return False


def send_new_order_notify_admin(order, items):
    """
    Gửi email báo admin có đơn hàng mới (ngay khi khách đặt)
    Trả về True nếu gửi thành công, False nếu lỗi.
    """
    admin_email = "hthanh1412004@gmail.com"

    if not admin_email:
        print("ADMIN_EMAIL not set")
        return False

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

        if 200 <= getattr(response, "status_code", 0) < 300:
            print("New order admin mail sent:", response.status_code)
            return True
        else:
            print("New order admin mail non-2xx:", getattr(response, "status_code", None))
            return False

    except Exception as e:
        print("NEW ORDER ADMIN MAIL ERROR:", e)
        return False