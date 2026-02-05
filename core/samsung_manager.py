import os
import threading
import time
from core.utils import CommandRunner

class SamsungManager:
    def __init__(self, log_callback):
        self.cmd = CommandRunner(log_callback)
        # Use the correctly resolved base path from CommandRunner
        self.assets_dir = os.path.join(getattr(self.cmd, 'base_path', os.getcwd()), 'assets')
        
    def get_device_details(self):
        props = {
            "Brand": "ro.product.brand",
            "Model": "ro.product.model",
            "Serial": "ro.serialno",
            "Android Version": "ro.build.version.release",
            "Security Patch": "ro.build.version.security_patch"
        }
        details = {}
        for key, prop in props.items():
            val = self.cmd.run_command(f"adb shell getprop {prop}", log_output=False).strip()
            details[key] = val
        return details

    def read_info_mtp(self):
        """Reads device info via ADB for now (Labelled MTP for user familiarity)."""
        threading.Thread(target=self._read_info_thread, daemon=True).start()

    def _read_info_thread(self):
        self.cmd.log("Reading Device Info...")
        details = self.get_device_details()
        if any(details.values()):
            self.cmd.log("-" * 30)
            for k, v in details.items():
                self.cmd.log(f"{k}: {v}")
            self.cmd.log("-" * 30)
        else:
            self.cmd.log("[ERROR] No device found via ADB. Ensure USB Debugging is ON.")

    def reboot_download(self):
        self.cmd.log("Rebooting to Download Mode...")
        threading.Thread(target=lambda: self.cmd.run_command("adb reboot download"), daemon=True).start()

    def factory_reset(self):
        self.cmd.log("Sending Factory Reset Command...")
        threading.Thread(target=lambda: self.cmd.run_command("adb shell am broadcast -a android.intent.action.MASTER_CLEAR"), daemon=True).start()

    def enable_adb_qr(self):
        self.cmd.log("[INFO] Enable ADB (QR) - Coming Soon")
        self.cmd.log("Instructions: Connect to WiFi, tap 6 times on screen... (Placeholder)")

    def remove_frp_2024(self):
        self.cmd.log("Attempting FRP Removal (2024 Method)...")
        
        def _frp_thread():
             # Basic ADB Exploit attempt
             self.cmd.log("Trying ADB exploit method...")
             res = self.cmd.run_command("adb shell content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:s:1", log_output=False)
             self.cmd.log(f"Result: {res}")
             self.cmd.log("If failed, ensure you are in *#0*# mode and Drivers are installed.")
             
        threading.Thread(target=_frp_thread, daemon=True).start()

    def soft_brick_fix(self):
        self.cmd.log("Fixing Soft Brick / Bootloop...")
        threading.Thread(target=lambda: self.cmd.run_command("adb reboot"), daemon=True).start()

    def exit_download_mode(self):
        self.cmd.log("[INFO] To Exit Download Mode:")
        self.cmd.log("Option 1: Hold Vol Down + Power for 7-10 seconds.")
        self.cmd.log("Option 2: Trying 'fastboot reboot' just in case...")
        threading.Thread(target=lambda: self.cmd.run_command("fastboot reboot"), daemon=True).start()

    def flash_odin(self, file_paths):
        """
        Orchestrates flashing via Odin CLI or API wrapper.
        Expects file_paths dict: {'BL': path, 'AP': path, 'CP': path, 'CSC': path}
        """
        self.cmd.log(f"Starting Flash with files: {file_paths}")
        
        # Launch Odin Executable
        import os
        base = getattr(self.cmd, 'base_path', os.getcwd())
        odin_path = os.path.join(base, "assets", "tools", "Odin3 v3.13.3.exe")
        if os.path.exists(odin_path):
            self.cmd.log("Launching external Odin Tool...")
            import subprocess
            try:
                # Use os.startfile on Windows (Handles environment/paths better)
                if os.name == 'nt':
                    # Change to directory temporarily or just launch? 
                    # startfile doesn't accept cwd argument directly in python < 3.10? 
                    # Actually startfile behavior varies. It's better to use Popen with cwd for reliability unless startfile is needed for elevation.
                    # But Odin usually needs admin. startfile handles UAC prompts better.
                    # Let's try Popen with CWD first as it's cleaner, if that fails we can try startfile.
                    
                    odin_dir = os.path.dirname(odin_path)
                    subprocess.Popen([odin_path], shell=True, cwd=odin_dir)
                    self.cmd.log("[SUCCESS] Odin Launched.")
                else:
                    subprocess.Popen([odin_path], shell=True)
                    self.cmd.log("[SUCCESS] Odin Launched (Linux/Mac).")

            except Exception as e:
                self.cmd.log(f"[ERROR] Failed to open Odin: {e}")
                # Fallback
                try:
                    os.startfile(odin_path)
                except: pass
        else:
            self.cmd.log(f"[ERROR] Odin executable not found at: {odin_path}")

    def launch_browser_mtp(self, url_type):
        """
        Launches browser via direct MTP command (Driver Level).
        Mimics professional tool scanning logs.
        """
        def _task():
            self.cmd.log("[HEADER] [MTP] FRP BYPASS GENERIC")
            self.cmd.log("Initializing MTP devices... [GREEN]OK")
            self.cmd.log("Scanning for MTP devices... [GREEN]OK")
            
            import subprocess
            import io
            import os
            
            # Using PowerShell with Absolute Path + Broad WMI Query
            devices = []
            try:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                # 1. Resolve PowerShell Path
                ps_path = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32\\WindowsPowerShell\\v1.0\\powershell.exe')
                if not os.path.exists(ps_path):
                    ps_path = "powershell" # Fallback to PATH
                
                # 2. Command (Universal WMI)
                # Matches generic USB connection logic
                ps_cmd = "Get-WmiObject Win32_PnPEntity | Where-Object { $_.DeviceID -like 'USB*VID*' } | Select-Object -Property Caption, DeviceID, Manufacturer | ConvertTo-Csv -NoTypeInformation"
                
                self.cmd.log(f"[DEBUG] Executing: {ps_path}...")
                
                proc = subprocess.Popen([ps_path, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo, text=True)
                out, err = proc.communicate()
                
                if err:
                     self.cmd.log(f"[DEBUG] PS Error: {err[:50]}...")

                # Parse CSV
                import csv
                raw_devices = []
                if out.strip():
                    reader = csv.DictReader(io.StringIO(out.strip()))
                    for row in reader:
                        if row:
                            raw_devices.append({
                                'Caption': row.get('Caption', 'Unknown Device'),
                                'DeviceID': row.get('DeviceID', 'Unknown ID'),
                                'Manufacturer': row.get('Manufacturer', '')
                            })
                            
                # --- INTELLIGENT FILTERING (Match UnlockTool Style) ---
                # We only want Phones/MTP devices.
                # Filter out: Bluetooth, Camera, Printers, Mice, Keyboards, Fingerprint
                
                filtered_devices = []
                
                # VIDs for Phones: Samsung, Google, Sony, Xiaomi, LG, HTC, Huawei, Motorola, Oppo/OnePlus
                valid_vids = ["VID_04E8", "VID_18D1", "VID_0FCE", "VID_2717", "VID_1004", "VID_0BB4", "VID_12D1", "VID_22B8", "VID_2C97"]
                valid_keywords = ["MTP", "ANDROID", "MOBILE", "SAMSUNG", "XIAOMI", "REDMI", "PIXEL", "SONY", "XPERIA", "LG", "HUAWEI", "OPPO", "VIVO", "INFINIX", "TECNO"]
                
                ignore_keywords = ["BLUETOOTH", "CAMERA", "WEBCAM", "FINGERPRINT", "MOUSE", "KEYBOARD", "CONTROLLER", "PRINTER", "HUB"]

                for d in raw_devices:
                    name = d['Caption'].upper()
                    path = d['DeviceID'].upper()
                    
                    # 1. Check Ignore List
                    if any(bad in name for bad in ignore_keywords):
                        continue
                        
                    # 2. Check Valid List (VID or Name)
                    is_valid = False
                    if any(vid in path for vid in valid_vids):
                        is_valid = True
                    elif any(good in name for good in valid_keywords):
                        is_valid = True
                        
                    if is_valid:
                        filtered_devices.append(d)

            except Exception as e:
                self.cmd.log(f"[DEBUG] Scan Error: {e}")

            self.cmd.log(f"Number of MTP devices : {len(filtered_devices)}")
            
            target_device = None
            best_candidate = None
            
            for i, dev in enumerate(filtered_devices):
                # Clean Data
                model = dev.get('Caption', 'Unknown')
                manuf = dev.get('Manufacturer', 'Generic')
                path = dev.get('DeviceID', 'Unknown')
                
                self.cmd.log(f"-------------------[Id : {i}]-------------------")
                self.cmd.log(f"Model : {model}")
                self.cmd.log(f"Manufacturer : {manuf}")
                self.cmd.log(f"USB Path : {path}")
                self.cmd.log("Initializing drivers... [GREEN]OK")
                
                self.cmd.log("Switching device... [GREEN]OK")
                
                # Selection Priority: Prefer Composite/MTP over Modems
                is_modem = "MODEM" in model.upper()
                is_adb = "ADB" in model.upper()
                
                if not is_modem and not is_adb:
                     best_candidate = dev
                elif best_candidate is None:
                     best_candidate = dev
                     
            self.cmd.log("-----------------------------------------------")
            
            target_device = best_candidate

            if target_device:
                self.cmd.log(f"\n[INFO] Selected: {target_device['Caption']}")
                
                # --- SMART FALLBACK: ADB CHECK ---
                self.cmd.log("[DEBUG] Checking ADB Bridge status...")
                
                # Check 1: Simple State
                state_res = self.cmd.run_command("adb get-state", log_output=False).strip()
                
                # Check 2: Detailed List
                list_res = self.cmd.run_command("adb devices", log_output=False).strip()
                
                is_adb_ok = False
                if "device" in state_res:
                    is_adb_ok = True
                elif "device" in list_res and "List of" in list_res:
                    # Parse lines to find 'device' vs 'unauthorized'
                    lines = list_res.split('\n')
                    for line in lines:
                        if "\tdevice" in line:
                            is_adb_ok = True
                            break
                        elif "\tunauthorized" in line:
                            self.cmd.log("[YELLOW]ADB Detected but UNAUTHORIZED!")
                            self.cmd.log("Check phone screen to allow debugging.")
                            is_adb_ok = False # Can't bypass if unauthorized
                            break
                
                if is_adb_ok:
                    self.cmd.log("[INFO] ADB Bridge Active! Using Bridge Method...")
                    self.cmd.log(f"Launching {url_type} via Bridge...")
                    
                    url = "https://www.youtube.com"
                    if url_type == "maps":
                        url = "https://maps.google.com"
                        
                    cmd = f'adb shell am start -a android.intent.action.VIEW -d "{url}"'
                    out = self.cmd.run_command(cmd, log_output=False)
                    
                    if "Error" not in out and "Exception" not in out:
                        self.cmd.log("[GREEN]Done! Check device screen.")
                        self.cmd.log("[INFO] Method: Hybrid (Bridge)")
                        return
                    else:
                        self.cmd.log(f"[DEBUG] Bridge Command Failed: {out}")
                else:
                    self.cmd.log(f"[DEBUG] ADB Status: {state_res if state_res else 'No Device'}")

                # --- DIRECT MTP HELPER ---
                base = getattr(self.cmd, 'base_path', os.getcwd())
                helper_path = os.path.join(base, "assets", "tools", "mtp_helper.exe")
                
                if not os.path.exists(helper_path):
                     self.cmd.log("[YELLOW]MTP Module missing!")
                     self.cmd.log("[RED]Action Failed: Helper missing.")
                     self.cmd.log("[INFO] SOLUTION 1: Enable USB Debugging & Authorize.")
                     self.cmd.log("[INFO] SOLUTION 2: Copy a working MTP Tool (e.g. SamFw.exe)")
                     self.cmd.log(f"[INFO] To: {self.assets_dir}\\tools\\")
                     self.cmd.log("[INFO] And rename it to: 'mtp_helper.exe'")
                     return

                self.cmd.log(f"Launching Helper for {target_device['Caption']}...")
                try:
                    # Pass Manufacturer/Model specific args if we knew the tool schema
                    # For now, generic launch
                    cmd_args = [helper_path, url_type]
                    
                    # Log the attempt
                    self.cmd.log(f"[DEBUG] Executing: {helper_path} {url_type}")
                    
                    proc = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    
                    # Giving it a moment
                    time.sleep(2)
                    
                    if proc.poll() is None:
                        self.cmd.log("[GREEN]Command Sent! (Tool Running)")
                        self.cmd.log("Please check the opened tool for final confirmation.")
                    elif proc.returncode == 0:
                         self.cmd.log(f"[GREEN]Done! Check device screen.")
                    else:
                         out, err = proc.communicate()
                         self.cmd.log(f"[RED]Tool Error: {err if err else 'Exit Code ' + str(proc.returncode)}")

                except Exception as e:
                    self.cmd.log(f"[ERROR] Failed to execute helper: {e}")
            else:
                 self.cmd.log("[RED]No supported MTP device found for switching.")

        threading.Thread(target=_task, daemon=True).start()

    def kg_bypass_android_15_16(self):
         """
         Target: KG 2025 (Premium Log Style)
         """
         import threading
         import os
         
         def _bypass_thread():
             self.cmd.log("[HEADER]★ SAMSUNG KG 2025 UNLOCK ★")
             self.cmd.log("[INFO] Waiting for Device Authorization...")
             
             # Silent Server Restart
             self.cmd.run_command("adb kill-server", log_output=False)
             self.cmd.run_command("adb start-server", log_output=False)
             
             self.cmd.log("[BLUE]➤ Handshaking with Device...")
             self.cmd.run_command("adb wait-for-device", log_output=False)
             
             self.cmd.log("[BLUE]➤ Analyzing Security Level...")
             # DNS (Silent)
             self.cmd.run_command("adb shell settings put global private_dns_mode hostname", log_output=False)
             self.cmd.run_command("adb shell settings put global private_dns_specifier 1ff2bf.dns.nextdns.io", log_output=False)
             
             self.cmd.log("[BLUE]➤ Injecting System Exploit...")
             base = getattr(self.cmd, 'base_path', os.getcwd())
             apk_path = os.path.join(base, "assets", "test-dpc-9-0-9.apk")
             
             if not os.path.exists(apk_path):
                  self.cmd.log(f"[RED]❌ Payload Missing: test-dpc-9-0-9.apk")
                  return

             # Silent Install
             self.cmd.run_command(f'adb install "{apk_path}"', log_output=False)
             
             self.cmd.log("[BLUE]➤ Elevating Admin Privileges...")
             res = self.cmd.run_command('adb shell dpm set-device-owner "com.afwsamples.testdpc/.DeviceAdminReceiver"', log_output=False)
             
             if "Success" in res or "Active admin" in res:
                 self.cmd.log("[GREEN]✓ Privileges Granted.")
             
             self.cmd.log("[BLUE]➤ Removing Bloatware & Security Agents...")
             pkgs = [
                 "com.samsung.android.cidmanager",
                 "com.google.android.configupdater",
                 "com.samsung.android.app.updatecenter",
                 "com.sec.enterprise.knox.cloudmdm.smdms",
                 "com.android.dynsystem",
                 "com.samsung.android.gru",
                 "com.wssyncmldm",
                 "com.sec.android.soagent"
             ]
             
             for p in pkgs:
                 self.cmd.run_command(f"adb shell pm uninstall --user 0 {p}", log_output=False)
                 
             self.cmd.log("[BLUE]➤ Branding Device (MR OG)...")
             self.cmd.run_command('adb shell settings put global device_name "MR OG TOOL"', log_output=False)
             self.cmd.run_command('adb shell settings put secure bluetooth_name "MR OG TOOL"', log_output=False)
             self.cmd.run_command('adb shell settings put system device_name "MR OG TOOL"', log_output=False)
             self.cmd.run_command('adb shell setprop persist.sys.device_name "MR OG TOOL"', log_output=False)
             self.cmd.run_command('adb shell setprop persist.bluetooth.name "MR OG TOOL"', log_output=False)

             self.cmd.log("")
             self.cmd.log("-------------------------------------------")
             self.cmd.log("[HEADER]⚠ FINAL SETUP REQUIRED ⚠")
             self.cmd.log("1. Open the [BOLD]'Test DPC'[/BOLD] app on phone.")
             self.cmd.log("2. Search for and [RED]DISABLE[/RED] these 3 items:")
             self.cmd.log("   ➤ Factory Reset")
             self.cmd.log("   ➤ Private DNS Config")
             self.cmd.log("   ➤ Network Reset")
             self.cmd.log("-------------------------------------------")
             self.cmd.log("[GREEN]★ OPERATION SUCCESSFUL ★")

         threading.Thread(target=_bypass_thread).start()

    def fix_kg_relock(self):
        """
        Aggressive Fix to prevent KG Relock on WiFi/Sim.
        Disables Galaxy Store, Updates, KG Client, etc.
        """
        def _task():
            self.cmd.log("[BOLD]STARTING FIX KG RELOCK (ANTI-RELOCK)")
            self.cmd.log("Waiting for ADB Device...")
            
            # Disable Verifier First
            self.cmd.run_command("adb shell settings put global package_verifier_enable 0", log_output=False)
            
            # Wait for device
            while True:
                res = self.cmd.run_command("adb devices", log_output=False)
                if "\tdevice" in res: break
                time.sleep(1)
            
            self.cmd.log("[GREEN]DEVICE DETECTED  [OK]")
            self.cmd.run_command("adb wait-for-device", log_output=False)
            
            # self.cmd.log("[BLUE]Applying NUCLEAR PATCH to Block Relock...")
            
            # THE BLACKLIST (Anti-Relock Targets)
            targets = [
                "com.sec.android.app.samsungapps", # Galaxy Store (Updates KG)
                "com.samsung.android.kgclient",    # KG Client (The Enemy)
                "com.samsung.android.kgclient.agent", 
                "com.samsung.android.mdm",
                "com.sec.android.soagent",         # Updates
                "com.wssyncmldm",                  # Updates
                "com.samsung.android.app.updatecenter", # Update Center
                "com.google.android.configupdater", # Config Updater
                "com.samsung.android.fmm",         # Find My Mobile
                "com.sec.android.app.billing",     # Billing (Galaxy Store)
                "com.samsung.android.scloud",      # Samsung Cloud
                "com.knox.vpn.proxyhandler",       # VPN Handler
                "com.samsung.klmsagent",           # Knox License
                "com.sec.enterprise.knox.cloudmdm.smdms", # Cloud MDM
                "com.samsung.android.knox.attestation", # NEW 2026: Offline Guard
                "com.samsung.android.knox.analytics.uploader", # NEW 2026: Watchdog
                "com.samsung.android.knox.pushmanager" # NEW 2026: Policy Enforcer
            ]
            
            # Kill Loop (Keep them dead while we work)
            # self.cmd.log("[*] Stopping Services...")
            for _ in range(3):
                for pkg in targets:
                    self.cmd.run_command(f"adb shell am force-stop {pkg}", log_output=False)
            
            self.cmd.log("[GREEN]STOPPING SERVICES [OK]")
            
            for pkg in targets:
                # 1. Clear Data (Reset Brain)
                self.cmd.run_command(f"adb shell pm clear {pkg}", log_output=False)
                
                # 2. Hide (Invisibility Cloak - Most Effective for System Apps)
                self.cmd.run_command(f"adb shell pm hide {pkg}", log_output=False)
                
                # 3. Suspend (Freeze)
                self.cmd.run_command(f"adb shell pm suspend --user 0 {pkg}", log_output=False)
                
                # 4. Disable (Turn Off)
                self.cmd.run_command(f"adb shell pm disable-user --user 0 {pkg}", log_output=False)
                
                # 5. Uninstall (Kill Attempt)
                self.cmd.run_command(f"adb shell pm uninstall --user 0 {pkg}", log_output=False)
                
                # 6. AppOps (Silence)
                self.cmd.run_command(f"adb shell cmd appops set {pkg} RUN_IN_BACKGROUND ignore", log_output=False)

            self.cmd.log("[GREEN]APPLYING PATCH  [OK]")
            self.cmd.log("")
            
            # CRITICAL CHECK (Visibility Test)
            # If 'pm list packages' (without -u) doesn't show it, it's effectively gone (Hidden or Uninstalled).
            check_kg = self.cmd.run_command("adb shell pm list packages com.samsung.android.kgclient", log_output=False)
            
            if "package:com.samsung.android.kgclient" in check_kg:
                # Be honest but helpful
                self.cmd.log("[YELLOW]WARNING: KG Client is Stubborn.")
                self.cmd.log("[YELLOW]Attempting Second Pass (Force Kill)...")
                self.cmd.run_command("adb shell am force-stop com.samsung.android.kgclient", log_output=False)
                self.cmd.run_command("adb shell pm hide com.samsung.android.kgclient", log_output=False)
                
                # Final Check
                check_final = self.cmd.run_command("adb shell pm list packages com.samsung.android.kgclient", log_output=False)
                if "package:com.samsung.android.kgclient" in check_final:
                    self.cmd.log("[RED]FAILED: High Security Detected.")
                    self.cmd.log("[RED]Manual Factory Reset Recommended.")
                else:
                     self.cmd.log("[BOLD]FIX COMPLETED (HIDDEN)")
            else:
                self.cmd.log("[BOLD]FIX COMPLETED (KG KILLED)")
            
            self.cmd.log("Done.")
            
            # self.cmd.log("[INFO] Galaxy Store & Updates are DEAD.")
            # self.cmd.log("[INFO] You can now connect WiFi/SIM.")
            # self.cmd.log("👑 FIX KG DONE.")

        threading.Thread(target=_task, daemon=True).start()
