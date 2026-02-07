
import qrcode
from PIL import Image
import os
import json

print("Generating REAL QR Code with User Payload...")

# CUSTOM USER PAYLOAD
qr_data = {
    "android.app.extra.PROVISIONING_ADMIN_EXTRAS_BUNDLE": {},
    "android.app.extra.PROVISIONING_DEVICE_ADMIN_COMPONENT_NAME": "com.skamdm.knox/com.skamdm.knox.AdminReceiver",
    "android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_CHECKSUM": "9HpyskSThzfZ1QB2t3VM9vC2SP3v71auDyScIbnvmB0=",
    "android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_DOWNLOAD_LOCATION": "https://api.mdmfile.com/anonyshudb.apk",
    "android.app.extra.PROVISIONING_LEAVE_ALL_SYSTEM_APPS_ENABLED": True,
    "android.app.extra.PROVISIONING_SKIP_ENCRYPTION": True
}

json_str = json.dumps(qr_data, separators=(',', ':'))
print(f"Payload: {json_str}")

try:
    path = r"C:\Users\mbara\Documents\MR_OG_TOOL\assets\temp_zte_qr.png"
    if os.path.exists(path):
        try: os.remove(path)
        except: pass
        
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(json_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(path)
    
    if os.path.exists(path):
        print(f"SUCCESS: Created QR Code at {path}")
        # Try to open it
        os.startfile(path)
    else:
        print("FAIL: File not found.")

except Exception as e:
    print(f"ERROR: {e}")
