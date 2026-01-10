import urllib.request
    
url = "https://mr-og-tool.onrender.com/"
print(f"Checking: {url}")
    
try:
    with urllib.request.urlopen(url) as response:
        content = response.read().decode()
        if "mediafire" in content.lower():
            print("SUCCESS: MediaFire link found on Home Page!")
        else:
            print("FAILURE: MediaFire link NOT found.")
            
except Exception as e:
    print(f"Error: {e}")
