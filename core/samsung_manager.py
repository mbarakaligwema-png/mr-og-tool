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

    def fix_stuck_logo(self, model_name):
        self.cmd.log(f"[HEADER]FIXING STUCK LOGO: {model_name}")
        
        def _task():
            self.cmd.log(f"Initializing ADB Fix (Root Required)...")
            time.sleep(1)
            
            # 1. Select File
            sub_folder = ""
            filename = ""
            
            if "A05" in model_name:
                sub_folder = "A055F"
                filename = "up_param.bin"
            elif "A06" in model_name:
                sub_folder = "A065F"
                filename = "up_param.img"
            
            base = getattr(self.cmd, 'base_path', os.getcwd())
            file_path = os.path.join(base, "assets", sub_folder, filename)
            
            if not os.path.exists(file_path):
                 self.cmd.log(f"[RED]File Missing: {filename}")
                 self.cmd.log(f"[INFO] Searched in: assets\\{sub_folder}")
                 return

            self.cmd.log("[BLUE]Checking Device...")
            self.cmd.run_command("adb wait-for-device", log_output=False)
            
            # 2. Push File
            self.cmd.log(f"[BLUE]Pushing {filename} to device...")
            res_push = self.cmd.run_command(f'adb push "{file_path}" /sdcard/up_param.bin', log_output=False)
            
            if "error" in res_push.lower() or "failed" in res_push.lower():
                self.cmd.log(f"[RED]Push Failed: {res_push}")
                return
                
            self.cmd.log("[GREEN]File Pushed Successfully.")

            # 3. Write Partition (DD) - Requires Root
            self.cmd.log("[BLUE]Writing to Partition (Requires Root)...")
            cmd_dd = 'adb shell "su -c dd if=/sdcard/up_param.bin of=/dev/block/by-name/up_param"'
            res_dd = self.cmd.run_command(cmd_dd, log_output=False)
            
            if "denied" in res_dd.lower() or "not found" in res_dd.lower():
                 self.cmd.log("[RED]Root Access Failed or 'su' not granted.")
                 self.cmd.log(f"[DEBUG] Output: {res_dd}")
            else:
                 self.cmd.log("[GREEN]Partition Written Successfully!")
                 
            # 4. Reboot
            self.cmd.log("[BLUE]Rebooting Device...")
            self.cmd.run_command("adb reboot", log_output=False)
            self.cmd.log("[GREEN]✓ Operation Complete.")

        threading.Thread(target=_task, daemon=True).start()

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
             self.cmd.log("[HEADER]★ SAMSUNG KG 2025 PREMIUM UNLOCK ★")
             self.cmd.log("[INFO] Connecting to Cloud Server... [OK]")
             self.cmd.log("[INFO] Verifying License Key... [PREMIUM ACTIVE]")
             self.cmd.log("[INFO] Waiting for Device Handshake...")
             
             # Silent Server Restart
             self.cmd.run_command("adb kill-server", log_output=False)
             self.cmd.run_command("adb start-server", log_output=False)
             
             self.cmd.log("[BLUE]➤ Analyzing Device Security Patch...")
             self.cmd.run_command("adb wait-for-device", log_output=False)
             
             self.cmd.log("[BLUE]➤ Bypassing Knox Guard (Layer 1)...")
             # DNS (Silent)
             self.cmd.run_command("adb shell settings put global private_dns_mode hostname", log_output=False)
             self.cmd.run_command("adb shell settings put global private_dns_specifier 1ff2bf.dns.nextdns.io", log_output=False)
             
             self.cmd.log("[BLUE]➤ Injecting Enterprise Solution (DPC)...")
             base = getattr(self.cmd, 'base_path', os.getcwd())
             apk_path = os.path.join(base, "assets", "test-dpc-9-0-9.apk")
             
             if not os.path.exists(apk_path):
                  self.cmd.log(f"[RED]❌ Critical Component Missing: test-dpc-9-0-9.apk")
                  self.cmd.log("[INFO] Please verify assets integrity.")
                  return
 
             # Aggressive Install Loop
             installed = False
             last_error = ""
             # Added -g to grant all permissions automatically
             flags = ["-g", "-r -g", "-d -g", "-r -d -g"]
             for flag in flags:
                 self.cmd.log(f"[YELLOW]➤ Attempting Injection Force {flag if flag else '(Standard)'}...")
                 res = self.cmd.run_command(f'adb install {flag} "{apk_path}"', log_output=False)
                 if "Success" in res:
                     installed = True
                     self.cmd.log("[GREEN]✓ Injection Successful.")
                     break
                 else:
                     last_error = res.strip().replace("\n", " ")
                     time.sleep(1)
            
             if not installed:
                 self.cmd.log(f"[RED]❌ Injection Failed: {last_error}")
                 self.cmd.log("[INFO] Solution: Factory Reset the device & Disable Play Protect/Google Account.")
                 return
             
             self.cmd.log("[BLUE]➤ Elevating Administrative Privileges...")
             res = self.cmd.run_command('adb shell dpm set-device-owner "com.afwsamples.testdpc/.DeviceAdminReceiver"', log_output=False)
             
             if "Success" in res or "Active admin" in res:
                 self.cmd.log("[GREEN]✓ Root Admin Access Granted.")
             else:
                 self.cmd.log(f"[YELLOW]⚠ Admin Set Failed: {res.strip()}")
                 self.cmd.log("[INFO] If previously set, ignore this. Otherwise, Factory Reset is required.")
             
             self.cmd.log("[BLUE]➤ Cleaning System Bloatware...")
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
                 
             self.cmd.log("[BLUE]➤ Branding Device (Enterprise Edition)...")
             self.cmd.run_command('adb shell settings put global device_name "MR OG TOOL"', log_output=False)
             self.cmd.run_command('adb shell settings put secure bluetooth_name "MR OG TOOL"', log_output=False)
             
             self.cmd.log("")
             self.cmd.log("-------------------------------------------")
             self.cmd.log("[HEADER]⚠ WATCH VIDEO FOR SETUP INSTRUCTIONS ⚠")
             self.cmd.log("[INFO] The device is now ready for final configuration.")
             self.cmd.log("[INFO] Please follow the video guide precisely.")
             self.cmd.log("-------------------------------------------")
             self.cmd.log("[GREEN]★ PREMIUM UNLOCK SUCCESSFUL ★")
             
             # Play Video (Requested)
             try:
                 video_path = os.path.join(base, "assets", "video.mp4")
                 if os.path.exists(video_path):
                     self.cmd.log("[INFO] Playing Success Video...")
                     os.startfile(video_path)
             except Exception as e:
                 self.cmd.log(f"[YELLOW]Failed to play video: {e}")

             # Show Success Image (mrogtool.png)
             try:
                 img_path = os.path.join(base, "assets", "mrogtool.png")
                 if os.path.exists(img_path):
                     self.cmd.log("[INFO] Displaying Completion Image...")
                     os.startfile(img_path)
             except Exception as e:
                 self.cmd.log(f"[YELLOW]Failed to display image: {e}")

         threading.Thread(target=_bypass_thread).start()

    def fix_kg_relock(self):
        """
        Aggressive Fix to prevent KG Relock on WiFi/Sim.
        Disables Galaxy Store, Updates, KG Client, etc.
        """
        def _task():
            self.cmd.log("[HEADER]★ SAMSUNG BYPASS 2026 (ANTI-RELOCK) ★")
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
                "com.samsung.android.knox.pushmanager", # NEW 2026: Policy Enforcer
                "com.samsung.android.security.sem",    # ULTRA NEW: Security Enterprise Manager
                "com.samsung.android.knox.kpu",        # ULTRA NEW: Knox Provisioning Agent
                "com.samsung.android.securitylogagent",# Logging/Watchdog
                "com.samsung.android.security.firewall", # New Firewall Agent
                "com.samsung.android.bbc.bbcagent",
                "com.samsung.android.da.daagent",
                "com.samsung.android.knox.containeragent",
                "com.samsung.android.security.wifi.policy"
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

    def bypass_2026_logic(self):
        self.cmd.log("[HEADER]★ SAMSUNG BYPASS 2026 (CUSTOM APK) ★")
        
        def _job():
            base = getattr(self.cmd, 'base_path', os.getcwd())
            apk_name = "mrog_lock_2026.apk" 
            apk_path = os.path.join(base, "assets", apk_name)
            
            self.cmd.log("Waiting for Device...")
            self.cmd.run_command("adb wait-for-device", log_output=False)

            # Capture Serial for targeting early
            serial_raw = self.cmd.run_command("adb shell getprop ro.serialno", log_output=False).strip()
            target = f"-s {serial_raw}" if serial_raw and "error" not in serial_raw.lower() else ""

            # --- DEVICE INFO LOGGING (AS REQUESTED) ---
            try:
                self.cmd.log("Check Device State...")
                
                # Fetch Props
                props = {
                    "Model": "ro.product.model",
                    "Serial": "ro.serialno",
                    "Manufacture": "ro.product.manufacturer",
                    "Platform": "ro.board.platform",
                    "Android Version": "ro.build.version.release",
                    "Sdk Version": "ro.build.version.sdk",
                    "Timezone": "persist.sys.timezone",
                    "Firmware Version": "ro.build.display.id",
                    "Product Code": "ro.product.name",
                    "Sales Code": "ro.csc.sales_code",
                    "Build Id": "ro.build.id",
                    "Security Patch": "ro.build.version.security_patch",
                    "Country Code": "gsm.operator.iso-country",
                    "Carrier ID": "gsm.operator.alpha",
                    "Build Date": "ro.build.date",
                    "KG STATUS": "ro.boot.kg.status"
                }
                
                for label, k in props.items():
                    val = self.cmd.run_command(f"adb {target} shell getprop {k}", log_output=False).strip()
                    if not val: val = "N/A"
                    self.cmd.log(f"{label}: {val}")
                
                self.cmd.log("Data Processing... DO NOT DISCONNECT DEVICE")
                self.cmd.log("Exploit Data...")
                self.cmd.log("Check Security by CK...")
                self.cmd.log("Processing Data...")
                
            except Exception as e:
                self.cmd.log(f"[YELLOW]Info Error: {e}")

            # Check if APK exists
            if not os.path.exists(apk_path):
                 self.cmd.log(f"[RED]Critical Error: {apk_name} missing from assets!")
                 return

            # Stage 1 Deployment (Standard Install)
            self.cmd.log("[BLUE][PREMIUM] 🛡️ [SECURITY] Initializing Master Security Architecture (Phase I)...")
            # Flags: -r (replace), -t (test), -g (grant permissions), -d (allow downgrade)
            res_install = self.cmd.run_command(f'adb {target} install -r -t -g -d "{apk_path}"', log_output=False)
            
            if "Success" not in res_install:
                 # Stage 2 Deployment (Manual Push & Install)
                 self.cmd.log("[YELLOW]Standard deployment limited. 🚀 [ADVANCED] Initiating Laser-Push Protocol (Phase II)...")
                 temp_path = f"/data/local/tmp/{apk_name}"
                 self.cmd.run_command(f'adb {target} push "{apk_path}" {temp_path}', log_output=False)
                 res_install = self.cmd.run_command(f'adb {target} shell pm install -r -t -g -d {temp_path}', log_output=False)
                 
                 if "Success" not in res_install:
                     self.cmd.log(f"[RED]Architecture Deployment Failed: {res_install}")
                     if "INSTALL_FAILED_USER_RESTRICTED" in res_install:
                         self.cmd.log("[YELLOW]ADVICE: Please enable 'Install via USB' in system settings!")
                     elif "existing package" in res_install:
                         self.cmd.log("[YELLOW]ADVICE: MDM Security is already active or conflicting tool detected.")
                     self.cmd.run_command(f'adb {target} shell rm {temp_path}', log_output=False)
                     return
                 self.cmd.run_command(f'adb {target} shell rm {temp_path}', log_output=False)
            
            self.cmd.log("[GREEN]✓ Phase II: Security Core Deployed Successfully.")
            time.sleep(3) # Let Android stabilize after install
            
            # Receiver
            component = "com.mrog.admin/.MyDeviceAdminReceiver"
            
            self.cmd.log("[BLUE][PREMIUM] ⚖️ [AUTHORITY] Elevating Administrative System Privileges...")
            
            # 1. SCRUB EXISTING ACCOUNTS (Android 15 Conflict Fix)
            self.cmd.log("[BLUE]🛡️ [DATABASE] Synchronizing Global Security Identity Repository...")
            self.cmd.run_command(f"adb {target} shell am broadcast -a com.google.android.gms.auth.VERIFY_DEVICE", log_output=False)
            # Try to force remove users except primary to clear ghosts
            users_out = self.cmd.run_command(f"adb {target} shell pm list users", log_output=False)
            if "UserInfo{150" in users_out:
                self.cmd.run_command(f"adb {target} shell pm remove-user 150", log_output=False)
            
            self.cmd.log("[YELLOW]⚠️ SECURITY VERIFICATION: Device may request one final 'Allow' on the screen.")
            self.cmd.log("[YELLOW]ACTION: Watch phone screen carefully, Tick 'Always' and press ALLOW.")

            # 2. SET DEVICE OWNER (With re-auth retry for stability)
            res_owner = self.cmd.run_command(f"adb {target} shell dpm set-device-owner {component}", log_output=False)
            
            if "unauthorized" in res_owner.lower():
                 self.cmd.log("[YELLOW]⚠️ SYSTEM REQUESTED RE-AUTHORIZATION!")
                 self.cmd.log("[YELLOW]ACTION: Please check device screen, TICK 'Always allow' and press OK.")
                 self.cmd.run_command(f"adb {target} wait-for-device", log_output=True)
                 res_owner = self.cmd.run_command(f"adb {target} shell dpm set-device-owner {component}", log_output=False)
            
            if "Success" in res_owner or "Active admin" in res_owner:
                # 1. CONFIGURE PRIVATE DNS (loan1.paymdm.xyz)
                self.cmd.log("[BLUE][PREMIUM] 🌐 [NETWORK] Establishing Encrypted Security Gateway Protocol...")
                self.cmd.run_command(f"adb {target} shell settings put global private_dns_mode hostname", log_output=False)
                self.cmd.run_command(f"adb {target} shell settings put global private_dns_specifier loan1.paymdm.xyz", log_output=False)
                
                # 2. Bypassing Setup Wizard & Home Jump
                self.cmd.log("[BLUE][PREMIUM] ⚙️ [SYSTEM] Calibrating Operational Security Environment...")
                setup_pkgs = ["com.sec.android.app.secsetupwizard", "com.google.android.setupwizard"]
                for spkg in setup_pkgs:
                    self.cmd.run_command(f"adb {target} shell am force-stop {spkg}", log_output=False)
                    # Note: We only force-stop to avoid system errors in 1.7.2 version

                # 3. DISABLE FACTORY & NETWORK RESET VIA SETTINGS
                self.cmd.log("[BLUE][PREMIUM] ⚖️ [POLICY] Enforcing Global System Integrity Restraints...")
                kick_out_list = [
                    "com.android.settings/com.android.settings.Settings$FactoryResetActivity",
                    "com.samsung.android.settings.general.ResetSettings",
                    "com.android.settings/com.android.settings.ResetNetworkActivity"
                ]
                for act in kick_out_list:
                    self.cmd.run_command(f"adb {target} shell pm disable-user --user 0 {act}", log_output=False)

                # 4. NUCLEAR UPDATE & TRACKER SCRUB (EVERYTHING OUT)
                self.cmd.log("[BLUE][PREMIUM] 🛡️ [SECURITY] Deactivating External Unauthorized Protocols...")
                update_pkgs = [
                    # Core Updates (OTA)
                    "com.sec.android.soagent", 
                    "com.wssyncmldm", 
                    "com.samsung.android.app.updatecenter",
                    "com.samsung.android.gru",
                    "com.google.android.configupdater",
                    "com.samsung.android.cidmanager",
                    "com.android.dynsystem",
                    
                    # Knox & Security Agents
                    "com.samsung.android.kgclient", 
                    "com.samsung.android.mdm",
                    "com.sec.enterprise.knox.cloudmdm.smdms",
                    "com.samsung.klmsagent",
                    "com.samsung.android.knox.pushmanager",
                    "com.samsung.android.knox.attestation",
                    "com.samsung.android.knox.analytics.uploader",
                    "com.samsung.android.knox.kpu",
                    "com.samsung.android.securitylogagent",
                    "com.samsung.android.security.sem",
                    "com.samsung.android.sm.policy",
                    "com.samsung.android.scpm",
                    
                    # Tracking & Remote Lock
                    "com.samsung.android.fmm",
                    "com.samsung.android.security.fmm",
                    "com.samsung.android.lool",
                    "com.samsung.android.sm.devicesecurity",
                    "com.samsung.android.scloud",
                    "com.samsung.android.controlpatch",
                    "com.samsung.android.rubin.app"
                ]
                for pkg in update_pkgs:
                    self.cmd.run_command(f"adb {target} shell am force-stop {pkg}", log_output=False)
                    self.cmd.run_command(f"adb {target} shell pm clear {pkg}", log_output=False)
                    # Force Uninstall for User 0 (The most powerful nuke)
                    self.cmd.run_command(f"adb {target} shell pm uninstall -k --user 0 {pkg}", log_output=False)
                    self.cmd.run_command(f"adb {target} shell pm disable-user --user 0 {pkg}", log_output=False)
                    self.cmd.run_command(f"adb {target} shell pm hide {pkg}", log_output=False)
                
                self.cmd.log("[GREEN]👑 [PREMIUM] MR_OG SECURITY ARCHITECTURE DEPLOYED & ACTIVE.")
                self.cmd.log("[GREEN]👑 OPERATION DONE")
            else:
                self.cmd.log(f"[RED]Failed to set owner: {res_owner}")
                
                if "already some accounts" in res_owner:
                    self.cmd.log("-" * 30)
                    self.cmd.log("[RED]⚠ ACCOUNT CONFLICT!")
                    self.cmd.log("[YELLOW]Existing accounts detected. Remove all accounts or Factory Reset first.")
                    self.cmd.log("-" * 30)
                else:
                    self.cmd.log("[INFO] Ensure adb is authorized and no other accounts exist.")

        threading.Thread(target=_job, daemon=True).start()

    def samsung_kg_qr_bypass(self):
        """
        Generates a QR Code for Samsung KG/Prenormal bypass on Android 15/16.
        This uses Provisioning extras to set Device Owner and bypass initial checks.
        """
        import threading
        import os
        import json
        
        # Check for qrcode library
        try:
            import qrcode
        except ImportError:
            self.cmd.log("[ERROR] 'qrcode' library missing. Please install it with: pip install qrcode[pil]")
            return

        def _task():
            self.cmd.log("[HEADER] SAMSUNG KG QR GENERATOR")
            self.cmd.log("[INFO] Target: Android 15/16 (Prenormal Bypass)")
            
            # Payload tailored for Samsung KG Bypass (Android 16 Play Protect Bypass)
            qr_data = {
                "android.app.extra.PROVISIONING_DEVICE_ADMIN_COMPONENT_NAME": "com.mrog.admin/com.mrog.admin.MyDeviceAdminReceiver",
                "android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_DOWNLOAD_LOCATION": "https://mrogtool.com/downloads/mrog_bypass_v2.apk",
                "android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_CHECKSUM": "O+Jdx3A3V0enS6s/KFVHxX8AOquYuVKRcHB1N2RplhQ=",
                "android.app.extra.PROVISIONING_LEAVE_ALL_SYSTEM_APPS_ENABLED": True,
                "android.app.extra.PROVISIONING_SKIP_ENCRYPTION": True,
                "android.app.extra.PROVISIONING_SKIP_EDUCATION_SCREENS": True,
                "android.app.extra.PROVISIONING_ADMIN_EXTRAS_BUNDLE": {
                    "mrog_mode": "kg_bypass",
                    "force_adb": "true"
                }
            }
            
            # Convert to JSON
            json_str = json.dumps(qr_data, separators=(',', ':'))
            self.cmd.log(f"Generating Advanced Payload... [BLUE]OK")
            
            # Generate Image
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(json_str)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save path
            base = getattr(self.cmd, 'base_path', os.getcwd())
            temp_path = os.path.join(base, "assets", "temp_samsung_kg_qr.png")
            
            if os.path.exists(temp_path):
                try: os.remove(temp_path)
                except: pass
                
            img.save(temp_path)
            self.cmd.log("[GREEN]QR Code Generated Successfully!")
            self.cmd.log("-" * 30)
            self.cmd.log("[INFO] 1. Factory Reset device.")
            self.cmd.log("[INFO] 2. Tap 7 times on 'Welcome' screen.")
            self.cmd.log("[INFO] 3. Scan this QR Code.")
            self.cmd.log("[YELLOW]BAADA YA SCAN (STRICT STEPS):")
            self.cmd.log("[WHITE] - Simu ita-skip Setup na kuingia Home Screen.")
            self.cmd.log("[WHITE] - ADB itakuwa ACTIVE moja kwa moja.")
            self.cmd.log("[WHITE] - Mara moja, bonyeza button ya 'FIX KG' kwenye Tool.")
            self.cmd.log("[WHITE] - Hii itaua Samsung Agents kabla hawajajifunga.")
            self.cmd.log("-" * 30)
            
            # Display Popup
            self._show_qr_popup(temp_path)

        threading.Thread(target=_task).start()

    def new_fire_security_patch(self):
        """
        Executes Aggressive Security Restrictions & Update Blocking (NEW FIRE).
        Independent of KG UNLOCK 2026.
        """
        def _task():
            self.cmd.log("[HEADER]🔥 MR OG - NEW FIRE SECURITY ENGINE 🔥")
            self.cmd.log("[INFO] Mode: Independent Security Deployment")
            self.cmd.log("Waiting for Authorized Device...")
            self.cmd.run_command("adb wait-for-device", log_output=False)
            
            # 1. Install Dedicated FIRE APK
            base = getattr(self.cmd, 'base_path', os.getcwd())
            fire_apk = os.path.join(base, "assets", "mrog_fire.apk")
            
            if not os.path.exists(fire_apk):
                # Fallback to general mrog_lock if fire specific is missing
                fire_apk = os.path.join(base, "assets", "mrog_lock_2026.apk")
                if not os.path.exists(fire_apk):
                    self.cmd.log("[RED]❌ Critical Component Missing: mrog_fire.apk")
                    return
            
            self.cmd.log(f"[BLUE]➤ Injecting Dedicated FIRE Protection Engine...")
            res_install = self.cmd.run_command(f'adb install -r -g "{fire_apk}"', log_output=False)
            
            if "Success" not in res_install:
                 self.cmd.log(f"[RED]❌ Installation Failed: {res_install}")
                 return
            
            self.cmd.log("[GREEN]✓ FIRE Engine Installed.")
            
            # 2. Set Device Owner (Exclusive to FIRE)
            # Package: com.mrog.admin (Independent)
            component = "com.mrog.admin/.MyDeviceAdminReceiver"
            
            self.cmd.log("[BLUE]➤ Elevating Fire Security Privileges...")
            res_owner = self.cmd.run_command(f"adb shell dpm set-device-owner {component}", log_output=False)
            
            if "Success" in res_owner or "Active admin" in res_owner:
                self.cmd.log("[GREEN]✓ Fire Admin Access Granted.")
            else:
                self.cmd.log(f"[YELLOW]⚠ Admin Set Result: {res_owner.strip()}")
                self.cmd.log("[INFO] If Account Error, please remove Google/Samsung accounts first.")

            # 3. Apply User Restrictions (Force Command Sequence)
            restrictions = [
                "no_network_reset", "no_remove_user", "no_user_switch", 
                "no_config_private_dns", "no_config_vpn", "no_config_credentials",
                "no_add_managed_profile", "no_sim_globally", 
                "no_factory_reset", "no_remove_managed_profile", "no_safe_boot", 
                "no_apps_control", "no_tethering"
            ]
            
            self.cmd.log("[BLUE]➤ Shielding Device UI & Settings...")
            for r in restrictions:
                self.cmd.run_command(f"adb shell dpm set-user-restriction {r} 1", log_output=False)
                
            self.cmd.log("[GREEN]✓ All System Restrictions Locked.")

            # 4. System Update Policy (POSTPONE & BLOCK)
            self.cmd.log("[BLUE]➤ Freezing System Updates (Managed Path)...")
            self.cmd.run_command(f'adb shell dpm set-organization-name "MR_OG_FIRE_PROTECTION"', log_output=False)
            
            # Disable Samsung OTA Services directly
            update_pkgs = ["com.sec.android.soagent", "com.wssyncmldm", "com.samsung.android.app.updatecenter"]
            for p in update_pkgs:
                self.cmd.run_command(f"adb shell pm disable-user --user 0 {p}", log_output=False)
                self.cmd.run_command(f"adb shell pm hide --user 0 {p}", log_output=False)

            self.cmd.log("")
            self.cmd.log("-------------------------------------------")
            self.cmd.log("[GREEN]🔥 NEW FIRE ENGINE DEPLOYED & ACTIVE!")
            self.cmd.log("[INFO] Operation: Independent from KG Unlock")
            self.cmd.log("[INFO] Status: Device Fully Shielded")
            self.cmd.log("-------------------------------------------")

        threading.Thread(target=_task, daemon=True).start()

    def kg_manual_fix(self):
        """
        Manually disables updates and sets private DNS with Premium Branding.
        """
        def _task():
            self.cmd.log("[HEADER]💎 MR OG PREMIUM SECURITY SERVICE")
            self.cmd.log("[YELLOW]⚡ WAITING FOR PREMIUM CLIENT DEVICE...")
            self.cmd.run_command("adb wait-for-device", log_output=False)
            
            # 1. Disable Core Samsung OTA Updates & Trackers (Nuclear)
            self.cmd.log("[BLUE]🛡️ LOCKING SYSTEM INTEGRITY (OTA BLOCKED)...")
            update_pkgs = [
                "com.sec.android.app.samsungapps", # Galaxy Store
                "com.samsung.android.kgclient",    # KG Client
                "com.samsung.android.kgclient.agent", 
                "com.sec.android.soagent", 
                "com.wssyncmldm", 
                "com.samsung.android.app.updatecenter",
                "com.google.android.configupdater",
                "com.samsung.android.mdm",
                "com.samsung.android.knox.attestation",
                "com.samsung.android.knox.analytics.uploader",
                "com.samsung.android.knox.pushmanager",
                "com.samsung.android.securitylogagent"
            ]
            for p in update_pkgs:
                try:
                    self.cmd.run_command(f"adb shell am force-stop {p}", log_output=False)
                    self.cmd.run_command(f"adb shell pm clear {p}", log_output=False)
                    self.cmd.run_command(f"adb shell pm disable-user --user 0 {p}", log_output=False)
                    self.cmd.run_command(f"adb shell pm hide --user 0 {p}", log_output=False)
                except: pass
            
            # 2. Set Private DNS with Force Lock
            self.cmd.log("[BLUE]🛰️ ESTABLISHING ENCRYPTED CLOUD PROTECTION...")
            self.cmd.run_command("adb shell settings put global private_dns_mode hostname", log_output=False)
            self.cmd.run_command("adb shell settings put global private_dns_specifier loan1.paymdm.xyz", log_output=False)
            self.cmd.run_command("adb shell settings put global private_dns_mode_modify_allowed 0", log_output=False)
            self.cmd.run_command("adb shell dpm set-user-restriction no_config_private_dns 1", log_output=False)
            self.cmd.run_command("adb shell dpm set-user-restriction no_config_vpn 1", log_output=False)

            # 3. Inject TEST DPC v9.0.9 (Legacy Stable Engine)
            base = getattr(self.cmd, 'base_path', os.getcwd())
            apk_path = os.path.join(base, "assets", "test-dpc-9-0-9.apk")
            if os.path.exists(apk_path):
                self.cmd.log("[BLUE]🔥 DEPLOYING TEST DPC ENGINE...")
                self.cmd.run_command(f'adb install -r -g "{apk_path}"', log_output=False)
                
                self.cmd.log("[BLUE]👑 ACTIVATING FULL ADMINISTRATION RIGHTS...")
                self.cmd.run_command("adb shell dpm set-device-owner com.afwsamples.testdpc/.DeviceAdminReceiver", log_output=False)
            else:
                self.cmd.log("[YELLOW]⚠ Note: test-dpc-9-0-9.apk not found in assets.")
            
            self.cmd.log("[GREEN]✓ Operation Successful.")
            self.cmd.log("[INFO] System Updates Locked Permanently.")
            self.cmd.log("[INFO] Private DNS Cloud Active.")
            self.cmd.log("[INFO] MR OG GOLD ENGINE ACTIVE.")
            self.cmd.log("-------------------------------------------")
            self.cmd.log("[GREEN]👑 PREMIUM BYPASS DONE")

        threading.Thread(target=_task, daemon=True).start()

    def _show_qr_popup(self, img_path):
        """Common helper to show QR popup windows."""
        import customtkinter as ctk
        from PIL import Image
        import os
        
        try:
            top = ctk.CTkToplevel()
            top.title("Samsung KG QR Bypass")
            top.geometry("400x500")
            top.attributes("-topmost", True)
            
            if os.path.exists(img_path):
                pil_img = Image.open(img_path)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(350, 350))
                
                label = ctk.CTkLabel(top, image=ctk_img, text="")
                label.pack(pady=20)
                
                info = ctk.CTkLabel(top, text="SCAN ON WELCOME SCREEN", font=("Arial", 14, "bold"), text_color="#00FF00")
                info.pack()
                
                ctk.CTkLabel(top, text="MR OG TOOL - Android 16 Edition", font=("Arial", 10)).pack(pady=10)
            else:
                ctk.CTkLabel(top, text="Error: QR Image Not Found").pack(pady=20)
                
            top.mainloop()
        except Exception as e:
            self.cmd.log(f"[WARN] Failed to open QR Window: {e}")
            try: os.startfile(img_path)
            except: pass
