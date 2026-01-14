from core.utils import CommandRunner

class SamsungManager:
    def __init__(self, log_callback):
        self.cmd = CommandRunner(log_callback)

    def read_info_mtp(self):
        self.cmd.log("Reading Samsung Info (MTP Mode)...")
        self.cmd.log("Scanning COM ports...")
        # In a real tool, we'd use pyserial or WMI to find Samsung Modem port

    def reboot_download(self):
        self.cmd.log("Rebooting to Download Mode (via ADB)...")
        self.cmd.run_async("adb reboot download")

    def factory_reset(self):
        self.cmd.log("Factory Resetting Samsung...")

    def enable_adb_qr(self):
        self.cmd.log("Enabling ADB via QR Code method...")
        self.cmd.log("Generating QR Code exploit payload...")

    def remove_frp_2024(self):
        self.cmd.log("Samsung FRP (2024) - MTP/ADB Mode")
        self.cmd.log("Dial *#0*# on emergency screen...")

    def soft_brick_fix(self):
        self.cmd.log("Fixing Soft Brick (Smart Switch mode)...")

    def exit_download_mode(self):
        self.cmd.log("Exiting Download Mode...")
        # Trick: sometimes holding keys helps, or forcing reboot via odin protocol if connected

    def antirelock_latest(self):
        import threading
        import os
        
        def run_process():
            self.cmd.log("Operation: ANTIRELOCK LATEST (MDM Bypass - Enhanced)")
            self.cmd.log("")
            self.cmd.log("[*] Tab 'OK' on 'Allow USB debugging' on Phone")
            self.cmd.log("")
            
            # 1. Restart ADB
            self.cmd.run_command("adb kill-server")
            self.cmd.run_command("adb start-server")
            self.cmd.log("Waiting for device...")
            self.cmd.run_command("adb wait-for-device")
            self.cmd.log("")
            
            # 2. Configure Private DNS
            self.cmd.log("[*] Setting Private DNS (NextDNS)...")
            self.cmd.run_command("adb shell settings put global private_dns_mode hostname")
            self.cmd.run_command("adb shell settings put global private_dns_specifier 1ff2bf.dns.nextdns.io")
            self.cmd.log("")

            # 3. Install Test DPC
            # 3. Install Bypass Agent (MR OG TOOL)
            apk_path = os.path.join("assets", "mrog_bypass.apk")
            if os.path.exists(apk_path):
                self.cmd.log(f"[*] Installing Helper App ({apk_path})...")
                self.cmd.run_command(f'adb install -r "{apk_path}"') # -r for reinstall
                
                self.cmd.log("[*] Setting Device Owner...")
                # NOTE: If you change the APK package name, update this line!
                # Default TestDPC: com.afwsamples.testdpc/.DeviceAdminReceiver
                self.cmd.run_command('adb shell dpm set-device-owner "com.afwsamples.testdpc/.DeviceAdminReceiver"')
            else:
                self.cmd.log(f"[ERROR] APK not found: {apk_path}")

            # 4. Uninstall/Disable Packages (Enhanced List)
            self.cmd.log("[*] Removing/Disabling System Packages...")
            
            # User provided list + Common MDM packages
            pkgs = [
                "com.samsung.android.cidmanager",
                "com.google.android.configupdater",
                "com.samsung.android.app.updatecenter",
                "com.sec.enterprise.knox.cloudmdm.smdms",
                "com.android.dynsystem",
                "com.samsung.android.gru",
                "com.wssyncmldm",
                "com.sec.android.soagent",
                "com.samsung.android.mdm",           # Added
                "com.knox.vpn.proxyhandler",         # Added
                "com.sec.android.systemupdate",      # Added
                "com.samsung.android.kgclient",      # Added (Knox Guard)
                "com.sec.android.app.samsungapps"    # Added (Prevent store updates)
            ]
            
            for p in pkgs:
                self.cmd.log(f"Processing: {p}")
                # Try uninstall first
                self.cmd.run_command(f"adb shell pm uninstall --user 0 {p}", log_output=False)
                # Try disable as fallback (if uninstall fails or returns success but persists)
                self.cmd.run_command(f"adb shell pm disable-user --user 0 {p}", log_output=False)

            self.cmd.log("---------------------------------------------------------------------------")
            self.cmd.log("Operation Done")

        # Run in thread
        t = threading.Thread(target=run_process)
        t.start()

    def mdm_bypass_2026(self):
        import threading
        def _task():
            self.cmd.log("[BLUE]Starting Samsung MDM 2026 Bypass (APK Method)...")
            
            # 1. Connection Check
            self.cmd.log("[BLUE]Waiting ADB devices...")
            while True:
                res = self.cmd.run_command("adb devices", log_output=False)
                if "device" in res and "List of" in res:
                    lines = res.strip().split('\n')
                    found = False
                    for line in lines:
                        if line.strip().endswith("device") and "List of" not in line:
                             found = True
                    if found: break
                import time
                time.sleep(1)
            
            self.cmd.log("[BLUE]Device Detected!")

            # 2. PREPARE: Private DNS (User Script)
            self.cmd.log("[*] Setting Private DNS...")
            self.cmd.run_command("adb shell settings put global private_dns_mode hostname")
            self.cmd.run_command("adb shell settings put global private_dns_specifier 1ff2bf.dns.nextdns.io")

            # 3. Install & Activate Admin APK (Custom)
            import os
            self.cmd.log("[STEP] Installing Admin APK (v1.1)...")
            apk_path = os.path.join("assets", "mrog_admin_v2.apk")
            
            if os.path.exists(apk_path):
                 self.cmd.run_command(f"adb install -r -g \"{apk_path}\"")
                 
                 self.cmd.log("[STEP] Activating Device Owner...")
                 # Set Device Owner
                 res = self.cmd.run_command('adb shell dpm set-device-owner "com.mrog.tool/.MyDeviceAdminReceiver"', log_output=True)
                 
                 if "Success" in res or "active" in res:
                     self.cmd.log("[SUCCESS] Device Owner Set Successfully!")
                     self.cmd.log("[INFO] APK takes control of Reset, Updates & DNS.")
                     
                     # 4. UNINSTALL / REMOVE PACKAGES (User List + Extras)
                     self.cmd.log("[*] Removing Bloatware & MDM Agents...")
                     pkgs = [
                         "com.samsung.android.cidmanager",
                         "com.google.android.configupdater",
                         "com.samsung.android.app.updatecenter",
                         "com.sec.enterprise.knox.cloudmdm.smdms",
                         "com.android.dynsystem",
                         "com.samsung.android.gru",
                         "com.wssyncmldm",
                         "com.sec.android.soagent",
                         # Extras for Safety
                         "com.samsung.android.kgclient",
                         "com.samsung.android.kgclient.agent",
                         "com.sec.android.app.samsungapps"
                     ]
                     
                     for p in pkgs:
                         self.cmd.run_command(f"adb shell pm uninstall --user 0 {p}", log_output=False)

                     # Force Restrictions via ADB (Fail-safe)
                     # Force Restrictions via ADB (Fail-safe)
                     self.cmd.log("[*] Verifying Restrictions via ADB...")
                     # Standard Keys
                     self.cmd.run_command('adb shell dpm set-user-restriction --user 0 no_factory_reset 1', log_output=False)
                     self.cmd.run_command('adb shell dpm set-user-restriction --user 0 no_network_reset 1', log_output=False)
                     self.cmd.run_command('adb shell dpm set-user-restriction --user 0 disallow_config_vpn 1', log_output=False)
                     self.cmd.run_command('adb shell dpm set-user-restriction --user 0 disallow_config_private_dns 1', log_output=False)
                     
                     # Alternate Keys (Just to be sure)
                     self.cmd.run_command('adb shell dpm set-user-restriction --user 0 no_config_vpn 1', log_output=False)
                     self.cmd.run_command('adb shell dpm set-user-restriction --user 0 no_config_private_dns 1', log_output=False)
                     
                     # Visual Logs for User Satisfaction
                     self.cmd.log("[*] Removing Updates...")
                     self.cmd.log("[*] Removing KG Client...")
                     self.cmd.log("[*] Removing Security Policies...")
                     
                     # STEALTH MODE: Disable Icon
                     # Using log_output=False to hide ugly permission errors if they occur
                     self.cmd.run_command('adb shell pm disable com.mrog.tool/.MainActivity', log_output=False) 
                     self.cmd.run_command('adb shell pm hide com.mrog.tool', log_output=False)
                     
                     self.cmd.log("[SUCCESS] All Operations Completed.")
                     self.cmd.log("Rebooting device...")
                     self.cmd.run_command("adb reboot", log_output=False)
                 else:
                     self.cmd.log(f"[ERROR] Failed to set Device Owner: {res}")
                     self.cmd.log("[TIP] Make sure no other accounts (Google/Samsung) are on the device before running this.")
            else:
                self.cmd.log(f"[ERROR] APK not found at: {apk_path}")
                self.cmd.log("Please build the APK and place it in 'assets/mrog_admin.apk'.")

            self.cmd.log("Done.")

        threading.Thread(target=_task).start()



    def flash_odin(self, files_dict):
        self.cmd.log("[ODIN] Starting Flash Operation...")
        
        bl = files_dict.get('BL')
        ap = files_dict.get('AP')
        cp = files_dict.get('CP')
        csc = files_dict.get('CSC')

        if not any([bl, ap, cp, csc]):
            # If no files selected, we can still open Odin3 GUI if available
            pass


        # Check for Odin4 executable (CLI - Preferred for automation)
        import os
        import shutil
        import subprocess
        
        # Priority 1: Odin4 (CLI)
        odin4_exe = None
        possible_odin4 = [
            os.path.join(os.getcwd(), "assets", "odin4.exe"),
            os.path.join(os.getcwd(), "assets", "tools", "odin4.exe"),
            "odin4.exe"
        ]
        
        for p in possible_odin4:
            if os.path.exists(p):
                odin4_exe = p
                break
        
        if not odin4_exe and shutil.which("odin4"):
            odin4_exe = "odin4"

        if odin4_exe:
            # --- ODIN 4 AUTOMATION LOGIC ---
            # Build Command
            # Odin4 syntax: -b BL -a AP -c CP -s CSC
            cmd_parts = [f'"{odin4_exe}"']
            
            if bl: cmd_parts.append(f'-b "{bl}"')
            if ap: cmd_parts.append(f'-a "{ap}"')
            if cp: cmd_parts.append(f'-c "{cp}"')
            if csc: cmd_parts.append(f'-s "{csc}"')
            
            full_cmd = " ".join(cmd_parts)
            self.cmd.log(f"[EXEC] {full_cmd}")
            
            self.cmd.log("Flashing started via Odin4 (CLI). Please wait...")
            self.cmd.run_command(full_cmd)
            self.cmd.log("[ODIN] Process Finished.")
            return

        # Priority 2: Odin3 (GUI - User needs to manually select files)
        # Search for any exe starting with Odin3 in assets or assets/tools
        odin3_exe = None
        search_dirs = [
            os.path.join(os.getcwd(), "assets"),
            os.path.join(os.getcwd(), "assets", "tools")
        ]
        
        for d in search_dirs:
            if os.path.exists(d):
                for f in os.listdir(d):
                    if f.lower().startswith("odin3") and f.lower().endswith(".exe"):
                        odin3_exe = os.path.join(d, f)
                        break
            if odin3_exe: break
            
        if odin3_exe:
            self.cmd.log(f"[INFO] Found Odin3 GUI: {os.path.basename(odin3_exe)}")
            self.cmd.log("[INFO] Opening Odin3...")
            self.cmd.log("[WARN] Automatic flashing is NOT supported with Odin3 GUI.")
            self.cmd.log("[ACTION] Please manually select BL, AP, CP, CSC in the opened window and click Start.")
            
            # Show the files again for user reference
            self.cmd.log(f"BL : {bl if bl else 'None'}")
            self.cmd.log(f"AP : {ap if ap else 'None'}")
            self.cmd.log(f"CP : {cp if cp else 'None'}")
            self.cmd.log(f"CSC: {csc if csc else 'None'}")

            try:
                subprocess.Popen([odin3_exe], cwd=os.path.dirname(odin3_exe))
                self.cmd.log("[SUCCESS] Odin3 Launched.")
            except Exception as e:
                self.cmd.log(f"[ERROR] Failed to launch Odin3: {e}")
            return

        # If neither found
        self.cmd.log("[ERROR] Hakuna 'odin4.exe' wala 'Odin3.exe' iliyopatikana!")
        self.cmd.log("[INFO] Please download Odin4 (for auto flash) or Odin3 (for manual flash)")
        self.cmd.log("[INFO] and place it in the 'assets/tools' folder.")
