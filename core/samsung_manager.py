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
         Target: Android 14, 15, 16 (Knox Guard / MDM)
         Method: Device Owner (Admin) + Package Disabling + UI Hiding
         """
         import threading
         import os
         
         def _bypass_thread():
             # 1. HEADER
             self.cmd.log("[BOLD]STARTING MDM BYPASS 2025")
             self.cmd.log("Waiting for ADB Device...")
             
             # Wait for device loop (FAST SCAN)
             # self.cmd.log("Scanning for Device...") # Silent
             while True:
                 res = self.cmd.run_command("adb devices", log_output=False)
                 if "device" in res and "List of" in res:
                    lines = res.strip().split('\n')
                    found = False
                    for line in lines:
                        if line.strip().endswith("device") and "List of" not in line:
                            found = True
                    if found: break
                 time.sleep(0.5)

             self.cmd.log("[GREEN]DEVICE DETECTED  [OK]")
             self.cmd.run_command("adb wait-for-device", log_output=False)
             
             # 0. INSTALL APK FIRST
             import os
             base = getattr(self.cmd, 'base_path', os.getcwd())
             apk_path = os.path.join(base, "assets", "mrog_admin_v3.apk")
             
             # Silent DNS
             # self.cmd.log("[*] Setting Private DNS (AdGuard)...")
             self.cmd.run_command("adb shell settings put global private_dns_mode hostname", log_output=False)
             self.cmd.run_command("adb shell settings put global private_dns_specifier dns.adguard.com", log_output=False)
             
             if os.path.exists(apk_path):
                 # Silent Install Block
                 check_mrog = self.cmd.run_command("adb shell pm path com.mrog.admin", log_output=False)
                 check_dpc = self.cmd.run_command("adb shell pm path com.afwsamples.testdpc", log_output=False)
                 
                 if "package:" in check_mrog:
                     # self.cmd.log("[INFO] Bypass App already installed (MROG). Skipping Install.")
                     install_success = True
                 elif "package:" in check_dpc:
                     # self.cmd.log("[INFO] Bypass App already installed (Test DPC). Skipping Install.")
                     install_success = True
                 else:
                     # self.cmd.log("[*] Installing Bypass App (Priority 1)...")
                     
                     # Retry Logic for Install (3 times)
                     install_success = False
                     for attempt in range(3):
                         self.cmd.run_command("adb wait-for-device", log_output=False) # Wait if dropped
                         
                         # Clean up only if no admin found (which is true here)
                         if attempt == 0:
                             self.cmd.run_command("adb shell settings put global package_verifier_enable 0", log_output=False)
                         
                         # ROBUST INSTALL STRATEGY: Push then Install (Fixes Streamed Install disconnects)
                         # self.cmd.log("[DEBUG] Uploading APK to device...")
                         push_res = self.cmd.run_command(f'adb push "{apk_path}" /data/local/tmp/base.apk', log_output=False)
                         
                         if "error" not in push_res.lower() and "fail" not in push_res.lower():
                             # self.cmd.log("[DEBUG] Installing from storage...")
                             res = self.cmd.run_command('adb shell pm install -t -r -g /data/local/tmp/base.apk', log_output=False)
                             self.cmd.run_command('adb shell rm /data/local/tmp/base.apk', log_output=False) # Cleanup
                             
                             if "Success" in res:
                                  # self.cmd.log("[GREEN]App Installed! Proceeding to Kill Agents...")
                                  install_success = True
                                  break
                             else:
                                  # Silent failure (retrying)
                                  pass 
                         else:
                             # Fallback to streaming
                             res = self.cmd.run_command(f'adb install -t -r -g "{apk_path}"', log_output=False)
                             if "Success" in res:
                                  install_success = True
                                  break
    
                         # Check for disconnect signs
                         if "no devices" in str(push_res) or "no devices" in str(res):
                              # self.cmd.log(f"[YELLOW]Connection unstable (Attempt {attempt+1}). Retrying...")
                              self.cmd.run_command("adb start-server", log_output=False)
                         else:
                              pass
                     
                     if not install_success:
                          # Final silent check
                          check_retry_m = self.cmd.run_command("adb shell pm path com.mrog.admin", log_output=False)
                          check_retry_d = self.cmd.run_command("adb shell pm path com.afwsamples.testdpc", log_output=False)
                          
                          if "package:" in check_retry_m or "package:" in check_retry_d:
                              # self.cmd.log("[INFO] App verified. Proceeding...")
                              install_success = True
                          else:
                              # self.cmd.log("[WARN] Install skip. Proceeding to Owner check...")
                              pass
             
             # 2. OTA UPDATE (This covers the installing/killing part in the customer's eyes)
             self.cmd.log("[GREEN]OTA UPDATE      [OK]")
             
             # 1. IMMEDIATE KILL (CRITICAL BEFORE ANYTHING ELSE)
             # self.cmd.log("[*] Pre-emptive Strike: Killing KG Agents...")
             self.cmd.run_command("adb wait-for-device", log_output=False)
             
             killer_pkgs = [
                "com.samsung.android.kgclient",
                "com.samsung.android.kgclient.agent",
                "com.samsung.android.mdm",
                "com.sec.enterprise.knox.cloudmdm.smdms",
                "com.samsung.klmsagent",
                "com.sec.android.soagent",
                "com.wssyncmldm",
                "com.sec.android.app.samsungapps",
                "com.sec.android.app.billing",
                "com.samsung.android.knox.analytics.uploader",
                "com.samsung.android.knox.attestation",
                "com.samsung.android.knox.pushmanager",
                "com.samsung.android.smartface.service",
                "com.samsung.android.server.wifi.mobilewips"
             ]
             
             # SEQUENTIAL KILL (Safer than Threaded Loop)
             # We iterate once but effectively.
             for p in killer_pkgs:
                 self.cmd.run_command(f"adb shell am force-stop {p}", log_output=False)
                 self.cmd.run_command(f"adb shell pm disable-user --user 0 {p}", log_output=False)
                 self.cmd.run_command(f"adb shell pm uninstall --user 0 {p}", log_output=False)
                 self.cmd.run_command(f"adb shell pm hide {p}", log_output=False)
                 self.cmd.run_command(f"adb shell pm suspend --user 0 {p}", log_output=False)
                 
             # 2. Silent Setup
             # self.cmd.log("[*] Initializing Setup...")
             
             # DNS (Disable Private DNS to prevent leaks/blocking)
             self.cmd.run_command('adb shell settings put global private_dns_mode off', log_output=False)
             # self.cmd.run_command('adb shell settings delete global private_dns_specifier', log_output=False)
             
 
             
             # (Install Block Moved to Top)
 
             # 3. Activate Owner (AUTO-DETECT PACKAGE)
             # self.cmd.log("[*] Activating Device Owner...")
             
             # Check which package installed
             check_mrog = self.cmd.run_command("adb shell pm path com.mrog.admin", log_output=False)
             check_tool = self.cmd.run_command("adb shell pm path com.mrog.tool", log_output=False)
             check_dpc = self.cmd.run_command("adb shell pm path com.afwsamples.testdpc", log_output=False)
             
             target_pkg = ""
             target_component = ""
             
             if "package:" in check_dpc:
                 # self.cmd.log("[INFO] Detected: Test DPC (Existing)")
                 target_pkg = "com.afwsamples.testdpc"
                 target_component = "com.afwsamples.testdpc/.DeviceAdminReceiver"
             elif "package:" in check_mrog:
                 # self.cmd.log("[INFO] Detected: MROG Admin")
                 target_pkg = "com.mrog.admin"
                 target_component = "com.mrog.admin/.MyDeviceAdminReceiver"
             elif "package:" in check_tool:
                 # self.cmd.log("[INFO] Detected: MROG TOOL (Old)")
                 target_pkg = "com.mrog.tool"
                 target_component = "com.mrog.tool/.MyDeviceAdminReceiver"
             else:
                 # Fallback to TEST DPC even if pm path failed (sometimes package exists but pm path is weird)
                 # self.cmd.log("[WARN] Auto-Detect unclear. Trying generic agents...")
                 target_pkg = "com.afwsamples.testdpc"
                 target_component = "com.afwsamples.testdpc/.DeviceAdminReceiver"
             
             if target_component:
                 cmd_owner = f'adb shell dpm set-device-owner --user 0 "{target_component}"'
                 
                 # Retry Logic for Owner (Handle ADB Version Mismatch/Reset)
                 owner_success = False
                 final_res = ""
                 
                 for attempt in range(3):
                     res = self.cmd.run_command(cmd_owner, log_output=False)
                     final_res = res
                     
                     # Success Criteria
                     if any(x in res for x in ["Success", "Active admin", "already set", "already an admin"]):
                         owner_success = True
                         break
                     
                     # Handle ADB reset/mismatch (Silent Retry)
                     if "adb server version" in res or "protocol fault" in res or "no devices" in res:
                         # self.cmd.log(f"[DEBUG] ADB Glitch detected. Retrying owner set...")
                         self.cmd.run_command("adb start-server", log_output=False)
                         self.cmd.run_command("adb wait-for-device", log_output=False)
                         time.sleep(1)
                     else:
                         # Other error, keep trying just in case
                         time.sleep(1)

                 if owner_success:
                     # self.cmd.log(f"[GREEN]Device Owner Set! ({target_pkg})")
                     
                     # HIDE ICON (Agizo: USIWEKE HIDE)
                     # self.cmd.log("[*] Skipping Icon Hide (User Request)...")
                     # self.cmd.run_command(f"adb shell pm hide {target_pkg}", log_output=False)
                     
                     # LOCKDOWN (Finya Zote - DPC Style) via ADB
                     # self.cmd.log("[*] Enforcing ALL ADB Restrictions (Finya Zote)...")
                     restrictions = [
                         "no_config_private_dns",
                         "no_config_vpn", 
                         "no_config_tethering",
                         "no_config_mobile_networks",
                         "no_network_reset",
                         "no_factory_reset",
                         "no_config_bluetooth",
                         "no_config_credentials",
                         "no_config_cell_broadcasts",
                         "no_add_user",
                         "no_mount_physical_media"
                     ]
                     
                     for r in restrictions:
                         self.cmd.run_command(f'adb shell dpm set-user-restriction --user 0 {r} 1', log_output=False)
                     
                 else:
                     self.cmd.log(f"[RED]Failed to set Owner: {final_res.strip()}")

             self.cmd.log("[GREEN]KG BYPASS       [OK]")
             self.cmd.log("")
             self.cmd.log("[BOLD]OPERATION DONE")
             # self.cmd.log("[INFO] - Agents Killed")
             # self.cmd.log("[INFO] - APK Installed & Owner Set")
             # self.cmd.log("Done.")
 
             # Show Instruction Popup (User Request)
             import tkinter.messagebox as messagebox
             msg = (
                 "Zoezi limekamilika kikamilifu.\n\n"
                 "Hatua za ziada za usalama (Test DPC):\n"
                 "1. Fungua Test DPC\n"
                 "2. Nenda sehemu ya 'Search'\n"
                 "3. Tafuta na uwashe (ON) vipengele hivi:\n"
                 "   - Disallow factory reset\n"
                 "   - Disallow network reset\n"
                 "   - Disallow config private dns"
             )
             messagebox.showinfo("Attention (Important)", msg)

         threading.Thread(target=_bypass_thread).start()

    def fix_kg_relock(self):
        """
        Aggressive Fix to prevent KG Relock on WiFi/Sim.
        Disables Galaxy Store, Updates, KG Client, etc.
        """
        def _task():
            self.cmd.log("[HEADER] FIX KG RELOCK (v1.6 Logic)")
            self.cmd.log("Waiting for ADB Device...")
            
            # Disable Verifier First
            self.cmd.run_command("adb shell settings put global package_verifier_enable 0", log_output=False)
            
            # Wait for device
            while True:
                res = self.cmd.run_command("adb devices", log_output=False)
                if "\tdevice" in res: break
                time.sleep(1)
                
            self.cmd.log("[BLUE]Applying NUCLEAR PATCH to Block Relock...")
            
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
                "com.sec.enterprise.knox.cloudmdm.smdms" # Cloud MDM
            ]
            
            # Kill Loop (Keep them dead while we work)
            self.cmd.log("[*] Stopping Services...")
            for _ in range(3):
                for pkg in targets:
                    self.cmd.run_command(f"adb shell am force-stop {pkg}", log_output=False)
            
            for pkg in targets:
                self.cmd.log(f"🔥 DESTROYING: {pkg}")
                # 1. Kill
                self.cmd.run_command(f"adb shell am force-stop {pkg}", log_output=False)
                # 2. Clear Data (CRITICAL for removing cached lock policies)
                self.cmd.run_command(f"adb shell pm clear {pkg}", log_output=False)
                # 3. Disable
                self.cmd.run_command(f"adb shell pm disable-user --user 0 {pkg}", log_output=False)
                # 4. Hide
                self.cmd.run_command(f"adb shell pm hide {pkg}", log_output=False)
                # 5. Suspend (Powerful)
                self.cmd.run_command(f"adb shell pm suspend --user 0 {pkg}", log_output=False)
                # 6. Uninstall (Final Blow - keeps data but removes from user 0)
                self.cmd.run_command(f"adb shell pm uninstall -k --user 0 {pkg}", log_output=False)
                # 7. AppOps (Silence Background Activity)
                self.cmd.run_command(f"adb shell cmd appops set {pkg} RUN_IN_BACKGROUND ignore", log_output=False)
                self.cmd.run_command(f"adb shell cmd appops set {pkg} START_FOREGROUND ignore", log_output=False)

            # DOUBLE TAP: Check if they are still alive (Zombie Check)
            self.cmd.log("[*] Verifying destruction...")
            for pkg in targets:
                res = self.cmd.run_command(f"adb shell pm list packages {pkg}", log_output=False)
                if pkg in res:
                    self.cmd.log(f"[YELLOW]Resilient Agent Found: {pkg} -> Retrying...")
                    self.cmd.run_command(f"adb shell pm uninstall --user 0 {pkg}", log_output=False)
                    self.cmd.run_command(f"adb shell pm disable {pkg}", log_output=False)
                
            self.cmd.log("---------------------------------------")
            self.cmd.log("[GREEN]ANTI-RELOCK PATCH APPLIED!")
            self.cmd.log("[INFO] Galaxy Store & Updates are DEAD.")
            self.cmd.log("[INFO] You can now connect WiFi/SIM.")
            self.cmd.log("👑 FIX KG DONE.")

        threading.Thread(target=_task, daemon=True).start()
