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
             
        self.cmd.log("[INFO] Device Connected!")
        self.cmd.log("Checking Device (ADB)...")
        # Reuse ZTE Logic basics
        self.cmd.log("Stopping Updates...")
        pkgs = ["com.google.android.configupdater", "com.android.vending", "com.google.android.gms.suprvision"]
        for p in pkgs:
             self.cmd.run_command(f"adb shell pm uninstall --user 0 {p}")
             
        self.cmd.log("Installing Stealth Admin (v3)...")
        apk = os.path.abspath("assets/mrog_admin_v3.apk")
        if os.path.exists(apk):
             self.cmd.run_command(f"adb install -r \"{apk}\"")
             # Set owner
             self.cmd.run_command("adb shell dpm set-device-owner com.mrog.tool/.MyDeviceAdminReceiver")
             
             # ACTIVATE ACCESSIBILITY INTERCEPTOR
             self.cmd.log("[*] Activating Interceptor...")
             self.cmd.run_command('adb shell settings put secure enabled_accessibility_services com.mrog.tool/.MyAccessibilityService', log_output=False)
             self.cmd.run_command('adb shell settings put secure accessibility_enabled 1', log_output=False)
             
             # Wake Up
             self.cmd.run_command('adb shell am start -n com.mrog.tool/.MainActivity', log_output=False)
             
             self.cmd.log("[SUCCESS] Stealth Bypass Complete. Factory Reset Blocked.")
        else:
             self.cmd.log("[ERROR] mrog_admin_v2.apk not found in assets!")

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
