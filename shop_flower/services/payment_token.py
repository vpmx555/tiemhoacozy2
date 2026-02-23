from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

signer = TimestampSigner()

def generate_payment_token(order_id):
    return signer.sign(order_id)

def verify_payment_token(token, max_age=86400):  # 24h
    try:
        order_id = signer.unsign(token, max_age=max_age)
        return order_id
    except (BadSignature, SignatureExpired):
        return None