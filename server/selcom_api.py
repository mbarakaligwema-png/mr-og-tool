import os
import json
import base64
import requests
import datetime
import uuid

# Selcom Environment Variables
SELCOM_BASE_URL = os.getenv("SELCOM_BASE_URL", "https://apigw.selcommobile.com")
SELCOM_VENDOR = os.getenv("SELCOM_VENDOR", "VENDOR_CODE")
SELCOM_API_KEY = os.getenv("SELCOM_API_KEY", "API_KEY")
SELCOM_API_SECRET = os.getenv("SELCOM_API_SECRET", "API_SECRET")

def initiate_ussd_push(phone_number: str, amount_tzs: int, order_id: str, email: str = ""):
    """
    Submits a USSD Push request to Selcom standard API.
    Returns the JSON response from Selcom.
    """
    endpoint = f"{SELCOM_BASE_URL}/v1/checkout/create-order-minimal"
    
    # Generate timestamp and auth config depending on your Selcom API version
    # Most Selcom v1 APIs use an Authorization header with base64
    auth_string = f"{SELCOM_API_KEY}:{SELCOM_API_SECRET}"
    encoded_auth = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
    
    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Clean the phone number (assuming 255 format)
    # If the user provides 07..., change it to 2557...
    if phone_number.startswith("0"):
        phone_number = "255" + phone_number[1:]
    elif phone_number.startswith("+"):
        phone_number = phone_number[1:]
        
    payload = {
        "vendor": SELCOM_VENDOR,
        "order_id": order_id,
        "buyer_email": email or "support@mrogtool.com",
        "buyer_name": "MR OG TOOL USER",
        "buyer_phone": phone_number,
        "amount": amount_tzs,
        "currency": "TZS",
        "payment_methods": "ALL"
        # Selcom normally returns a URL, or triggers push depending on the payment method code specified
    }
    
    try:
        # Note: Depending on Selcom's exact environment, we might catch the response or return a mock for now
        # response = requests.post(endpoint, json=payload, headers=headers, timeout=15)
        # return response.json()
        
        # MOCK SUCCESS FOR NOW UNTIL WE SET REAL KEYS
        print(f"Mocking Selcom Call: {payload}")
        return {
            "result": "SUCCESS",
            "message": "Push sent successfully",
            "order_id": order_id,
            "status": "PENDING_PAYMENT"
        }
    except Exception as e:
        return {"result": "FAIL", "message": str(e)}

