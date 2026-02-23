# shop_flower/services/vietqr.py
from io import BytesIO
import base64
import qrcode

# ---------- helper TLV ----------
def tlv(id_str: str, value: str) -> str:
    """Build TLV element where id_str is 2-digit string, length is 2-digit decimal."""
    b = value.encode("utf-8")
    length = len(b)
    if length > 99:
        raise ValueError("TLV value too long (>99 bytes)")
    return f"{id_str}{length:02d}{value}"

# ---------- CRC16-CCITT (X25 / CCITT-FALSE) ----------
def crc16_ccitt(data: bytes, poly: int = 0x1021, init: int = 0xFFFF) -> int:
    crc = init
    for b in data:
        crc ^= (b << 8)
        for _ in range(8):
            if (crc & 0x8000):
                crc = ((crc << 1) & 0xFFFF) ^ poly
            else:
                crc = (crc << 1) & 0xFFFF
    return crc & 0xFFFF

# ---------- Build VietQR payload ----------
def build_vietqr_payload(account_number: str,
                         bank_bin: str,
                         beneficiary_name: str,
                         amount_vnd: int = None,
                         reference: str = None,
                         bank_gui: str = "A000000727",
                         merchant_city: str = "HANOI",
                         merchant_name: str = None) -> str:
    """
    Build an EMVCo-style VietQR payload suited for many VN banking apps.
    - account_number: string of account (no spaces)
    - bank_bin: 6-digit BIN code for the bank (e.g. "970436")
    - beneficiary_name: beneficiary display name
    - amount_vnd: integer VND amount (e.g. 150000)
    - reference: order reference like "DH123"
    - bank_gui: default A000000727 (NAPAS-like)
    Returns payload string WITHOUT CRC (CRC appended later).
    """

    # basic validations
    if not bank_bin or not bank_bin.isdigit():
        raise ValueError("bank_bin (BIN) is required and must be numeric (e.g. '970436')")
    if not account_number:
        raise ValueError("account_number is required")

    # 00 Payload format indicator
    payload = tlv("00", "01")
    # 01 Point of initiation method: '11' static, '12' dynamic — use '12' (dynamic-like)
    payload += tlv("01", "12")

    # 26 Merchant Account Information (sub-TLVs)
    mai = ""
    mai += tlv("00", bank_gui)                      # GUI / RID
    identifier = f"{bank_bin}{account_number}"      # BIN + account (no separator)
    mai += tlv("01", identifier)
    if merchant_name:
        mai += tlv("02", merchant_name[:25])
    payload += tlv("26", mai)

    # 52 Merchant Category Code (use "0000" if unknown)
    payload += tlv("52", "0000")
    # 53 Transaction currency (704 = VND)
    payload += tlv("53", "704")
    # 54 Transaction amount (optional) — use integer form (no decimals)
    if amount_vnd is not None:
        payload += tlv("54", str(int(amount_vnd)))
    # 58 Country code
    payload += tlv("58", "VN")
    # 59 Merchant name (max 25)
    payload += tlv("59", (merchant_name or beneficiary_name)[:25])
    # 60 Merchant city (max 15)
    payload += tlv("60", merchant_city[:15])

    # 62 Additional Data Field Template (sub-TLV 01 often used for reference)
    if reference:
        add = tlv("01", str(reference))
        payload += tlv("62", add)

    # CRC (63) appended outside
    return payload

def finalize_payload_with_crc(payload_without_crc: str) -> str:
    # append CRC placeholder '63' + '04' then compute CRC on bytes
    crc_input = (payload_without_crc + "6304").encode("utf-8")
    crc_value = crc16_ccitt(crc_input)
    crc_hex = f"{crc_value:04X}"
    return payload_without_crc + tlv("63", crc_hex)

def generate_vietqr_data_uri(account_number: str,
                             bank_bin: str,
                             beneficiary_name: str,
                             amount_vnd: int = None,
                             reference: str = None,
                             bank_gui: str = "A000000727",
                             merchant_city: str = "HANOI",
                             merchant_name: str = None,
                             box_size: int = 8,
                             border: int = 2) -> dict:
    """
    Returns {"payload": "<EMV string>", "qr_data_uri": "data:image/png;base64,..."}
    """
    payload = build_vietqr_payload(
        account_number=account_number,
        bank_bin=bank_bin,
        beneficiary_name=beneficiary_name,
        amount_vnd=amount_vnd,
        reference=reference,
        bank_gui=bank_gui,
        merchant_city=merchant_city,
        merchant_name=merchant_name,
    )
    final = finalize_payload_with_crc(payload)

    qr = qrcode.QRCode(version=None, box_size=box_size, border=border,
                       error_correction=qrcode.constants.ERROR_CORRECT_Q)
    qr.add_data(final)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    data_uri = f"data:image/png;base64,{img_b64}"

    return {"payload": final, "qr_data_uri": data_uri}