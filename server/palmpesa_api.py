import os
import json
import httpx
import time
import hashlib
import hmac
from datetime import datetime

# PalmPesa / PalmPay Environment Variables
PALMPESA_BASE_URL = os.getenv("PALMPESA_BASE_URL", "https://api.palmpay.com/v1")
PALMPESA_MERCHANT_ID = os.getenv("PALMPESA_MERCHANT_ID", "487") 
PALMPESA_APP_ID = os.getenv("PALMPESA_APP_ID", "")           # We need this from you
PALMPESA_API_KEY = os.getenv("PALMPESA_API_KEY", "uzczuHsDoFwPyQlJAyS3nBSzp2JSIxkrrXUR8opop9591mY6Qsfiklkh2M0q")

def generate_signature(payload: dict, secret: str):
    """
    Generates a signature for PalmPay. 
    Usually involves sorting keys and hashing with the secret.
    """
    sorted_payload = sorted(payload.items())
    query_string = "&".join(f"{k}={v}" for k, v in sorted_payload if v)
    return hmac.new(secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

def initiate_ussd_push(phone_number: str, amount_tzs: int, order_id: str):
    """
    Submits a USSD Push request to PalmPesa (PalmPay).
    """
    endpoint = f"{PALMPESA_BASE_URL}/payment/momo/create-order"
    
    # Clean the phone number (assuming 255 format)
    if phone_number.startswith("0"):
        phone_number = "255" + phone_number[1:]
    elif phone_number.startswith("+"):
        phone_number = phone_number[1:]

    payload = {
        "merchantId": PALMPESA_MERCHANT_ID,
        "appId": PALMPESA_APP_ID,
        "orderId": order_id,
        "amount": str(amount_tzs),
        "currency": "TZS",
        "phone": phone_number,
        "description": "MR OG TOOL Access",
        "timestamp": str(int(time.time() * 1000))
    }
    
    # PalmPay usually requires a signature
    # signature = generate_signature(payload, PALMPESA_API_KEY)
    # payload["signature"] = signature

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {PALMPESA_API_KEY}" # Some use Bearer, some use signature
    }

    try:
        # For now, let's mock it until we confirm the exact payload structure
        print(f"Initiating PalmPesa Push: {payload}")
        
        # Real call would be:
        # with httpx.Client() as client:
        #     response = client.post(endpoint, json=payload, headers=headers)
        #     return response.json()
        
        return {
            "result": "SUCCESS",
            "message": "Push sent via PalmPesa",
            "order_id": order_id,
            "status": "PENDING"
        }
    except Exception as e:
        return {"result": "FAIL", "message": str(e)}
