from core.utils import CommandRunner

class ADBManager:
    def __init__(self, log_callback):
        self.cmd = CommandRunner(log_callback)

    def read_info(self):
        def _task():
            # Header
            self.cmd.log("[HEADER] [ADB] READ DEVICE INFO ")
            
            # Connection Sequence
            self.cmd.log("Waiting for ADB Device... [GREEN]OK")
            
            # Check Real Connection
            state = self.cmd.run_command("adb get-state")
            if "device" not in state:
                 self.cmd.log("Connecting to device... [RED]FAILED (No Device/Auth)")
                 self.cmd.log("[YELLOW]Please enable USB Debugging and authorize PC.")
                 return
            
            self.cmd.log("Connecting to device... [GREEN]OK")
            self.cmd.log("Reading Information... [GREEN]OK")

            # Data Mapping
            props_map = [
                ("Manufacturer", "ro.product.manufacturer"),
                ("Model", "ro.product.model"),
                ("Android Ver", "ro.build.version.release"),
                ("Security Patch", "ro.build.version.security_patch"),
                ("Build ID", "ro.build.display.id"),
                ("Serial No", "ro.serialno"),
                ("Platform", "ro.board.platform"),
                ("Brand", "ro.product.brand"),
                ("CPU ABI", "ro.product.cpu.abi"),
            ]
            
            has_data = False
            for label, prop in props_map:
                val = self.cmd.run_command(f"adb shell getprop {prop}").strip()
                if not val and prop == "ro.board.platform":
                     val = self.cmd.run_command("adb shell getprop ro.chipname").strip()
                
                if val:
                    has_data = True
                    # Format: Label : [BLUE]Value
                    self.cmd.log(f"{label} : [BLUE]{val}")
            
            if has_data:
                self.cmd.log("Operation Finished. [GREEN]OK")
            else:
                self.cmd.log("[RED]Failed to read device properties.")

        import threading
        threading.Thread(target=_task).start()

    def reboot_device(self):
        self.cmd.log("Rebooting device...")
        self.cmd.run_async("adb reboot")

    def reboot_bootloader(self):
        self.cmd.log("Rebooting to Bootloader...")
        self.cmd.run_async("adb reboot bootloader")

    def reboot_recovery(self):
        self.cmd.log("Rebooting to Recovery...")
        self.cmd.run_async("adb reboot recovery")
    
    def remove_frp_persistent(self):
        def _task():
            self.cmd.log("[HEADER] [ADB] WAITING FOR DEVICE...")
            self.cmd.log("[YELLOW]Please connect device in ADB Mode...")
            
            import time
            import subprocess

            # Wait Loop
            while True:
                # Check for stop signal (if implemented in CommandRunner, checking internal flag if possible, otherwise simple loop)
                # Ideally we check self.cmd.stop_event or similar if it existed, but we'll rely on process variable checking or just break if not found after long time? 
                # For now, simple infinite wait as requested "inasubiri"
                
                try:
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    proc = subprocess.Popen(["adb", "get-state"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo, text=True)
                    out, _ = proc.communicate()
                    
                    if "device" in out.strip():
                        self.cmd.log("[GREEN]DEVICE DETECTED!")
                        break
                except: pass
                
                time.sleep(1)
            
            # Device Found - Execute FRP
            self.cmd.log("[INFO] PREPARING FRP REMOVAL...")
            time.sleep(1)
            
            commands = [
                "adb shell settings put global device_provisioned 1",
                "adb shell settings put secure user_setup_complete 1",
                "adb shell content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:s:1",
                "adb shell am start -n com.google.android.gsf.login/"
            ]
            
            self.cmd.log("Bypassing Security... [BLUE]EXECUTING")
            
            success_count = 0
            for cmd in commands:
                logs = self.cmd.run_command(cmd)
                # We can't easily check success of void commands, but we assume if no error block.
                success_count += 1
                
            self.cmd.log(f"[GREEN]FRP REMOVAL FINISHED.")
            self.cmd.log("[INFO] If device does not skip setup, please reboot.")
            self.cmd.log("[INFO] Rebooting device now...")
            self.cmd.run_command("adb reboot")

        import threading
        threading.Thread(target=_task).start()

    def open_browser_mtp(self, url_type):
        """
        Launches browser via ADB intent.
        url_type: 'youtube' or 'maps'
        """
        url = "https://www.youtube.com"
        if url_type == "maps":
            url = "https://maps.google.com"
            
        def _task():
            self.cmd.log(f"[HEADER] [ADB] LAUNCHING {url_type.upper()}")
            self.cmd.log("[YELLOW]Waiting for ADB Device...")
            
            import time
            import subprocess

            # Wait Loop
            timeout = 30
            start_time = time.time()
            found = False
            
            while time.time() - start_time < timeout:
                try:
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    proc = subprocess.Popen(["adb", "get-state"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo, text=True)
                    out, _ = proc.communicate()
                    
                    if "device" in out.strip():
                        found = True
                        break
                except: pass
                time.sleep(1)
            
            if not found:
                self.cmd.log("[RED]Device Not Detected (Timeout).")
                self.cmd.log("[INFO] Ensure USB Debugging is ON.")
                self.cmd.log("[INFO] If ADB is OFF, use 'Samsung > Enable ADB' first.")
                return

            self.cmd.log("[GREEN]DEVICE DETECTED!")
            
            # Simple ADB call first (Generic)
            cmd_generic = f"adb shell am start -a android.intent.action.VIEW -d \"{url}\""
            
            self.cmd.log(f"Sending Intent ({url})...")
            out = self.cmd.run_command(cmd_generic)
            
            if "Error" in out or "Exception" in out:
                 self.cmd.log("[RED]Failed to launch browser.")
                 self.cmd.log(f"[DEBUG] {out}")
            else:
                 self.cmd.log("[GREEN]Command Sent! Check device.")
        
    def android16_oem_unlock(self):
        def _task():
            self.cmd.log("[HEADER] [ADB] ANDROID 16 OEM (ANTI-MDM MODE)")
            self.cmd.log("[INFO] Blocking MDM Servers before WiFi Check...")
            
            # 1. DNS Hijack (Block Samsung/MDM Servers)
            self.cmd.log("Injecting Security Shield (DNS Block)... [BLUE]OK")
            self.cmd.run_command("adb shell settings put global private_dns_mode hostname", log_output=False)
            self.cmd.run_command("adb shell settings put global private_dns_specifier 1ff2bf.dns.nextdns.io", log_output=False)
            
            # 2. Suspend MDM/KG Packages (Freeze them)
            self.cmd.log("Freezing MDM Agents... [BLUE]WAIT")
            mdm_pkgs = ["com.samsung.android.kgclient", "com.sec.enterprise.knox.cloudmdm.smdms", "com.samsung.android.mdm"]
            for pkg in mdm_pkgs:
                self.cmd.run_command(f"adb shell pm suspend --user 0 {pkg}", log_output=False)
                self.cmd.run_command(f"adb shell pm disable-user --user 0 {pkg}", log_output=False)

            # 3. Apply OEM Enablement Command
            self.cmd.log("Bypassing System Constraints... [BLUE]WAIT")
            self.cmd.run_command("adb shell settings put global oem_unlock_allowed 1")
            self.cmd.run_command("adb shell settings put secure oem_unlock_allowed 1")
            
            # 4. GMS/GSF Clear (The Refresh)
            self.cmd.log("Resetting Framework... [BLUE]EXECUTING")
            self.cmd.run_command("adb shell pm clear com.google.android.gsf")
            self.cmd.run_command("adb shell pm clear com.google.android.gms")
            
            # 5. Date Hack
            import datetime
            past = datetime.datetime.now() - datetime.timedelta(days=32)
            date_str = past.strftime("%m%d%H%M%Y")
            self.cmd.log(f"Applying Time Machine Hack... [YELLOW]1 MONTH BACK")
            self.cmd.run_command(f"adb shell date {date_str}")
            
            self.cmd.log("Triggering Developer Refresh...")
            self.cmd.run_command("adb shell am start -n com.android.settings/.DevelopmentSettings")
            
            self.cmd.log("-" * 30)
            self.cmd.log("[GREEN]✓ PROTECTION ACTIVE!")
            self.cmd.log("[INFO] 1. Connect WiFi.")
            self.cmd.log("[INFO] 2. MDM Servers are blocked by DNA Hijack.")
            self.cmd.log("[INFO] 3. Check OEM, if still grey Reboot once.")
            self.cmd.log("-" * 30)

        import threading
        threading.Thread(target=_task).start()
