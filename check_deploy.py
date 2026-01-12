import urllib.request
import json
import ssl

print("Checking Deployment Status...")
url = "https://mrogtool.com/health"
print(f"Checking: {url}")

try:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    with urllib.request.urlopen(url, context=ctx) as response:
        data = json.loads(response.read().decode())
        print(f"Server Version: {data.get('version', 'UNKNOWN')}")
        
except Exception as e:
    print(f"Error: {e}")
