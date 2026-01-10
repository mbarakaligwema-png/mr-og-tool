import sys
import os

# Add current directory to path so we can import core
sys.path.append(os.getcwd())

from core.network import check_internet_connection, verify_server_access

def test_checks():
    print("Testing Internet Connection...")
    if check_internet_connection():
        print("PASS: Internet Connection Detected")
    else:
        print("FAIL: No Internet (Ensure you are connected)")

    print("\nTesting Server Verification (Valid URL)...")
    if verify_server_access("https://www.google.com"):
        print("PASS: Server Verified")
    else:
        print("FAIL: Server Verification Failed")
        
    print("\nTesting Server Verification (Invalid URL)...")
    if not verify_server_access("http://invalid-url-that-does-not-exist.com"):
        print("PASS: Server Verification Correctly Failed for Invalid URL")
    else:
        print("FAIL: Server Verification Passed for Invalid URL")

if __name__ == "__main__":
    test_checks()
