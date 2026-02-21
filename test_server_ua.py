import urllib.request
import ssl
import json

def test_ua(ua=None):
    url = "https://mrogtool.com/health"
    print(f"Testing with UA: {ua}")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    headers = {}
    if ua:
        headers["User-Agent"] = ua
        
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            print(f"Status: {response.getcode()}")
            print(f"Body: {response.read().decode()}")
    except Exception as e:
        print(f"Error: {e}")

print("--- Test 1: Default UA ---")
test_ua()

print("\n--- Test 2: Chrome UA ---")
test_ua("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
