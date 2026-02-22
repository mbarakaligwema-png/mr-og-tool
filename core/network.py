import urllib.request
import urllib.parse
import urllib.error
import socket
import json
import ssl

def check_internet_connection(host="8.8.8.8", port=53, timeout=3):
    """
    Check if there is an active internet connection by connecting to Google DNS.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


def verify_server_access(server_url):
    """
    Verify server is reachable.
    """
    try:
        if not server_url:
            return False
        
        # Determine strictness.
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        # Add User-Agent to avoid being blocked by WAF/Firewalls
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        req = urllib.request.Request(server_url, headers=headers)
        # Low timeout to avoid hanging startup
        with urllib.request.urlopen(req, timeout=8, context=ctx) as response:
            # Check for 200 OK
            if response.getcode() == 200:
                return True
            return False

    except Exception as e:
        print(f"Server Check Error: {e}")
        return False

def verify_user_license(server_url, username, password, hwid):
    """
    Call API to verify user.
    Returns: (is_allowed: bool, message: str)
    """
    api_url = f"{server_url.rstrip('/')}/api/v1/verify"
    data = urllib.parse.urlencode({
        "username": username,
        "password": password,
        "hwid": hwid,
        "version": "1.7.1"
    }).encode()
    
    # Create SSL Context to ignore verification
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        req = urllib.request.Request(api_url, data=data, headers=headers, method="POST") 
        with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
            if response.getcode() == 200:
                raw_response = response.read().decode()
                try:
                    body = json.loads(raw_response)
                except json.JSONDecodeError:
                    return False, "Server Parsing Error: Invalid JSON received."

                if body.get("status") == "OK":
                    if body.get("update_required", False):
                         return False, "UPDATE REQUIRED: Download new version from website."
                    expiry = body.get("expiry", "Unknown")
                    return True, f"Expires: {expiry}"
                else:
                    return False, body.get("message", "Access Denied")
            else:
                return False, f"Server HTTP {response.getcode()}"
                
    except urllib.error.HTTPError as e:
        # FastAPI returns 403/404 for blocks, read body
        try:
            body = json.loads(e.read().decode())
            return False, body.get("message", "Access Denied")
        except:
             return False, f"Server Error: {e.code}"
    except Exception as e:
        return False, f"Connection Failed: {str(e)}"
