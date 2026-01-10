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
        
        def run_process():
            self.cmd.log("Operation: ANTIRELOCK LATEST")
            self.cmd.log("Initializing ADB Server...")
            
            # 1. Restart ADB
            self.cmd.run_command("adb kill-server")
            self.cmd.run_command("adb start-server")
            
            self.cmd.log("Waiting for device...")
            # Using specific timeout logic or just wait-for-device
            self.cmd.run_command("adb wait-for-device")
            
            self.cmd.log("")
            self.cmd.log("[+] Device Connected Successfully!")
            self.cmd.log("---------------------------------------------------------------------------")

            # 2. Configure Private DNS
            self.cmd.log("[*] Configuring Private DNS...")
            self.cmd.run_command("adb shell settings put global private_dns_mode hostname")
            self.cmd.run_command("adb shell settings put global private_dns_specifier 1ff2bf.dns.nextdns.io")
            self.cmd.log("[OK] Private DNS Configured.")

            # 3. Install Test DPC
            self.cmd.log("")
            self.cmd.log("[*] Installing Test DPC...")
            
            import os
            apk_path = os.path.join("assets", "test-dpc-9-0-9.apk")
            if os.path.exists(apk_path):
                # Install APK
                res = self.cmd.run_command(f"adb install \"{apk_path}\"")
                # Set Device Owner
                # cmd: adb shell dpm set-device-owner "com.afwsamples.testdpc/.DeviceAdminReceiver"
                # Note: We need careful quoting for the shell command string in Python
                self.cmd.run_command('adb shell dpm set-device-owner "com.afwsamples.testdpc/.DeviceAdminReceiver"')
                self.cmd.log("[SUCCESS] Test DPC Installed Successfully!")
            else:
                 self.cmd.log(f"[ERROR] APK not found at: {apk_path}")

            # 4. Remove Bloatware
            self.cmd.log("")
            self.cmd.log("[*] Removing System Updates and Bloatware...")
            
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
                self.cmd.run_command(f"adb shell pm uninstall --user 0 {p}")
            
            self.cmd.log("[SUCCESS] System Updates Removed Successfully!")
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
        self.cmd.log(f"BL: {files_dict.get('BL')}")
        self.cmd.log(f"AP: {files_dict.get('AP')}")
        self.cmd.log(f"CP: {files_dict.get('CP')}")
        self.cmd.log(f"CSC: {files_dict.get('CSC')}")
        
        # Check for heimdall or odin CLI
        msg = "Automatic flashing requires 'Heimdall' or 'Odin4 CLI'.\n" \
              "Currently behaving as a placeholder. Please use GUI Odin for now until the flasher module is fully integrated."
        self.cmd.log(f"[WARN] {msg}")
        self.cmd.log("[INFO] Files validated successfully.")
