import os
import httpx
import time

# PalmPesa Environment Variables
# Base URL ya kweli ni: https://palmpesa.drmlelwa.co.tz
PALMPESA_BASE_URL = os.getenv("PALMPESA_BASE_URL", "https://palmpesa.drmlelwa.co.tz")
PALMPESA_MERCHANT_ID = os.getenv("PALMPESA_MERCHANT_ID", "487")
PALMPESA_APP_ID = os.getenv("PALMPESA_APP_ID", "487")
PALMPESA_API_KEY = os.getenv("PALMPESA_API_KEY", "uzczuHsDoFwPyQlJAyS3nBSzp2JSIxkrrXUR8opop9591mY6Qsfiklkh2M0q")

def initiate_ussd_push(phone_number: str, amount_tzs: int, order_id: str):
    """
    Submits a USSD Push request to PalmPesa (palmpesa.drmlelwa.co.tz).
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
        "X-User-ID": str(PALMPESA_MERCHANT_ID),
        "X-Api-Token": PALMPESA_API_KEY,
    }

    # Payload for PalmPesa (drmlelwa)
    payload = {
        "user_id": PALMPESA_MERCHANT_ID,
        "api_token": PALMPESA_API_KEY,
        "order_id": order_id,
        "amount": str(amount_tzs),
        "currency": "TZS",
        "phone": phone_number,
        "phone_number": phone_number,
        "description": "MR OG TOOL License",
        "notify_url": "https://mrogtool.com/api/palmpesa/webhook",
        "callback_url": "https://mrogtool.com/api/palmpesa/webhook",
        "return_url": "https://mrogtool.com/dashboard",
        "reference": order_id,
    }

    # Try all known PalmPesa endpoint patterns
    endpoints = [
        f"{PALMPESA_BASE_URL}/api/payment/ussd-push",
        f"{PALMPESA_BASE_URL}/api/payment/create",
        f"{PALMPESA_BASE_URL}/api/checkout/create",
        f"{PALMPESA_BASE_URL}/api/v1/payment",
        f"{PALMPESA_BASE_URL}/api/pay",
        f"{PALMPESA_BASE_URL}/api/transaction",
    ]

    last_error = ""
    for endpoint in endpoints:
        try:
            print(f"[PalmPesa] Trying: {endpoint}")
            with httpx.Client(timeout=15.0, verify=True) as client:
                response = client.post(endpoint, json=payload, headers=headers)

            print(f"[PalmPesa] Status: {response.status_code}, Response: {response.text[:300]}")

            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    # Check for success indicators
                    result_code = (
                        data.get("resultCode") or
                        data.get("code") or
                        data.get("status") or
                        data.get("result") or
                        data.get("success")
                    )
                    if result_code in ["00000", "SUCCESS", "200", "0", 0, "PENDING", "success", True, 1, "1"]:
                        return {"result": "SUCCESS", "message": "Push sent via PalmPesa. Confirm with PIN.", "order_id": order_id}
                    else:
                        last_error = data.get("message") or data.get("resultMessage") or str(data)
                except Exception:
                    last_error = response.text[:200]
            elif response.status_code == 404:
                last_error = f"Endpoint not found: {endpoint}"
                continue
            else:
                last_error = f"HTTP {response.status_code}: {response.text[:200]}"

        except Exception as e:
            last_error = str(e)
            print(f"[PalmPesa] Error on {endpoint}: {e}")
            continue

    return {"result": "FAIL", "message": f"PalmPesa: {last_error}"}
