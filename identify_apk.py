import os
import subprocess
import time

def run_adb(cmd):
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        res = subprocess.run(cmd, capture_output=True, text=True, startupinfo=startupinfo)
        return res.stdout
    except Exception as e:
        return str(e)

def get_packages():
    out = run_adb(["adb", "shell", "pm", "list", "packages", "-3"])
    pkgs = set()
    for line in out.splitlines():
        if "package:" in line:
            pkgs.add(line.strip().split(":")[1])
    return pkgs

print("Reading existing packages...")
before = get_packages()
print(f"Found {len(before)} packages.")

apk_path = os.path.abspath("assets/mrog_admin_v1.apk")
print(f"Installing {apk_path}...")

# Push and install
run_adb(["adb", "push", apk_path, "/data/local/tmp/temp.apk"])
res = run_adb(["adb", "shell", "pm", "install", "-t", "-g", "/data/local/tmp/temp.apk"])
print(f"Install Result: {res}")
run_adb(["adb", "shell", "rm", "/data/local/tmp/temp.apk"])

print("Reading new packages...")
after = get_packages()

new_pkgs = after - before
if new_pkgs:
    pkg = list(new_pkgs)[0]
    print(f"DETECTED PACKAGE NAME: {pkg}")
    
    # Try to find receivers
    print("Finding Receivers...")
    # This is tricky with plain adb, but we can try dumping package
    dump = run_adb(["adb", "shell", "dumpsys", "package", pkg])
    import re
    # Look for receiver that handles DEVICE_ADMIN
    # or just any receiver
    receivers = re.findall(r'Receiver.*\{(.*)\}', dump)
    for r in receivers:
        print(f"Receiver Found: {r}")
        if pkg in r:
           short_name = r.split(" ")[1] # Usually u0 com.pkg/.Receiver
           print(f"Candidate: {short_name}")
           
    # Simpler regex for component
    # Format usually: ComponentInfo{com.package/com.package.Class}
    
else:
    print("No new package detected! Is it already installed?")
    # Try to guess if 'mrog' or 'admin' is in 'after'
    for p in after:
        if "mrog" in p or "admin" in p or "bypass" in p:
            print(f"Potential existing candidate: {p}")
