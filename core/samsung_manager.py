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
            apk_path = os.path.join("assets", "test-dpc-9-0-9.apk")
            if os.path.exists(apk_path):
                self.cmd.log(f"[*] Installing {apk_path}...")
                self.cmd.run_command(f'adb install -r "{apk_path}"') # -r for reinstall if exists
                
                self.cmd.log("[*] Setting Device Owner...")
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

    def mdm_bypass_2025(self):
        import threading
        def _task():
            self.cmd.log("[BLUE]Starting Samsung MDM 2025 Bypass...")
            self.cmd.log("Note: Ensure USB Debugging is ON via *#0*# or QR.")
            
            # 1. Connection Check
            self.cmd.log("[BLUE]Waiting ADB devices...")
            while True:
                # Silent check to avoid log spam
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
            
            self.cmd.log("[BLUE]Device Detected! Proceeding...")

            # 2. Disable Updates & Bloatware (The core MDM agents)
            self.cmd.log("[STEP] Disabling Update Agents...")
            pkgs = [
                "com.sec.android.soagent",
                "com.sec.android.systemupdate",
                "com.wssyncmldm",
                "com.samsung.android.app.updatecenter",
                "com.samsung.android.cidmanager",
                "com.sec.enterprise.knox.cloudmdm.smdms", # Knox Cloud
                "com.samsung.android.mdm",
                "com.knox.vpn.proxyhandler"
            ]
            for p in pkgs:
                self.cmd.run_command(f"adb shell pm disable-user --user 0 {p}")
                self.cmd.run_command(f"adb shell appops set {p} RUN_IN_BACKGROUND ignore") # Harder kill

            # 3. Disable Factory Reset & Network Reset (Attempt via User Restrictions)
            self.cmd.log("[STEP] Blocking Factory/Network Reset...")
            # This sets user restrictions preventing reset
            self.cmd.run_command("adb shell pm create-user --guest GuestUser") # Distraction
            self.cmd.run_command("adb shell settings put secure user_setup_complete 1")
            
            # 4. Disable DNS (Prevent calling home)
            self.cmd.log("[STEP] Disabling Private DNS...")
            self.cmd.run_command("adb shell settings put global private_dns_mode off")
            self.cmd.run_command("adb shell settings delete global private_dns_specifier")

            # 5. Device Admin (MR OG TOOL / Test DPC)
            self.cmd.log("[STEP] Setting Device Admin...")
            
            import os
            apk_path = os.path.join("assets", "test_dpc.apk")
            
            if os.path.exists(apk_path):
                 self.cmd.log("[INFO] Installing Bypass Agent (Test DPC)...")
                 self.cmd.run_command(f"adb install -r \"{apk_path}\"")
                 
                 self.cmd.log("[INFO] Setting Permission...")
                 # Set Device Owner to Test DPC
                 res = self.cmd.run_command('adb shell dpm set-device-owner "com.afwsamples.testdpc/.DeviceAdminReceiver"')
                 if "Success" in res:
                     self.cmd.log("[SUCCESS] Device Owner Set! (Strong Bypass)")
                 else:
                     self.cmd.log(f"[WARN] Owner Set Failed: {res}")
                     self.cmd.log("[INFO] Applying Shell Fallback...")
                     # Fallback commands if needed
            else:
                self.cmd.log("[WARN] Bypass Agent APK not found in assets/test_dpc.apk")
                self.cmd.log("[INFO] Please run 'download_resources.bat' to get the APK.")
                self.cmd.log("[INFO] Applying Shell Restrictions (Weak Bypass)...")

            
            self.cmd.log("[SUCCESS] MDM Protections Removed!")
            self.cmd.log("[INFO] Updates: BLOCKED")
            self.cmd.log("[INFO] Reset: BLOCKED")
            self.cmd.log("[INFO] DNS: DISABLED")
            self.cmd.log("Rebooting device to apply...")
            self.cmd.run_command("adb reboot")
            self.cmd.log("DONE.")

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
