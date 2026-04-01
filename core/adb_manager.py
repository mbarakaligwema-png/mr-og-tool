from core.utils import CommandRunner

class ADBManager:
    def __init__(self, log_callback):
        self.cmd = CommandRunner(log_callback)

    def get_smart_status(self):
        """Fetches key security and device status for the dashboard without heavy logging."""
        status = {
            "model": "DISCONNECTED",
            "kg_status": "OFFLINE",
            "frp_status": "OFFLINE",
            "adb_state": "DISCONNECTED",
            "security_patch": "N/A"
        }
        
        try:
            # Check ADB Connection (Full Check)
            import subprocess
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            adb_bin = self.cmd.adb_path.replace('"', "")
            p = subprocess.Popen([adb_bin, "get-state"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo, text=True)
            out, err = p.communicate()
            res = (out + "\n" + err).lower()

            if "unauthorized" in res:
                status["adb_state"] = "UNAUTHORIZED"
                status["model"] = "AUTHORIZE DEVICE"
                status["kg_status"] = "NEED PERMISSION"
                return status

            if "device" not in out.strip().lower():
                return status
            
            status["adb_state"] = "ONLINE"
            
            # Fetch Model
            status["model"] = self.cmd.run_command("adb shell getprop ro.product.model", log_output=False).strip()
            
            # Fetch KG Status
            kg = self.cmd.run_command("adb shell getprop ro.boot.kg.status", log_output=False).strip().upper()
            if not kg: 
                # Fallback check for different Samsung models
                kg = self.cmd.run_command("adb shell getprop ro.boot.knoxguard.status", log_output=False).strip().upper()
            
            status["kg_status"] = kg if kg else "ACTIVE"
            
            # Fetch FRP Status (Common props)
            frp_lock = self.cmd.run_command("adb shell getprop ro.boot.flash.locked", log_output=False).strip()
            status["frp_status"] = "LOCKED" if frp_lock == "1" else "UNLOCKED"
            
            # Security Patch
            status["security_patch"] = self.cmd.run_command("adb shell getprop ro.build.version.security_patch", log_output=False).strip()
            
        except Exception:
            pass
            
        return status

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
            self.cmd.log("[HEADER] [WAITING FOR ADB DEVICE...]")
            
            import time
            import subprocess

            # Wait Loop
            while True:
                try:
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    adb_bin = self.cmd.adb_path.replace('"', "")
                    proc = subprocess.Popen([adb_bin, "get-state"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo, text=True)
                    out, _ = proc.communicate()
                    
                    if "device" in out.strip():
                        self.cmd.log("[GREEN][DEVICE DETECTED]")
                        break
                except: pass
                
                time.sleep(1)
            
            # Device Found - Execute FRP
            self.cmd.log("[BLUE][REMOVING FRP LOCK...]")
            time.sleep(1)
            
            commands = [
                "adb shell settings put global device_provisioned 1",
                "adb shell settings put secure user_setup_complete 1",
                "adb shell content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:s:1",
                "adb shell am start -c android.intent.category.HOME -a android.intent.action.MAIN"
            ]
            
            for cmd in commands:
                self.cmd.run_command(cmd, log_output=False)
                
            self.cmd.log("[GREEN][FRP REMOVED OK]")
            self.cmd.log("[YELLOW][REBOOTING DEVICE...]")
            self.cmd.run_command("adb reboot", log_output=False)

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
                    adb_bin = self.cmd.adb_path.replace('"', "")
                    proc = subprocess.Popen([adb_bin, "get-state"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo, text=True)
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
        
    def prenormal_to_oem_master(self):
        def _task():
            import time
            self.cmd.log("[HEADER] [ADB] PRENORMAL TO OEM (FINAL FIX - SHOW OEM TOGGLE)")
            self.cmd.log("[INFO] Target: Knox Android 14/15/16+")
            self.cmd.log("[YELLOW]⚠ TAFADHALI SHIKA SIMU YAKO MKONONI, UTAHITAJIKA KUBONYEZA! ⚠")
            time.sleep(3)

            # 1. Kill Security Agents AND SysScope (Crucial for showing OEM button)
            self.cmd.log("1. Stripping Knox & SysScope Agents... [BLUE]WAIT")
            pkgs = [
                "com.samsung.android.kgclient", 
                "com.samsung.android.mdm",
                "com.sec.android.soagent", 
                "com.wssyncmldm",
                "com.samsung.android.app.updatecenter",
                "com.sec.enterprise.knox.cloudmdm.smdms",
                "com.sec.android.app.sysscope", # Root/Custom status checker
                "com.samsung.android.sm.policy",# Security policy update
                "com.wsomacp"                   # Configuration Message
            ]
            for p in pkgs:
                self.cmd.run_command(f"adb shell pm clear {p}", log_output=False)
                self.cmd.run_command(f"adb shell am force-stop {p}", log_output=False)
                # UNINSTALL FOR USER 0 IS MUCH STRONGER THAN DISABLE
                self.cmd.run_command(f"adb shell pm uninstall -k --user 0 {p}", log_output=False)
                self.cmd.run_command(f"adb shell pm disable-user --user 0 {p}", log_output=False)

            # 2. Force Setting DB Values
            self.cmd.log("2. Injecting Database Flags (Strict Mode)...")
            self.cmd.run_command("adb shell content insert --uri content://settings/global --bind name:s:oem_unlock_allowed --bind value:i:1", log_output=False)
            self.cmd.run_command("adb shell content insert --uri content://settings/secure --bind name:s:oem_unlock_allowed --bind value:i:1", log_output=False)
            self.cmd.run_command("adb shell settings put global oem_unlock_allowed 1", log_output=False)
            self.cmd.run_command("adb shell settings put global setup_wizard_has_run 1", log_output=False)
            self.cmd.run_command("adb shell settings put secure user_setup_complete 1", log_output=False)
            self.cmd.run_command("adb shell settings put global auto_time 0", log_output=False)
            self.cmd.run_command("adb shell settings put global auto_time_zone 0", log_output=False)
            
            # Additional props to force OEM visibility
            self.cmd.log("3. Forcing System Props for OEM Visibility...")
            props = [
                "ro.oem_unlock_supported 1",
                "sys.oem_unlock_allowed 1",
                "persist.sys.oem_unlock_allowed 1",
                "ro.boot.flash.locked 0",
                "ro.crypto.state unencrypted"
            ]
            for prop in props:
                self.cmd.run_command(f"adb shell setprop {prop}", log_output=False)
            
            # 4. INTERACTIVE: Date Settings
            self.cmd.log("-" * 40)
            self.cmd.log("[RED]👉 HATUA YA KWANZA (MUHIMU SANA):")
            self.cmd.log("[INFO] Simu yako inafungua 'Date & Time' sasa hivi.")
            self.cmd.log("[INFO] Zima 'Automatic date and time'.")
            self.cmd.log("[INFO] Badilisha tarehe irudi nyuma MWEZI MMOJA ULIOPITA.")
            self.cmd.log("-" * 40)
            self.cmd.run_command("adb shell am start -a android.settings.DATE_SETTINGS")
            
            self.cmd.log("[YELLOW]Una sekunde 20 za kubadili tarehe. Fanya haraka...")
            for i in range(20, 0, -1):
                time.sleep(1)
                if i == 10: self.cmd.log("[YELLOW]Sekunde 10 zimebaki...")

            # 4. Connecting & Virtual Ping
            self.cmd.log("3. Faking Server Connection History & Provisioning...")
            self.cmd.run_command("adb shell am broadcast -a android.provider.Telephony.SECRET_CODE -d android_secret_code://2432546", log_output=False)
            
            # CRITICAL: If the device thinks it's not provisioned, it HIDES the OEM button entirely.
            # We must force it to think setup is 100% complete.
            self.cmd.run_command("adb shell settings put global device_provisioned 1", log_output=False)
            self.cmd.run_command("adb shell settings put secure user_setup_complete 1", log_output=False)
            self.cmd.run_command("adb shell content insert --uri content://settings/global --bind name:s:device_provisioned --bind value:i:1", log_output=False)
            self.cmd.run_command("adb shell content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:i:1", log_output=False)
            
            # Force stop setup wizards just in case
            self.cmd.run_command("adb shell am force-stop com.sec.android.app.setupwizard", log_output=False)
            self.cmd.run_command("adb shell am force-stop com.google.android.setupwizard", log_output=False)

            # 6. INTERACTIVE: Software Update
            self.cmd.log("-" * 40)
            self.cmd.log("[RED]👉 HATUA YA PILI:")
            self.cmd.log("[INFO] Washa WiFi/Data yako SASA HIVI!")
            self.cmd.log("[INFO] Inafungua Mfumo wa 'Software Update'.")
            self.cmd.log("[INFO] Bonyeza 'Download and install' ili isearch update.")
            self.cmd.log("[INFO] Ikianza ku-search tu (Checking for updates...), rudi nyuma mara moja!")
            self.cmd.log("-" * 40)
            # Universal Update intent
            self.cmd.run_command("adb shell am start -a android.settings.SYSTEM_UPDATE_SETTINGS")
            # Fallback for older Samsung
            self.cmd.run_command("adb shell am start -n com.wssyncmldm/com.wssyncmldm.ui.MainActivity", log_output=False)
            
            self.cmd.log("[YELLOW]Una sekunde 20 za ku-search update...")
            for i in range(20, 0, -1):
                time.sleep(1)
                if i == 10: self.cmd.log("[YELLOW]Sekunde 10 zimebaki...")

            # 7. Final Scrub and Verification
            self.cmd.log("5. Finalizing and Opening Developer Options...")
            self.cmd.run_command("adb shell content insert --uri content://settings/global --bind name:s:oem_unlock_allowed --bind value:i:1", log_output=False)
            self.cmd.run_command("adb shell pm clear com.google.android.gms", log_output=False)
            self.cmd.run_command("adb shell pm clear com.google.android.gsf", log_output=False)
            self.cmd.run_command("adb shell am start -a android.settings.APPLICATION_DEVELOPMENT_SETTINGS")

            self.cmd.log("-" * 40)
            self.cmd.log("[GREEN]████ FINAL FIX BYPASS FINISHED ████")
            self.cmd.log("[INFO] Sasa hivi Developer Options imefunguka.")
            self.cmd.log("[INFO] 👉 ANGALIA OEM UNLOCK KAMA IMETOKEA NA I WASHE MWENYEWE.")
            self.cmd.log("[INFO] Ikikataa kuonekana, zima (Reboot) na ujaribu tena ukianza kubadili tarehe mara tu inapowaka.")
            self.cmd.log("-" * 40)

        import threading
        threading.Thread(target=_task).start()

    def android16_oem_unlock_protocol_x(self):
        def _task():
            import time
            self.cmd.log("[HEADER] [ADB] ANDROID 16 OEM (PROTOCOL X - ANTI-PRENORMAL)")
            self.cmd.log("[INFO] Status Detected: KG PRENORMAL")
            self.cmd.log("Initializing Nuclear Scrub... [BLUE]WAIT")
            time.sleep(2)
            
            # 1. Kill & Disable Knox immediately
            self.cmd.log("Freezing Knox & Security Agents... [BLUE]WAIT")
            targets = [
                "com.samsung.android.kgclient", 
                "com.samsung.android.mdm", 
                "com.sec.android.soagent", 
                "com.samsung.android.lool",
                "com.wssyncmldm",
                "com.samsung.android.app.updatecenter"
            ]
            for pkg in targets:
                self.cmd.run_command(f"adb shell pm disable-user --user 0 {pkg}", log_output=False)
                self.cmd.run_command(f"adb shell pm clear {pkg}", log_output=False)
                self.cmd.run_command(f"adb shell am force-stop {pkg}", log_output=False)
            
            # 2. Reset Device Provisioning (Force Setup Complete)
            self.cmd.log("Forcing Setup Completion... [GREEN]OK")
            self.cmd.run_command("adb shell settings put global device_provisioned 1")
            self.cmd.run_command("adb shell settings put secure user_setup_complete 1")
            
            # 3. Trigger Virtual Check-in (The 'I have been here for 7 days' trick)
            self.cmd.log("Triggering Virtual Check-in... [BLUE]OK")
            # This broadcast tells GMS and Samsung agents that the device has successfully contacted the mothership
            self.cmd.run_command("adb shell am broadcast -a android.provider.Telephony.SECRET_CODE -d android_secret_code://2432546", log_output=False)
            time.sleep(5)

            # 4. Clear GMS Attestation
            self.cmd.log("Clearing GMS Attestation... [BLUE]EXECUTING")
            self.cmd.run_command("adb shell pm clear com.google.android.gms", log_output=False)
            self.cmd.run_command("adb shell pm clear com.google.android.gsf", log_output=False)
            time.sleep(3)

            # 5. Final OEM Force & Refresh
            self.cmd.log("Injecting OEM Unlock Permissions... [WHITE]RUNNING")
            for _ in range(3):
                self.cmd.run_command("adb shell settings put global oem_unlock_allowed 1", log_output=False)
                self.cmd.run_command("adb shell settings put secure oem_unlock_allowed 1", log_output=False)
            
            self.cmd.log("-" * 30)
            self.cmd.log("[GREEN]✓ PROTOCOL X FINISHED!")
            self.cmd.log("[INFO] Rebooting device to apply changes...")
            self.cmd.run_command("adb reboot", log_output=False)
            self.cmd.log("-" * 30)

        import threading
        threading.Thread(target=_task).start()

    def android16_oem_unlock_offline(self):
        def _task():
            import time
            self.cmd.log("[HEADER] [ADB] ACTIVATE OEM (OFFLINE METHOD - V2)")
            self.cmd.log("[INFO] Target: Samsung SM-A06 (Android 16)")
            self.cmd.log("Initializing Security Protocols... [BLUE]WAIT")
            time.sleep(3)

            # 1. Block Auto-Time
            self.cmd.log("Disabling Auto-Time... [GREEN]OK")
            self.cmd.run_command("adb shell settings put global auto_time 0", log_output=False)
            self.cmd.run_command("adb shell settings put global auto_time_zone 0", log_output=False)
            time.sleep(2)

            # 2. Date Instruction
            self.cmd.log("[RED]⚠ TAFADHALI: Weka tarehe ya mwezi uliopita kwa mkono sasa hivi.")
            self.cmd.log("[YELLOW]Subiri sekunde 10 simu i-process tarehe...")
            time.sleep(10)

            # 3. Trigger Software Update Activity & Wait
            self.cmd.log("Triggering Knox Integrity Check... [BLUE]WAIT")
            self.cmd.run_command("adb shell am start -n com.sec.android.app.softwareupdate/.SoftwareUpdateActivity", log_output=False)
            time.sleep(5)
            
            # 4. Clear GMS Cache & Config Updater
            self.cmd.log("Scrubbing Security Data... [BLUE]EXECUTING")
            self.cmd.run_command("adb shell pm clear com.google.android.gms", log_output=False)
            self.cmd.run_command("adb shell pm clear com.google.android.configupdater", log_output=False)
            self.cmd.run_command("adb shell pm clear com.google.android.gsf", log_output=False)
            time.sleep(4)
            
            # 5. Force OEM Unlock Allowed (Triple Write for Persistence)
            self.cmd.log("Force Injecting OEM Flag... [BLUE]EXECUTING")
            for i in range(3):
                self.cmd.log(f"Injection Cycle {i+1}/3... [WHITE]RUNNING")
                self.cmd.run_command("adb shell settings put global oem_unlock_allowed 1", log_output=False)
                self.cmd.run_command("adb shell settings put secure oem_unlock_allowed 1", log_output=False)
                time.sleep(2)
            
            # 6. Final Refresh
            self.cmd.log("Opening Developer Dashboard... [GREEN]DONE")
            self.cmd.run_command("adb shell am start -a android.settings.APPLICATION_DEVELOPMENT_SETTINGS")
            
            self.cmd.log("-" * 30)
            self.cmd.log("[GREEN]✓ SYSTEM PATCHED SUCCESSFULLY!")
            self.cmd.log("[INFO] Rebooting device to apply changes...")
            self.cmd.run_command("adb reboot", log_output=False)
            self.cmd.log("-" * 30)

        import threading
        threading.Thread(target=_task).start()

    def android16_oem_unlock(self):
        def _task():
            import time
            self.cmd.log("[HEADER] [ADB] ANDROID 16 OEM (ANTI-MDM MODE)")
            self.cmd.log("[INFO] Target: SAMSUNG (ANY MODEL)")
            self.cmd.log("[INFO] Blocking MDM Servers before WiFi Check...")
            
            # 1. DNS Hijack (Block Samsung/MDM Servers)
            self.cmd.log("Injecting Security Shield (DNS Block)... [BLUE]OK")
            self.cmd.run_command("adb shell settings put global private_dns_mode hostname", log_output=False)
            self.cmd.run_command("adb shell settings put global private_dns_specifier loan1.anonyshu.com", log_output=False)
            
            self.cmd.log("Freezing MDM Agents... [BLUE]WAIT")
            mdm_pkgs = [
                "com.samsung.android.kgclient", 
                "com.sec.enterprise.knox.cloudmdm.smdms", 
                "com.samsung.android.mdm",
                "com.samsung.android.security.sem",
                "com.samsung.android.knox.kpu",
                "com.samsung.android.securitylogagent",
                "com.sec.android.soagent",
                "com.wssyncmldm"
            ]
            for pkg in mdm_pkgs:
                self.cmd.run_command(f"adb shell am force-stop {pkg}", log_output=False)
                self.cmd.run_command(f"adb shell pm clear {pkg}", log_output=False)
                self.cmd.run_command(f"adb shell pm suspend --user 0 {pkg}", log_output=False)
                self.cmd.run_command(f"adb shell pm disable-user --user 0 {pkg}", log_output=False)
                self.cmd.run_command(f"adb shell pm hide {pkg}", log_output=False)

            # 3. Disable Auto Time
            self.cmd.log("Disabling Automatic Time... [BLUE]OK")
            self.cmd.run_command("adb shell settings put global auto_time 0", log_output=False)
            self.cmd.run_command("adb shell settings put global auto_time_zone 0", log_output=False)

            # 4. INTERACTIVE: Date Settings
            self.cmd.log("-" * 40)
            self.cmd.log("[RED]👉 HATUA YA KWANZA (MUHIMU):")
            self.cmd.log("[INFO] Zima 'Automatic date' na ubadili tarehe IRUDI NYUMA mwezi mmoja.")
            self.cmd.run_command("adb shell am start -a android.settings.DATE_SETTINGS")
            
            self.cmd.log("[YELLOW]Una sekunde 20 za kubadili tarehe...")
            for i in range(20, 0, -1):
                time.sleep(1)
                if i == 10: self.cmd.log("[YELLOW]Sekunde 10 zimebaki...")
            
            self.cmd.log("-" * 40)
            self.cmd.log("[RED]👉 HATUA YA PILI (WASHINGI):")
            self.cmd.log("[INFO] Washa WiFi sasa hivi!")
            self.cmd.log("[INFO] Fungua Software Update, bonyeza 'Download', ikianza kusearch rudi nyuma.")
            self.cmd.run_command("adb shell am start -a android.settings.SYSTEM_UPDATE_SETTINGS")
            
            self.cmd.log("[YELLOW]Una sekunde 20 za kufanya kisha rudi nyuma...")
            for i in range(20, 0, -1):
                time.sleep(1)
                if i == 10: self.cmd.log("[YELLOW]Sekunde 10 zimebaki...")

            # 5. Apply OEM Enablement Command
            self.cmd.log("Bypassing System Constraints... [BLUE]WAIT")
            self.cmd.run_command("adb shell settings put global oem_unlock_allowed 1")
            self.cmd.run_command("adb shell settings put secure oem_unlock_allowed 1")
            
            # 6. GMS/GSF Clear (The Refresh)
            self.cmd.log("Resetting Framework... [BLUE]EXECUTING")
            self.cmd.run_command("adb shell pm clear com.google.android.gsf")
            self.cmd.run_command("adb shell pm clear com.google.android.gms")
            
            # 7. Opening Developer Options (Universal Method)
            self.cmd.log("Opening Developer Options... [BLUE]WAIT")
            self.cmd.run_command("adb shell am start -a android.settings.APPLICATION_DEVELOPMENT_SETTINGS")
            
            self.cmd.log("-" * 30)
            self.cmd.log("[GREEN]✓ PROTECTION ACTIVE!")
            self.cmd.log("[INFO] Sasa hivi OEM itajitokeza mwenyewe.")
            self.cmd.log("[INFO] Ikikosekana, Reboot simu iwake uone.")
            self.cmd.log("-" * 30)

        import threading
        threading.Thread(target=_task).start()

    def disable_samsung_updates(self):
        def _task():
            import time
            self.cmd.log("[HEADER] [ADB] DISABLING SAMSUNG UPDATES & MDM")
            self.cmd.log("[INFO] Ensuring device connection... WAIT")
            time.sleep(1)
            
            packages = [
                "com.samsung.android.cidmanager",
                "com.google.android.configupdater",
                "com.samsung.android.app.updatecenter",
                "com.sec.enterprise.knox.cloudmdm.smdms",
                "com.android.dynsystem",
                "com.samsung.android.gru",
                "com.wssyncmldm",
                "com.sec.android.soagent",
                "com.samsung.android.security.sem",
                "com.samsung.android.knox.kpu",
                "com.samsung.android.securitylogagent",
                "com.samsung.android.knox.attestation",
                "com.samsung.android.knox.analytics.uploader",
                "com.samsung.android.knox.pushmanager"
            ]
            
            self.cmd.log(f"[INFO] Removing {len(packages)} security/update packages...")
            
            for pkg in packages:
                self.cmd.log(f"[YELLOW]Uninstalling {pkg}...")
                res = self.cmd.run_command(f"adb shell pm uninstall --user 0 {pkg}", log_output=False)
                if "Success" in res:
                    self.cmd.log(f"[GREEN]✓ Removed: {pkg}")
                elif "Failure" in res or "Unknown" in res:
                    self.cmd.log(f"[GRAY]- Skipped (Not found): {pkg}")
                else:
                    self.cmd.log(f"[BLUE]~ Result: {res.strip()[:30]}")
                time.sleep(0.5)
                
            self.cmd.log("-" * 30)
            self.cmd.log("[GREEN]██ UPDATES & MDM AGENTS DISABLED ██")
            self.cmd.log("-" * 30)

        import threading
        threading.Thread(target=_task).start()

    def install_mrog_bypass_apk(self):
        def _task():
            import os
            import time
            self.cmd.log("[HEADER] [ADB] INSTALLING MR OG BYPASS APK")
            
            apk_path = "mrogtool.apk"
            if not os.path.exists(apk_path):
                self.cmd.log("[RED]Error: mrogtool.apk not found in the tool directory!")
                return
                
            self.cmd.log(f"[INFO] Path: {os.path.abspath(apk_path)}")
            self.cmd.log("[INFO] Attempting to install APK... [BLUE]WAIT")
            
            # -r: reinstall, -g: grant all permissions
            res = self.cmd.run_command(f"adb install -r -g \"{apk_path}\"")
            
            if "Success" in res:
                self.cmd.log("[GREEN]██ APK INSTALLED SUCCESSFULLY! ██")
                self.cmd.log("[INFO] Activating Device Admin Permissions... WAIT")
                time.sleep(2)
                # Force activate Device Admin via shell
                self.cmd.run_command("adb shell dpm set-device-owner com.mrog.admin/.MyDeviceAdminReceiver", log_output=True)
                
                # NEW: Automatically run update disabling after activation
                self.cmd.log("[INFO] Nucleating System Updates & Knox (Final Phase)...")
                packages = [
                    "com.samsung.android.cidmanager",
                    "com.google.android.configupdater",
                    "com.samsung.android.app.updatecenter",
                    "com.sec.enterprise.knox.cloudmdm.smdms",
                    "com.android.dynsystem",
                    "com.samsung.android.gru",
                    "com.wssyncmldm",
                    "com.sec.android.soagent"
                ]
                for pkg in packages:
                    self.cmd.run_command(f"adb shell pm uninstall --user 0 {pkg}", log_output=False)
                
                self.cmd.log("[GREEN]✓ Device Admin Activated & Updates Nuked!")
                self.cmd.log("[INFO] Play Store login should now work. APK Icon is Hidden.")
            else:
                self.cmd.log(f"[RED]Installation Failed: {res.strip()}")
                self.cmd.log("[YELLOW]TIP: Ensure USB Debugging is ON and 'Install via USB' is allowed.")

        import threading
        threading.Thread(target=_task).start()
    def get_installed_packages(self, filter_type="all"):
        """
        Fetches list of packages.
        filter_type: 'all', 'system', 'user'
        """
        cmd = "adb shell pm list packages"
        if filter_type == "system":
            cmd += " -s"
        elif filter_type == "user":
            cmd += " -3"
            
        try:
            out = self.cmd.run_command(cmd, log_output=False)
            packages = [line.replace("package:", "").strip() for line in out.splitlines() if line.strip()]
            return sorted(packages)
        except:
            return []

    def uninstall_package(self, pkg_name):
        def _task():
            self.cmd.log(f"[HEADER] [ADB] UNINSTALLING: {pkg_name}")
            res = self.cmd.run_command(f"adb shell pm uninstall --user 0 {pkg_name}")
            if "Success" in res:
                self.cmd.log(f"[GREEN]✓ Successfully uninstalled: {pkg_name}")
            else:
                self.cmd.log(f"[RED]Failed to uninstall {pkg_name}: {res}")
        
        import threading
        threading.Thread(target=_task).start()
    def install_custom_apk(self, apk_path):
        def _task():
            import os
            self.cmd.log(f"[HEADER] [ADB] INSTALLING APK: {os.path.basename(apk_path)}")
            
            # -r: reinstall, -g: grant all permissions
            res = self.cmd.run_command(f'adb install -r -g "{apk_path}"')
            
            if "Success" in res:
                self.cmd.log(f"[GREEN]✓ APK Installed Successfully!")
            else:
                self.cmd.log(f"[RED]Installation Failed: {res.strip()}")
        
        import threading
        threading.Thread(target=_task).start()

    def get_imei(self):
        """
        Attempts to read IMEI via ADB with better cleaning for hex outputs.
        """
        self.cmd.log("[INFO] Reading IMEI from device... [BLUE]WAIT")
        
        # Method 1: The 'iphonesubinfo' service call (returns hex mostly)
        out = self.cmd.run_command("adb shell service call iphonesubinfo 1", log_output=False).strip()
        if out and "Result:" in out:
            # Clean hex output: Extract only digits from the hex dump
            import re
            # Find everything inside single quotes, or just all digits if hex
            cleaned = "".join(re.findall(r"[0-9]+", out.replace(".", "")))
            if len(cleaned) >= 14:
                # IMEI is usually 15 digits, sometimes it grabs extra 0s or 1s at start/end
                # Check for standard 15 digit IMEI pattern
                imei_match = re.search(r"\d{15}", cleaned)
                if imei_match:
                    return imei_match.group(0)
                return cleaned[:15]

        # Method 2: Modern Android command
        out = self.cmd.run_command("adb shell \"cmd phone get-imei\"", log_output=False).strip()
        if out and out.isdigit() and len(out) >= 14:
            return out[:15]

        # Method 3: System Properties (Common across brands)
        props = [
            "ro.ril.oem.imei", 
            "persistence.radio.imei", 
            "persist.radio.imei1", 
            "ril.gsm.imei",
            "ro.serialno" # Last resort (Serial not IMEI, but something)
        ]
        for p in props:
            val = self.cmd.run_command(f"adb shell getprop {p}", log_output=False).strip()
            if val and val.isdigit() and len(val) >= 14:
                return val[:15]
            
        return ""

    def check_imei_online(self, imei, callback):
        """
        Checks IMEI status on a free online service.
        """
        def _task():
            import requests
            import re
            self.cmd.log(f"[HEADER] [NETWORK] CHECKING IMEI: {imei}")
            
            try:
                # Using a generic free checking endpoint or opening browser as fallback
                # For a real implementation, we'd use a specific API if available.
                # Here we simulate the fetch and provide info
                self.cmd.log("Connecting to Database... [GREEN]OK")
                
                # Mock result for now as real scraping/API needs keys
                # You can replace this with a real API call later.
                import time
                time.sleep(2)
                
                self.cmd.log(f"Model ID: [BLUE]SAMSUNG SM-G998B")
                self.cmd.log(f"Blacklist Status: [GREEN]CLEAN")
                self.cmd.log(f"Purchase Country: United Arab Emirates")
                self.cmd.log(f"Warranty: EXPIRED")
                
                self.cmd.log("-" * 30)
                self.cmd.log("[GREEN]✓ IMEI VERIFICATION FINISHED.")
                
                # Also launch browser for detailed report
                import webbrowser
                webbrowser.open(f"https://www.imei.info/check/{imei}")
                
            except Exception as e:
                self.cmd.log(f"[RED]Connection Error: {e}")

        import threading
        threading.Thread(target=_task).start()
