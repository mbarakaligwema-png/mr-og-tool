import urllib.request
import urllib.parse
import ssl
import json

def test_verify():
    url = "https://mrogtool.com/api/v1/verify"
    print(f"Testing Verify Endpoint...")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    data = urllib.parse.urlencode({
        "username": "non_existent_user_xyz",
        "password": "somepassword",
        "hwid": "somehwid",
        "version": "1.7.0"
    }).encode()
    
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            print(f"Status: {response.getcode()}")
            print(f"Body: {response.read().decode()}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print(f"Body: {e.read().decode()}")
    except Exception as e:
        print(f"Error: {e}")

test_verify()
