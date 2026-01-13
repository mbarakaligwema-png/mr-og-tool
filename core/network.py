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
        
        # Determine strictness. For now, just check if we can reach the home page.
        # We assume local server is HTTP. If HTTPS, context needed.
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        if "http://127.0.0.1" in server_url or "localhost" in server_url:
             req = urllib.request.Request(server_url)
             with urllib.request.urlopen(req, timeout=5) as response:
                return response.getcode() == 200
        else:
             # For production/google mock
             req = urllib.request.Request(server_url)
             with urllib.request.urlopen(req, timeout=5, context=ctx) as response:
                return response.getcode() == 200

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
        "hwid": hwid
    }).encode()
    
    try:
        req = urllib.request.Request(api_url, data=data, method="POST") 
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.getcode() == 200:
                body = json.loads(response.read().decode())
                if body.get("status") == "OK":
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
        return False, f"Connection Failed: {e}"
