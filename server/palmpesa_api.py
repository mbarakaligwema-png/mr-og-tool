import os
import httpx
import time

# PalmPesa Environment Variables
PALMPESA_BASE_URL = os.getenv("PALMPESA_BASE_URL", "https://api.palmpay.com/v1")
PALMPESA_MERCHANT_ID = os.getenv("PALMPESA_MERCHANT_ID", "487")
PALMPESA_APP_ID = os.getenv("PALMPESA_APP_ID", "487")
PALMPESA_API_KEY = os.getenv("PALMPESA_API_KEY", "uzczuHsDoFwPyQlJAyS3nBSzp2JSIxkrrXUR8opop9591mY6Qsfiklkh2M0q")

def initiate_ussd_push(phone_number: str, amount_tzs: int, order_id: str):
    """
    Submits a USSD Push request to PalmPesa.
    """
    # Clean the phone number (ensure 255 format)
    if phone_number.startswith("0"):
        phone_number = "255" + phone_number[1:]
    elif phone_number.startswith("+"):
        phone_number = phone_number[1:]

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {PALMPESA_API_KEY}",
        "userId": str(PALMPESA_MERCHANT_ID),
    }

    # Payload - PalmPesa/PalmPay MoMo endpoint
    payload = {
        "merchantId": PALMPESA_MERCHANT_ID,
        "appId": PALMPESA_APP_ID,
        "userId": PALMPESA_MERCHANT_ID,
        "orderId": order_id,
        "amount": str(amount_tzs),
        "currency": "TZS",
        "phone": phone_number,
        "mobileNumber": phone_number,
        "description": "MR OG TOOL License",
        "notifyUrl": "https://mrogtool.com/api/palmpesa/webhook",
        "returnUrl": "https://mrogtool.com/dashboard",
        "timestamp": str(int(time.time() * 1000))
    }

    # Try multiple known PalmPesa endpoints
    endpoints = [
        f"{PALMPESA_BASE_URL}/payment/momo/create-order",
        f"{PALMPESA_BASE_URL}/checkout/create",
        "https://api.palmpay.co.tz/v1/payment/momo",
        "https://palmpesa.tz/api/v1/checkout/create-order",
    ]

    last_error = ""
    for endpoint in endpoints:
        try:
            print(f"[PalmPesa] Trying endpoint: {endpoint}")
            print(f"[PalmPesa] Payload: {payload}")

            with httpx.Client(timeout=20.0) as client:
                response = client.post(endpoint, json=payload, headers=headers)

            print(f"[PalmPesa] Status: {response.status_code}")
            print(f"[PalmPesa] Response: {response.text}")

            if response.status_code in [200, 201]:
                data = response.json()
                # PalmPay returns different fields depending on version
                result_code = data.get("resultCode") or data.get("code") or data.get("result")
                if result_code in ["00000", "SUCCESS", "200", "0", 0, "PENDING"]:
                    return {"result": "SUCCESS", "message": "Push sent via PalmPesa", "order_id": order_id, "data": data}
                else:
                    last_error = data.get("resultMessage") or data.get("message") or str(data)
                    continue
            else:
                last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                continue

        except Exception as e:
            last_error = str(e)
            continue

    return {"result": "FAIL", "message": f"PalmPesa API Error: {last_error}"}
