import qrcode
import json
import hashlib
import base64
import os

# 1. Calculate Checksum for THE NEW APK (mrog_bypass_v2.apk which is a copy of anonyshudb.apk)
apk_path = os.path.join("assets", "mrog_bypass_v2.apk")
if not os.path.exists(apk_path):
    print(f"Error: {apk_path} not found!")
    exit(1)

print("Calculating checksum...")
sha = hashlib.sha256()
with open(apk_path, 'rb') as f:
    while True:
        data = f.read(65536)
        if not data: break
        sha.update(data)
checksum = base64.urlsafe_b64encode(sha.digest()).decode().strip('=')
print(f"Checksum: {checksum}")

# 2. Prepare JSON Data
# User JSON provided:
# {"android.app.extra.PROVISIONING_ADMIN_EXTRAS_BUNDLE":{},
#  "android.app.extra.PROVISIONING_DEVICE_ADMIN_COMPONENT_NAME":"com.skamdm.knox/com.skamdm.knox.AdminReceiver",
#  "android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_CHECKSUM":"9HpyskSThzfZ1QB2t3VM9vC2SP3v71auDyScIbnvmB0=",
#  "android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_DOWNLOAD_LOCATION":"https://api.mdmfile.com/anonyshudb.apk", ...}

# WE UPDATE THE URL AND NAMES, BUT KEEP INTERNAL COMPONENT NAME (Cannot change without recompile)

qr_data = {
    "android.app.extra.PROVISIONING_ADMIN_EXTRAS_BUNDLE": {},
    "android.app.extra.PROVISIONING_DEVICE_ADMIN_COMPONENT_NAME": "com.skamdm.knox/com.skamdm.knox.AdminReceiver",
    "android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_CHECKSUM": checksum,
    "android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_DOWNLOAD_LOCATION": "https://mrogtool.com/downloads/mrog_bypass_v2.apk",
    "android.app.extra.PROVISIONING_LEAVE_ALL_SYSTEM_APPS_ENABLED": True,
    "android.app.extra.PROVISIONING_SKIP_ENCRYPTION": True
}

json_str = json.dumps(qr_data, separators=(',', ':'))
print(f"JSON Data: {json_str}")

# 3. Generate QR Image
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(json_str)
qr.make(fit=True)

output_path = os.path.join("assets", "zte_qr.png")
img = qr.make_image(fill_color="black", back_color="white")
img.save(output_path)
print(f"QR Code successfully saved to {output_path}")
print(f"NOTE: Please ensure 'mrog_bypass_v2.apk' is uploaded to https://mrogtool.com/downloads/mrog_bypass_v2.apk")
