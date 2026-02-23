import requests
from django.conf import settings
import urllib.parse

VIETQR_API = "https://api.vietqr.io/v2/generate"


def generate_vietqr(order):
    """
    Trả về:
    {
        "qr_code": base64,
        "qr_data_url": image url,
        "payload": raw
    }
    """

    payload = {
        "accountNo": settings.VIETQR_ACCOUNT_NO,
        "accountName": settings.VIETQR_ACCOUNT_NAME,
        "acqId": settings.VIETQR_BANK_BIN,
        "amount": int(order.total_amount),
        "addInfo": f"DH{order.id}",
        "format": "text",
    }

    headers = {
        "Content-Type": "application/json",
        "x-client-id": settings.VIETQR_CLIENT_ID,
        "x-api-key": settings.VIETQR_API_KEY,
    }

    response = requests.post(VIETQR_API, json=payload, headers=headers, timeout=15)

    if response.status_code != 200:
        raise Exception(f"VietQR API error: {response.text}")

    data = response.json()

    if data.get("code") != "00":
        raise Exception(f"VietQR failed: {data}")

    return data["data"]

def generate_vietqr_image_url(order):
    """
    Return VietQR image URL (no need to generate QR locally)
    """

    amount = int(order.total_amount)
    add_info = f"DH{order.id}"

    account_name = urllib.parse.quote(settings.VIETQR_ACCOUNT_NAME)

    url = (
        f"https://img.vietqr.io/image/"
        f"{settings.VIETQR_BANK_BIN}-{settings.VIETQR_ACCOUNT_NO}-compact2.png"
        f"?amount={amount}"
        f"&addInfo={add_info}"
        f"&accountName={account_name}"
    )

    return url