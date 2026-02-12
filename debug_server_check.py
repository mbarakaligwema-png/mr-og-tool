
import sys
import os
sys.path.append(os.getcwd())
from core.network import verify_server_access

url = "https://mrogtool.com"
print(f"Testing URL: {url}")
result = verify_server_access(url)
print(f"Result: {result}")
