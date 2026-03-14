import os
import httpx
import time
import uuid

# PalmPesa Environment Variables
# Base URL: https://palmpesa.drmlelwa.co.tz
PALMPESA_BASE_URL = os.getenv("PALMPESA_BASE_URL", "https://palmpesa.drmlelwa.co.tz")
PALMPESA_MERCHANT_ID = os.getenv("PALMPESA_MERCHANT_ID", "487")
PALMPESA_API_KEY = os.getenv("PALMPESA_API_KEY", "uzczuHsDoFwPyQlJAyS3nBSzp2JSIxkrrXUR8opop9591mY6Qsfiklkh2M0q")

def initiate_ussd_push(phone_number: str, amount_tzs: int, order_id: str, buyer_name: str = "MR OG USER", buyer_email: str = ""):
    """
    Submits a USSD Push request to PalmPesa.
    Endpoint: POST https://palmpesa.drmlelwa.co.tz/api/pay-via-mobile
    
    Required payload (from official PalmPesa docs):
    {
        "user_id": "string",
        "name": "string",
        "email": "string",
        "phone": "255XXXXXXXXX",
        "amount": 500,
        "transaction_id": "unique_id",
        "address": "string",
        "postcode": "string",
        "buyer_uuid": "string"
    }
    """
    # Clean the phone number (ensure 255 format)
    if phone_number.startswith("0"):
        phone_number = "255" + phone_number[1:]
    elif phone_number.startswith("+"):
        phone_number = phone_number[1:]

    # PalmPesa requires at least 2 words for the name
    if buyer_name and len(buyer_name.split()) < 2:
        buyer_name = f"{buyer_name} Customer"
    elif not buyer_name:
        buyer_name = "MR OG Customer"

    endpoint = f"{PALMPESA_BASE_URL}/api/pay-via-mobile"

    headers = {
        "Authorization": f"Bearer {PALMPESA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "user_id": str(PALMPESA_MERCHANT_ID),
        "name": buyer_name,
        "email": buyer_email or "user@mrogtool.com",
        "phone": phone_number,
        "amount": amount_tzs,
        "transaction_id": order_id,
        "address": "Tanzania",
        "postcode": "00000",
        "buyer_uuid": str(PALMPESA_MERCHANT_ID),
    }

    try:
        print(f"[PalmPesa] Calling: {endpoint}")
        print(f"[PalmPesa] Payload: {payload}")

        with httpx.Client(timeout=20.0) as client:
            response = client.post(endpoint, json=payload, headers=headers)

        print(f"[PalmPesa] Status: {response.status_code}")
        print(f"[PalmPesa] Response: {response.text[:500]}")

        if response.status_code in [200, 201]:
            data = response.json()
            # PalmPesa returns: {"message": "Payment request sent to user's phone"}
            msg = data.get("message", "")
            if "sent" in msg.lower() or "success" in msg.lower() or "payment" in msg.lower():
                return {"result": "SUCCESS", "message": "Push sent to your phone. Please enter your PIN to confirm payment!", "order_id": order_id}
            else:
                return {"result": "FAIL", "message": data.get("message") or str(data)}
        else:
            return {"result": "FAIL", "message": f"HTTP {response.status_code}: {response.text[:200]}"}

    except Exception as e:
        print(f"[PalmPesa] Exception: {e}")
        return {"result": "FAIL", "message": str(e)}
