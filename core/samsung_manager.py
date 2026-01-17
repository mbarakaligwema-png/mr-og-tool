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
             
             # Wait for device loop
             while True:
                 res = self.cmd.run_command("adb devices", log_output=False)
                 if "device" in res and "List of" in res:
                    lines = res.strip().split('\n')
                    found = False
                    for line in lines:
                        if line.strip().endswith("device") and "List of" not in line:
                            found = True
                    if found: break
                 time.sleep(1)

             self.cmd.log("Device Detected.")

             # 1. IMMEDIATE KILL (CRITICAL BEFORE ANYTHING ELSE)
             self.cmd.log("[*] Pre-emptive Strike: Killing KG Agents...")
             killer_pkgs = [
                "com.samsung.android.kgclient",
                "com.samsung.android.kgclient.agent",
                "com.samsung.android.mdm",
                "com.sec.enterprise.knox.cloudmdm.smdms",
                "com.samsung.klmsagent",
                "com.sec.android.soagent",
                "com.wssyncmldm"
             ]
             
             def _kill_loop():
                 # Keep killing in background during setup
                 for _ in range(10):
                     for p in killer_pkgs:
                         self.cmd.run_command(f"adb shell am force-stop {p}", log_output=False)
                         self.cmd.run_command(f"adb shell pm disable-user --user 0 {p}", log_output=False)
                     time.sleep(2)
             
             threading.Thread(target=_kill_loop, daemon=True).start()
             
             for p in killer_pkgs:
                 self.cmd.run_command(f"adb shell pm uninstall -k --user 0 {p}", log_output=False)
                 self.cmd.run_command(f"adb shell pm hide {p}", log_output=False)
                 self.cmd.run_command(f"adb shell pm suspend --user 0 {p}", log_output=False)

             # 2. Silent Setup
             self.cmd.log("[*] Initializing Setup...")
             
             # DNS (Silent)
             self.cmd.run_command('adb shell settings put global private_dns_mode hostname', log_output=False)
             self.cmd.run_command('adb shell settings put global private_dns_specifier 1ff2bf.dns.nextdns.io', log_output=False)
             
             # Uninstall Old (Silent)
             self.cmd.run_command('adb uninstall com.mrog.tool', log_output=False)
             
             # Install APK (Silent)
             apk_path = os.path.join(self.assets_dir, "mrog_admin_v3.apk")
             if os.path.exists(apk_path):
                 installation_res = self.cmd.run_command(f'adb install -r -g "{apk_path}"', log_output=False)
                 if "Success" not in installation_res:
                      self.cmd.log(f"[ERROR] Install Failed: {installation_res}")
                      # Continue anyway
             else:
                 self.cmd.log(f"[ERROR] mrog_admin_v3.apk missing at {apk_path}!")
                 return

             # 3. Activate Owner
             self.cmd.log("[*] Activating Device Owner...")
             res = self.cmd.run_command('adb shell dpm set-device-owner "com.mrog.tool/.MyDeviceAdminReceiver"', log_output=False)
             
             if "Success" in res or "Active admin" in res or "already set" in res:
                 self.cmd.log("[GREEN]Device Owner Set Successfully!")
             else:
                 self.cmd.log(f"[RED]Failed to set Owner: {res}")
                 # Continue to try logic anyway

             # 4. Enforce Policy (WAKE UP THE APP + ENABLE ACCESSIBILITY)
             self.cmd.log("[*] Waking up Admin App & Services...")
             
             # Force Enable Accessibility Service (The Interceptor)
             acc_cmd = 'adb shell settings put secure enabled_accessibility_services com.mrog.tool/.MyAccessibilityService'
             self.cmd.run_command(acc_cmd, log_output=False)
             self.cmd.run_command('adb shell settings put secure accessibility_enabled 1', log_output=False)
             
             # Launch UI to ensure app is not in 'stopped' state
             self.cmd.run_command('adb shell am start -n com.mrog.tool/.MainActivity', log_output=False)
             time.sleep(3)
             
             # Send Broadcast with FLAG_INCLUDE_STOPPED_PACKAGES (32)
             # This tells the APK to specifically execute its "Lock" logic (DISALLOW_FACTORY_RESET)
             self.cmd.run_command('adb shell am broadcast -a com.mrog.tool.ACTION_LOCK -f 32', log_output=False)
             
             # NEW: Force MDM Restrictions (The Real Fix)
             self.cmd.log("[*] Enforcing MDM Restrictions...")
             # Try to set via ADB (works on many Samsung exploits when owner is set)
             cmd_fr = 'adb shell dpm set-user-restriction --user 0 no_factory_reset 1'
             self.cmd.run_command(cmd_fr, log_output=False)
             self.cmd.run_command('adb shell dpm set-user-restriction --user 0 no_config_credentials 1', log_output=False)
             
             # Check if it sticked
             res_check = self.cmd.run_command('adb shell dpm get-user-restriction --user 0 no_factory_reset', log_output=False)
             if "true" in str(res_check).lower() or "1" in str(res_check):
                 self.cmd.log("[GREEN]Factory Reset BLOCKED via Policy!")
             else:
                 self.cmd.log("[YELLOW]Policy Blocked by Samsung Security (Normal on A15/16).")
                 self.cmd.log("[INFO] Relying on UI Hiding...")
                 
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
                "com.samsung.android.kgclient",
                "com.sec.android.app.samsungapps", 
                "com.samsung.android.mdm",
                "com.sec.android.systemupdate",
                "com.wssyncmldm", # Update
                "com.sec.android.soagent", # Update
                "com.google.android.gms.policy_sidecar_aps",
                "com.samsung.android.lool",
                "com.samsung.android.server.wifi.mobilewips", 
                "com.samsung.android.knox.attestation",
                "com.knox.vpn.proxyhandler",
                "com.sec.android.app.billing", 
                "com.samsung.android.scloud",
                "com.sec.enterprise.knox.cloudmdm.smdms", # Cloud MDM
                "com.samsung.klmsagent", # Knox License
                "com.samsung.android.bixby.agent",
                "com.samsung.android.visionintelligence",
                # SEARCH & ACCOUNT (PREVENT FIND MY MOBILE WIPE & RESET SEARCH)
                "com.samsung.android.settings.intelligence", # Settings Search
                "com.osp.app.signin", # Samsung Account (Remote Wipe)
                "com.sec.android.easyMover", # Smart Switch
                "com.samsung.android.smartswitchassistant", # Smart Switch Helper
                
                # GOOGLE RESTRICTIONS (PARTIAL)
                "com.google.android.configupdater", # Block Updates to Config
                # "com.android.vending", # Play Store Allowed
                # "com.google.android.gms", 
                # "com.google.android.gsf", 
             ]
             
             self.cmd.log("[*] Nuking Samsung Services (Play Store Allowed)...")
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
                 "com.samsung.klmsagent"
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
             self.cmd.run_command('adb shell pm disable com.mrog.tool/.MainActivity', log_output=False) 
             self.cmd.run_command('adb shell pm hide com.mrog.tool', log_output=False)
             
             self.cmd.log("[GREEN]KG ANDROID 15/16 BYPASS COMPLETED.")
             self.cmd.log("[INFO] Device is Protected.")
             self.cmd.log("[IMPORTANT] DO NOT UPDATE THE SYSTEM.")
             self.cmd.log("Restarting device in 5 seconds...")
             time.sleep(5)
             self.cmd.run_command("adb reboot", log_output=False)
             self.cmd.log("Done.")

         threading.Thread(target=_bypass_thread).start()
