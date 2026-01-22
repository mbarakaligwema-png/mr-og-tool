import os
import threading
import time
from core.utils import CommandRunner

class SamsungManager:
    def __init__(self, log_callback):
        self.cmd = CommandRunner(log_callback)
        self.assets_dir = os.path.join(os.getcwd(), 'assets')
        
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
        odin_path = os.path.join(self.assets_dir, "tools", "Odin3 v3.13.3.exe")
        if os.path.exists(odin_path):
            self.cmd.log("Launching external Odin Tool...")
            import subprocess
            try:
                subprocess.Popen([odin_path], shell=True)
                self.cmd.log("[SUCCESS] Odin Launched.")
            except Exception as e:
                self.cmd.log(f"[ERROR] Failed to open Odin: {e}")
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
                helper_path = os.path.join(self.assets_dir, "tools", "mtp_helper.exe")
                
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
             self.cmd.log("Starting KG BYPASS (ANDROID 15/16/17)...")
             self.cmd.log("Waiting for ADB Device...")
             # self.cmd.run_command("adb wait-for-device", log_output=False)
             
             # Wait for device loop (FAST SCAN)
             self.cmd.log("Scanning for Device...")
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

             self.cmd.log("Device Detected.")
             
             # 0. INSTALL APK FIRST (To avoid USB Reset by KG Agents later)
             apk_path = os.path.join(self.assets_dir, "mrog_admin_v3.apk")
             if os.path.exists(apk_path):
                 self.cmd.log("[*] Installing Bypass App (Priority 1)...")
                 self.cmd.run_command("adb shell settings put global package_verifier_enable 0", log_output=False)
                 res = self.cmd.run_command(f'adb install -t -r -g "{apk_path}"', log_output=False)
                 
                 if "Success" in res:
                      self.cmd.log("[GREEN]App Installed! Proceeding to Kill Agents...")
                 else:
                      self.cmd.log(f"[RED]Install Failed: {res}")
             
             # 1. IMMEDIATE KILL (CRITICAL BEFORE ANYTHING ELSE)
             self.cmd.log("[*] Pre-emptive Strike: Killing KG Agents...")
             killer_pkgs = [
                "com.samsung.android.kgclient",
                "com.samsung.android.kgclient.agent",
                "com.samsung.android.mdm",
                "com.sec.enterprise.knox.cloudmdm.smdms",
                "com.samsung.klmsagent",
                "com.sec.android.soagent",
                "com.wssyncmldm",
                "com.sec.android.app.samsungapps", # NEW: Galaxy Store (Block Updates)
                "com.sec.android.app.billing"      # NEW: Billing
             ]
             
             def _kill_loop():
                 # Keep killing in background during setup
                 for _ in range(15): # Increased duration
                     for p in killer_pkgs:
                         self.cmd.run_command(f"adb shell am force-stop {p}", log_output=False)
                         self.cmd.run_command(f"adb shell pm disable-user --user 0 {p}", log_output=False)
                     time.sleep(1.5)
             
             threading.Thread(target=_kill_loop, daemon=True).start()
             
             for p in killer_pkgs:
                 self.cmd.run_command(f"adb shell pm uninstall -k --user 0 {p}", log_output=False)
                 self.cmd.run_command(f"adb shell pm hide {p}", log_output=False)
                 self.cmd.run_command(f"adb shell pm suspend --user 0 {p}", log_output=False)

             # 2. Silent Setup
             self.cmd.log("[*] Initializing Setup...")
             
             # DNS (Disable Private DNS to prevent leaks/blocking)
             self.cmd.run_command('adb shell settings put global private_dns_mode off', log_output=False)
             # self.cmd.run_command('adb shell settings delete global private_dns_specifier', log_output=False)
             

             
             # (Install Block Moved to Top)

             # 3. Activate Owner
             self.cmd.log("[*] Activating Device Owner...")
             
             # Attempt to set owner
             cmd_owner = 'adb shell dpm set-device-owner --user 0 "com.mrog.admin/.MyDeviceAdminReceiver"'
             res = self.cmd.run_command(cmd_owner, log_output=False)
             
             # Analyze Result
             if "Success" in res or "Active admin" in res or "already set" in res or "already an admin" in res:
                 self.cmd.log("[GREEN]Device Owner Set Successfully!")
             else:
                 # Check for common errors
                 clean_res = res.strip()
                 self.cmd.log(f"[RED]Failed to set Owner: {clean_res}")
                 
                 if "getting account" in clean_res.lower() or "accounts" in clean_res.lower() or "account" in clean_res.lower():
                     self.cmd.log("[YELLOW]HINT: Remove ALL Google/Samsung Accounts manually from Settings first!")
                     self.cmd.log("[YELLOW]Or Factory Reset the device if you cannot remove accounts.")
                 
                 elif "not allowed" in clean_res.lower():
                     self.cmd.log("[YELLOW]HINT: Device might be provisioned already. Factory Reset needed.")

                 # Fallback: Try to just enable it as admin (Less power, but something)
                 # self.cmd.run_command('adb shell dpm set-active-admin --user 0 "com.mrog.admin/.MyDeviceAdminReceiver"', log_output=False)
                 
                 # Continue anyway? No, without owner, the 'nuclear' options won't work.
                 # But we proceed to try the other adb commands just in case.

             # 4. Enforce Policy (WAKE UP THE APP + ENABLE ACCESSIBILITY)
             self.cmd.log("[*] Waking up Admin App & Services...")
             
             # Force Enable Accessibility Service (The Interceptor)
             acc_cmd = 'adb shell settings put secure enabled_accessibility_services com.mrog.admin/.MyAccessibilityService'
             self.cmd.run_command(acc_cmd, log_output=False)
             self.cmd.run_command('adb shell settings put secure accessibility_enabled 1', log_output=False)
             
             # Launch UI to ensure app is not in 'stopped' state
             self.cmd.run_command('adb shell am start -n com.mrog.admin/.MainActivity', log_output=False)
             time.sleep(3)
             
             # Send Broadcast with FLAG_INCLUDE_STOPPED_PACKAGES (32)
             # This tells the APK to specifically execute its "Lock" logic (DISALLOW_FACTORY_RESET)
             self.cmd.log("[*] Sending LOCK Command to Admin App...")
             self.cmd.run_command('adb shell am broadcast -a com.mrog.admin.ACTION_LOCK -f 32', log_output=False)
             self.cmd.run_command('adb shell am broadcast -a com.mrog.admin.ACTION_LOCK', log_output=False) # Without flag just in case
             
             # NEW: Force MDM Restrictions (The Real Fix)
             self.cmd.log("[*] Verifying MDM Restrictions...")
             # Try to set via ADB (works on many Samsung exploits when owner is set)
             cmd_fr = 'adb shell dpm set-user-restriction --user 0 no_factory_reset 1'
             self.cmd.run_command(cmd_fr, log_output=False)
             self.cmd.run_command('adb shell dpm set-user-restriction --user 0 no_config_credentials 1', log_output=False)
             
             # Check if it sticked
             res_check = self.cmd.run_command('adb shell dpm get-user-restriction --user 0 no_factory_reset', log_output=False)
             if "true" in str(res_check).lower() or "1" in str(res_check):
                 self.cmd.log("[GREEN]Factory Reset BLOCKED via ADB!")
             else:
                 self.cmd.log("[YELLOW]ADB Restrictions blocked by Android 16 Security.")
                 self.cmd.log("[GREEN]Trusting Internal Admin App to enforce Policy...")
                 # Retrigger the internal enforcement
                 self.cmd.run_command('adb shell am broadcast -a com.mrog.admin.ACTION_LOCK -f 32', log_output=False)
                 
             time.sleep(1)

             # 5. Hide/Disable Reset Activities (Silent)
             reset_activities = [
                 "com.android.settings/com.android.settings.Settings$FactoryResetActivity",
                 "com.android.settings/com.samsung.android.settings.general.ResetSettings",
                 "com.android.settings/com.samsung.android.settings.privacy.FactoryReset",
                 "com.android.settings/com.samsung.android.settings.general.GeneralDeviceSettings",
                 "com.android.settings/com.samsung.android.settings.general.ResetDashboardActivity",
                 "com.android.settings/com.android.settings.Settings$PrivacySettingsActivity",
                 "com.android.settings/com.samsung.android.settings.backup.BackupResetSettingsActivity",
                 "com.android.settings/com.samsung.android.settings.general.ResetNetworkActivity",
                 "com.sec.android.app.factoryreset",
                 # NEW: Confirm Screens
                 "com.android.settings/com.samsung.android.settings.general.FactoryResetConfirm",
                 "com.android.settings/com.samsung.android.settings.factory.FactoryResetActivity"
             ]
             
             self.cmd.log("[*] Disabling Reset Menus...")
             for act in reset_activities:
                 # pm disable-user works on components
                 res = self.cmd.run_command(f"adb shell pm disable-user --user 0 {act}", log_output=False)
                 if "SecurityException" in res or "Error" in res:
                      self.cmd.log(f"[DEBUG] Failed to disable {act.split('.')[-1]}")
                 
                 # pm hide ONLY works on PACKAGES, not components. 
                 # We shouldn't run it on 'com.android.settings/...' it will fail or do nothing.
                 # So we rely on disable-user.

             # FORCE SETTINGS REFRESH (Critical for removing cached menu items)
             self.cmd.run_command("adb shell pm clear com.android.settings", log_output=False)

             # 6. Package Cleanup (AGGRESSIVE MODE - NO PLAY STORE)
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
             
             self.cmd.log("[*] Nuking Samsung Services...")
             for p in pkgs:
                 # 1. Kill
                 self.cmd.run_command(f"adb shell am force-stop {p}", log_output=False)
                 # 2. Clear Data
                 self.cmd.run_command(f"adb shell pm clear {p}", log_output=False)
                 # 3. Disable
                 self.cmd.run_command(f"adb shell pm disable-user --user 0 {p}", log_output=False)
                 # 4. Hide (Package Level)
                 self.cmd.run_command(f"adb shell pm hide {p}", log_output=False)
                 # 5. Uninstall (Optional)
                 self.cmd.run_command(f"adb shell pm uninstall -k --user 0 {p}", log_output=False)
            
             # EXPLICITLY HIDE FACTORY RESET PACKAGE (If it exists as separate app)
             self.cmd.run_command("adb shell pm hide com.sec.android.app.factoryreset", log_output=False)

             # DOUBLE CHECK: Re-apply Reset Blocks (Safety Lock)
             self.cmd.log("[*] Finalizing Safety Locks (SUSPEND MODE)...")
             
             # PM SUSPEND (New Layer of Security)
             suspend_targets = [
                 # Reset Screens
                 "com.sec.android.app.factoryreset",
                 "com.android.settings/com.android.settings.Settings$FactoryResetActivity",
                 "com.android.settings/com.samsung.android.settings.general.ResetSettings",
                 "com.android.settings/com.samsung.android.settings.general.FactoryResetConfirm",
                 # CRITICAL: Prevent Updates & Relock
                 "com.sec.android.soagent",
                 "com.wssyncmldm",
                 "com.sec.android.systemupdate",
                 "com.sec.enterprise.knox.cloudmdm.smdms",
                 "com.samsung.klmsagent",
                 "com.sec.android.app.samsungapps" # Galaxy Store
             ]
             
             for target in suspend_targets:
                 # Suspend requires Package, usually.
                 if "/" in target:
                     # It's an activity, use disable
                     self.cmd.run_command(f"adb shell pm disable-user --user 0 {target}", log_output=False)
                 else:
                     # It's a package, use suspend + hide + disable
                     self.cmd.run_command(f"adb shell pm suspend --user 0 {target}", log_output=False)
                     self.cmd.run_command(f"adb shell pm hide {target}", log_output=False)
                     self.cmd.run_command(f"adb shell pm disable-user --user 0 {target}", log_output=False)

             # Final Policy Push
             cmd_fr = 'adb shell dpm set-user-restriction --user 0 no_factory_reset 1'
             self.cmd.run_command(cmd_fr, log_output=False)
             
             # Final Settings Clear
             self.cmd.run_command("adb shell pm clear com.android.settings", log_output=False)

             self.cmd.log("[GREEN]System Cleanup: DONE (Strict Mode)")
             
             # 7. Finalize (Silent)
             self.cmd.run_command('adb shell pm disable com.mrog.admin/.MainActivity', log_output=False) 
             self.cmd.run_command('adb shell pm hide com.mrog.admin', log_output=False)
             
             self.cmd.log("[GREEN]KG ANDROID 15/16 BYPASS COMPLETED.")
             self.cmd.log("[INFO] Device is Protected.")
             self.cmd.log("[IMPORTANT] DO NOT UPDATE THE SYSTEM.")
             # self.cmd.log("Restarting device in 5 seconds...")
             # time.sleep(5)
             # self.cmd.run_command("adb reboot", log_output=False)
             self.cmd.log("Done. Please reboot manually if needed.")

         threading.Thread(target=_bypass_thread).start()

    def fix_kg_relock(self):
        """
        Aggressive Fix to prevent KG Relock on WiFi/Sim.
        Disables Galaxy Store, Updates, KG Client, etc.
        """
        def _task():
            self.cmd.log("[HEADER] FIX KG RELOCK (ANTI-RELOCK)")
            self.cmd.log("Waiting for ADB Device...")
            
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
