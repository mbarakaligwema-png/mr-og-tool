import urllib.request
import json
import ssl
import sys

# Load URL from config
try:
    with open("config.json", "r") as f:
        config = json.load(f)
        # 1. Get Server URL
    # server_url = config.get("server_url", "https://mrogtool.com")
    
    # HARDCODED TEST
    server_url = "https://mrogtool.com"
except:
    server_url = "https://mrogtool.com"

print(f"Target Server: {server_url}")

url = f"{server_url}/api/v1/verify"
data = {
    "username": "admin", # Admin should exist
    "password": "admin",
    "hwid": "DEBUG_TEST_HWID"
}

import urllib.parse

print("Sending request (Form Data)...")
try:
    # Use standard form encoding
    data_encoded = urllib.parse.urlencode(data).encode("utf-8")
    # No json header, standard form
    req = urllib.request.Request(url, data=data_encoded)
    
    # Bypass SSL for testing if needed
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    with urllib.request.urlopen(req, context=ctx) as response:
        result = response.read().decode()
        print("\n--- RAW SERVER RESPONSE ---")
        print(result)
        
        parsed = json.loads(result)
        if "expiry" in parsed:
            print(f"\n[PASS] Expiry field found: {parsed['expiry']}")
        else:
            print("\n[FAIL] 'expiry' field MISSING in response! Server code is likely OLD.")

    with urllib.request.urlopen(server_url, context=ctx) as response:
        home_html = response.read().decode()
        if "(UPDATED)" in home_html:
            print("\n[INFO] Home Page: FOUND '(UPDATED)' string. -> Version is OLD (approx step 426).")
        else:
            print("\n[INFO] Home Page: '(UPDATED)' string NOT found. -> Version is NEWER (approx step 481+).")

except Exception as e:
    print(f"\n[ERROR] Request failed: {e}")
