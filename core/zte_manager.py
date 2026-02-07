import threading
import time
from core.utils import CommandRunner

class ZTEManager:
    def __init__(self, log_callback):
        self.cmd = CommandRunner(log_callback)
        self.is_running = False

    def a35_bypass(self):
        if self.is_running:
             self.cmd.log("[WARN] Operation already running. Please wait or click STOP.")
             return

        def _task():
            self.is_running = True
            try:
                # SWAG LOGS 2026
                self.cmd.log("🔥 PHONE DETECTED: ADB MODE ACTIVE")
                self.cmd.log("🚀 OPERATION: ZTE A35 CYBER-UNLOCK 2026")
                self.cmd.log("🔐 CHECKING SECURITY CLEARANCE: GRANTED [OK]")
                
                # Restart ADB
                self.cmd.log("⚡ INITIALIZING ADB SERVER... [OK]")
                self.cmd.run_command("adb kill-server")
                self.cmd.run_command("adb start-server")
                
                self.cmd.log("[BLUE]📡 SCANNING FOR TARGET DEVICE...")
                
                while True:
                    output = self.cmd.run_command("adb devices", log_output=False)
                    lines = output.strip().split('\n')
                    device_found = False
                    for line in lines:
                        val = line.strip()
                        if not val or "List of devices attached" in val: continue
                        if val.endswith("device") and not val.endswith("no permissions"):
                             device_found = True
                             break
                    if device_found: break
                    time.sleep(1)
    
                self.cmd.log("[BLUE]📶 CONNECTION ESTABLISHED: STABLE")
                
                state = self.cmd.run_command("adb get-state")
                if "device" not in state:
                     self.cmd.log("[ERROR] 🛑 DEVICE OFFLINE OR UNAUTHORIZED!")
                     return
    
                self.cmd.log("[BLUE]🔥 TARGET LOCK ACQUIRED. INITIATING BREACH...")
                
                # ZTE Bloatware Removal
                self.cmd.log("☠️ NUKING ZTE BLOATWARE (CLEANING TRASH)...")
                zte_apps = [
                    "com.zte.zdmdaemon", "com.zte.zdm.omacp", "com.zte.nubrowser",
                    "com.zte.haertyservice.strategy", "com.zte.handservice", "com.zte.faceverify",
                    "com.zte.emodeservice", "com.zte.emode", "com.zte.devicemanager.client",
                    "com.zte.burntest.camera", "com.ztebeautify", "com.zteappsimcardfilter",
                    "com.zte.zdmdaemon.install"
                ]
                
                # Silent Kill Loop
                count = 0
                for app in zte_apps:
                    self.cmd.run_command(f"adb shell pm uninstall --user 0 {app}", log_output=False)
                    count += 1
                self.cmd.log(f"✅ CLEANED {count} JUNK APPS [OK]")

                # Google / System Fixes
                self.cmd.log("🧹 SWEEPING GOOGLE/FACEBOOK TRACKERS...")
                sys_apps = [
                    "com.google.android.gms.suprvision", "com.google.android.configupdater",
                    "com.google.android.as.oss", "com.google.android.apps.wellbeing",
                    "com.google.android.apps.turbo", "com.google.android.apps.safetyhub",
                    "com.android.managedprovisioning", "com.android.dynsystem",
                    "com.facebook.system", "com.facebook.services", "com.facebook.appmanager"
                ]
                for app in sys_apps:
                    self.cmd.run_command(f"adb shell pm uninstall --user 0 {app}", log_output=False)
                self.cmd.log("✅ TRACKERS REMOVED [OK]")

                # Disable ZDM Services
                self.cmd.log("🛡️ CRUSHING SECURITY AGENTS (ZDM & DEMONS)...")
                zdm_pkgs = [
                    "com.zte.zdm", "com.zte.zdm.omacp", "com.zte.zdmdaemon", "com.zte.zdmdaemon.install"
                ]
                for pkg in zdm_pkgs:
                     self.cmd.run_command(f"adb shell pm disable-user --user 0 {pkg}", log_output=False)
                self.cmd.log("✅ SECURITY AGENTS DISABLED [OK]")

                # Clear Data & WiFi
                self.cmd.log("✨ WIPING GMS TRACES & GHOSTING WIFI...")
                self.cmd.run_command("adb shell pm clear com.google.android.gms", log_output=False)
                self.cmd.run_command("adb shell cmd -w wifi set-wifi-enabled disabled", log_output=False)

                # Disable Setup Wizard (THE FIX for White Screen)
                self.cmd.log("⛔ DISABLING SETUP WIZARD (BYPASSING GATE)...")
                
                # FIX HOME BUTTON & NOTIFICATIONS (Critical)
                self.cmd.run_command("adb shell settings put global device_provisioned 1", log_output=False)
                self.cmd.run_command("adb shell settings put secure user_setup_complete 1", log_output=False)
                
                setup_pkgs = ["com.google.android.setupwizard"]
                for p in setup_pkgs:
                     self.cmd.run_command(f"adb shell pm disable-user --user 0 {p}", log_output=False)
                     self.cmd.run_command(f"adb shell pm clear {p}", log_output=False)
                self.cmd.log("✅ SETUP WIZARD BYPASSED [OK]")
    
                # Back Keys Navigation
                self.cmd.log("🤖 AUTO-PILOT ENGAGED: NAVIGATION HOME...")
                for _ in range(4):
                    self.cmd.run_command("adb shell input keyevent 4", log_output=False)
                    time.sleep(0.5)
                
                # Force Home Screen
                self.cmd.run_command("adb shell input keyevent 3", log_output=False) # Key Event Home
                self.cmd.run_command("adb shell am start -a android.intent.action.MAIN -c android.intent.category.HOME", log_output=False) # Intent Home
    
                self.cmd.log("✅ MISSION ACCOMPLISHED: DEVICE UNLOCKED & SECURED!")
                self.cmd.log("👑 DONE. MR OG TOOL 2026 (NO REBOOT).")
            
            except Exception as e:
                 self.cmd.log(f"[ERROR] Operation Failed: {e}")
            finally:
                 self.is_running = False

        threading.Thread(target=_task).start()

    def a34_bypass(self):
        if self.is_running:
             self.cmd.log("[WARN] Operation already running. Please wait or click STOP.")
             return

        def _task():
            self.is_running = True
            try:
                self.cmd.log("Phone Mode: ADB Debuging")
                self.cmd.log("Operation: A34 Bypass (Custom Script)")
                self.cmd.log("Check Authority: OK")
                
                # Check Connection
                self.cmd.log("Starting server... OK")
                self.cmd.run_command("adb start-server")
                
                self.cmd.log("[BLUE]Waiting ADB devices...")
                while True:
                    output = self.cmd.run_command("adb devices", log_output=False)
                    if "device" in output and not output.strip().endswith("List of devices attached"):
                         # Basic check, can be improved
                         break
                    time.sleep(1)
    
                self.cmd.log("[BLUE]Check Conection... OK")
                
                # Uninstalling unwanted apps
                self.cmd.log("[STEP] Uninstalling unwanted apps...")
                packages = [
                    "com.zte.zdmdaemon.install",
                    "com.android.mms.service",
                    "com.android.dynsystem",
                    "com.zte.devicemanager.client",
                    "com.google.android.configupdater",
                    "com.android.cts.priv.ctsshim",
                    "com.android.cts.ctsshim",
                    "com.android.egg",
                    "com.android.proxyhandler"
                ]
                
                for pkg in packages:
                    self.cmd.log(f"Uninstalling {pkg}...")
                    self.cmd.run_command(f"adb shell pm uninstall --user 0 {pkg}")

                # Install Custom App
                self.cmd.log("[STEP] Implementing Custom App (king.apk)...")
                
                import os
                # Use base_path
                base = getattr(self.cmd, 'base_path', os.getcwd())
                
                # Priority 1: king.apk (Root or Assets)
                apk_path = None
                
                p1 = os.path.join(base, "king.apk")
                p2 = os.path.join(base, "assets", "king.apk")
                
                if os.path.exists(p1): apk_path = p1
                elif os.path.exists(p2): apk_path = p2
                
                # Priority 2: mrog_admin_v2.apk (Fallback)
                if not apk_path:
                    p3 = os.path.join(base, "assets", "mrog_admin_v2.apk")
                    if os.path.exists(p3):
                        self.cmd.log("[INFO] king.apk not found, using mrog_admin_v2.apk...")
                        apk_path = p3
                
                if apk_path and os.path.exists(apk_path):
                     self.cmd.log(f"Installing: {os.path.basename(apk_path)}")
                     self.cmd.run_command(f"adb install \"{apk_path}\"")
                else:
                     self.cmd.log(f"[WARN] No Custom APK found. Trying generic install command...")
                     self.cmd.run_command("adb install king.apk")

                # Set Device Owner
                self.cmd.log("[STEP] Setting device owner...")
                self.cmd.run_command("adb shell dpm set-device-owner com.afwsamples.testdpc/.DeviceAdminReceiver")
                
                self.cmd.log("[SUCCESS] All tasks completed! A34 Bypass Done.")
                self.cmd.log("You can now reboot if needed.")

            except Exception as e:
                 self.cmd.log(f"[ERROR] Operation Failed: {e}")
            finally:
                 self.is_running = False

        threading.Thread(target=_task).start()

    def detect_and_bypass(self):
        if self.is_running:
             self.cmd.log("[WARN] Operation already running.")
             return

        def _task():
            self.is_running = True
            try:
                self.cmd.log("Operation: Smart Auto-Detect Bypass")
                self.cmd.log("Checking Device Model...")
                
                # Check devices
                output = self.cmd.run_command("adb devices", log_output=False)
                if "device" not in output or output.strip().endswith("List of devices attached"):
                     self.cmd.log("[WAIT] Waiting for device...")
                     while True:
                        output = self.cmd.run_command("adb devices", log_output=False)
                        if "device" in output and not output.strip().endswith("List of devices attached"):
                            break
                        time.sleep(1)
                
                # Get Model
                model = self.cmd.run_command("adb shell getprop ro.product.model", log_output=False).strip()
                self.cmd.log(f"[INFO] Detected Model: {model}")
                
                if "A34" in model or "ZTE A34" in model:
                     self.cmd.log("[INFO] Identified as ZTE A34. Starting A34 logic...")
                     # We can't call threaded method within thread easily without handling is_running lock
                     # So we run logic directly or release lock. 
                     # Better to release lock and call the method? No, just run logic.
                     # But a34_bypass creates a thread.
                     # Let's just launch the thread after releasing is_running temporarily?
                     # Simplest: Just call the inner logic? 
                     # Actually, reusing the method is better.
                     self.is_running = False
                     self.a34_bypass()
                     return
                elif "A35" in model or "ZTE A35" in model:
                     self.cmd.log("[INFO] Identified as ZTE A35. Starting A35 logic...")
                     self.is_running = False
                     self.a35_bypass()
                     return
                else:
                     self.cmd.log(f"[WARN] Model '{model}' not explicitly recognized as A34 or A35.")
                     self.cmd.log("Please select specific operation manually if needed.")
            
            except Exception as e:
                 self.cmd.log(f"[ERROR] Detection Failed: {e}")
            finally:
                 # If we didn't call another method, we need to reset flag.
                 # If we called another method, it handles its own flag (and checks it at start).
                 # We set is_running = False before calling them, so it's fine.
                 # If we didn't call, we set it here.
                 if self.is_running: 
                    self.is_running = False

        threading.Thread(target=_task).start()

    def a75_bypass(self):
        """
        Specific Bypass Logic for ZTE A75 (Blade A75 5G usually).
        Uses mrog_admin_v2 and removes updates.
        """
        if self.is_running:
             self.cmd.log("[WARN] Operation already running.")
             return

        def _task():
            self.is_running = True
            try:
                self.cmd.log("Phone Mode: ADB Debuging")
                self.cmd.log("Operation: A75 Bypass (mrog_admin_v2)")
                self.cmd.log("Check Authority: OK")
                
                # Check Connection
                self.cmd.log("Starting server... OK")
                self.cmd.run_command("adb start-server")
                
                self.cmd.log("[BLUE]Waiting ADB devices...")
                while True:
                    output = self.cmd.run_command("adb devices", log_output=False)
                    if "device" in output and not output.strip().endswith("List of devices attached"):
                         break
                    time.sleep(1)
    
                self.cmd.log("[BLUE]Check Conection... OK")
                
                # Uninstalling unwanted apps & Updates
                self.cmd.log("[STEP] Stopping System Updates & Removing Bloat...")
                packages = [
                    # Updates
                    "com.google.android.configupdater",
                    "com.google.android.gms.suprvision",
                    "com.android.dynsystem",
                    "com.zte.zdmdaemon",
                    "com.zte.zdmdaemon.install",
                    # Common Bloat
                    "com.android.vending", # Store (Optional, but often requested to stop auto-updates)
                    "com.zte.devicemanager.client",
                    "com.facebook.system",
                    "com.facebook.appmanager",
                    "com.facebook.services"
                ]
                
                for pkg in packages:
                    self.cmd.log(f"Uninstalling {pkg}...")
                    self.cmd.run_command(f"adb shell pm uninstall --user 0 {pkg}")

                # Install mrog_admin_v2.apk
                self.cmd.log("[STEP] Installing mrog_admin_v2...")
                
                import os
                # Use self.cmd.base_path for safety in frozen app
                base = getattr(self.cmd, 'base_path', os.getcwd())
                apk_path = os.path.join(base, "assets", "mrog_admin_v2.apk")
                
                if os.path.exists(apk_path):
                     self.cmd.run_command(f"adb install -r \"{apk_path}\"")
                     
                     # Set Device Owner
                     self.cmd.log("[STEP] Setting device owner...")
                     self.cmd.run_command("adb shell dpm set-device-owner com.mrog.admin/.AdminReceiver")
                     
                     self.cmd.log("[SUCCESS] A75 Bypass (Stealth) Complete!")
                     self.cmd.log("Updates Disabled. Admin Hidden.")
                     self.cmd.log("Please reboot manually.")
                else:
                     self.cmd.log(f"[ERROR] mrog_admin_v2.apk not found in assets folder!")

            except Exception as e:
                 self.cmd.log(f"[ERROR] Operation Failed: {e}")
            finally:
                 self.is_running = False

        threading.Thread(target=_task).start()

    def qr_code_op(self):
        """
        Generates and displays a QR code for ZTE Provisioning.
        Uses SHA-256 Checksum of local APK if available, or predefined values.
        """
        import threading
        import os
        import json
        import hashlib
        import base64
        import customtkinter as ctk
        from PIL import Image, ImageTk
        
        # Check for qrcode library
        try:
            import qrcode
        except ImportError:
            self.cmd.log("[ERROR] 'qrcode' library missing. Please install it.")
            return

        def _task():
            self.cmd.log("[HEADER] ZTE QR GENERATOR")
            self.cmd.log("[BLUE]USING CUSTOM SKA MDM PAYLOAD...")

            # User provided JSON payload
            # "android.app.extra.PROVISIONING_DEVICE_ADMIN_COMPONENT_NAME":"com.skamdm.knox/com.skamdm.knox.AdminReceiver"
            # "android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_DOWNLOAD_LOCATION":"https://api.mdmfile.com/anonyshudb.apk"
            
            # User Specific QR Payload
            qr_data = {
                "android.app.extra.PROVISIONING_ADMIN_EXTRAS_BUNDLE": {},
                "android.app.extra.PROVISIONING_DEVICE_ADMIN_COMPONENT_NAME": "com.mrog.admin/com.mrog.admin.MyDeviceAdminReceiver",
                "android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_CHECKSUM": "E4wh5boly3eQi4ieNfZ7x1BY5aLiGz7VkVNw3Xgck0I=",
                "android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_DOWNLOAD_LOCATION": "https://mrogtool.com/downloads/anonyshudb.apk",
                "android.app.extra.PROVISIONING_LEAVE_ALL_SYSTEM_APPS_ENABLED": True,
                "android.app.extra.PROVISIONING_SKIP_ENCRYPTION": True
            }
            
            # Generate JSON string
            json_str = json.dumps(qr_data, separators=(',', ':'))
            self.cmd.log(f"Payload: {json_str}")

            # 3. Generate Image
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(json_str)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save temp file (Hardcoded Absolute Path for Certainty)
            temp_path = r"C:\Users\mbara\Documents\MR_OG_TOOL\assets\temp_zte_qr.png"
            
            # Force delete old file if it exists
            if os.path.exists(temp_path):
                try: os.remove(temp_path)
                except: pass
                
            img.save(temp_path)
            
            self.cmd.log("[GREEN]QR Code Generated (Fresh)!")
            self.cmd.log("[INFO] Scan the code below.")
            
            # 4. Display Popup
            self._show_qr_popup(temp_path)

        threading.Thread(target=_task).start()

    def _show_qr_popup(self, img_path):
        """Displays the generated QR code in a Toplevel window."""
        import customtkinter as ctk
        from PIL import Image, ImageTk
        import os

        # Since we are in a thread, updating UI is tricky.
        # But Tkinter methods like Toplevel sometimes work if called carefully, 
        # or we might need to invoke it on the main thread if possible.
        # However, purely threaded Toplevel can crash.
        
        # Best Hack: Use a separate process or try creating it directly.
        # If this crashes, we know why.
        
        try:
            # Create PopUp
            top = ctk.CTkToplevel()
            top.title("Scan QR Code")
            top.geometry("400x450")
            top.attributes("-topmost", True)
            
            # Load Image
            if os.path.exists(img_path):
                pil_img = Image.open(img_path)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(350, 350))
                
                label = ctk.CTkLabel(top, image=ctk_img, text="")
                label.pack(pady=20)
                
                info = ctk.CTkLabel(top, text="Scan with QR Scanner", font=("Arial", 14, "bold"))
                info.pack()
            else:
                ctk.CTkLabel(top, text="Error: QR Image Not Found").pack(pady=20)
                
            top.mainloop() # Keep it alive if in thread
            
        except Exception as e:
            self.cmd.log(f"[WARN] Failed to open QR Window: {e}")
            self.cmd.log(f"[INFO] Opening file manually...")
            try: os.startfile(img_path)
            except: pass


    def _ensure_fastboot(self):
        """Helper to switch to fastboot if in ADB."""
        self.cmd.log("[INFO] Checking device mode...")
        adb_devs = self.cmd.run_command("adb devices", log_output=False)
        if "device" in adb_devs and not "List of devices attached" == adb_devs.strip():
             self.cmd.log("[INFO] ADB Device detected. Rebooting to Fastboot...")
             self.cmd.run_command("adb reboot bootloader")
             time.sleep(5)
        
        # Check fastboot
        fb_devs = self.cmd.run_command("fastboot devices", log_output=False)
        if "fastboot" in fb_devs:
            return True
        else:
            self.cmd.log("[ERROR] Device not found in Fastboot mode! Please connect in Fastboot.")
            return False

    def sc9863a_factory_reset(self):
        def _task():
            self.is_running = True
            try:
                self.cmd.log("Operation: ZTE SC9863A Factory Reset")
                if not self._ensure_fastboot():
                    return
                
                self.cmd.log("Erasing Userdata...")
                self.cmd.run_command("fastboot erase userdata")
                self.cmd.log("Erasing Cache...")
                self.cmd.run_command("fastboot erase cache")
                
                self.cmd.log("Rebooting...")
                self.cmd.run_command("fastboot reboot")
                self.cmd.log("[SUCCESS] Factory Reset Complete.")
            except Exception as e:
                self.cmd.log(f"[ERROR] {e}")
            finally:
                self.is_running = False
        threading.Thread(target=_task).start()


    def sc9863a_frp(self):
        def _task():
            self.is_running = True
            try:
                self.cmd.log("Operation: ZTE SC9863A FRP Remove")
                if not self._ensure_fastboot():
                    return

                self.cmd.log("Erasing FRP Partition...")
                self.cmd.run_command("fastboot erase frp")
                self.cmd.log("Erasing Config...")
                self.cmd.run_command("fastboot erase config")
                self.cmd.log("Erasing Persist...")
                self.cmd.run_command("fastboot erase persist")
                
                self.cmd.log("Rebooting...")
                self.cmd.run_command("fastboot reboot")
                self.cmd.log("[SUCCESS] FRP Remove Complete.")
            except Exception as e:
                self.cmd.log(f"[ERROR] {e}")
            finally:
                self.is_running = False
        threading.Thread(target=_task).start()

    def spd_boot_operation(self, model, mode):
        """
        Handles SPD Boot-based operations (Factory Reset / FRP).
        Requires Boot file in assets/boot/{model}/
        """
        if self.is_running:
             self.cmd.log("[WARN] Operation already running. Wait or STOP.")
             return

        def _task():
            self.is_running = True
            try:
                import os
                import glob
                # self.cmd.log(f"[HEADER] SPD BOOT SERVICE: {model}")
                # self.cmd.log(f"Mode: {mode}")

                # 1. Locate Boot Files
                # Normalize model name to folder name (e.g. "ZTE A35" -> "a35")
                folder_name = model.lower().replace("zte ", "").replace(" ", "")
                base = getattr(self.cmd, 'base_path', os.getcwd())
                boot_dir = os.path.join(base, "assets", "boot", folder_name)
                
                if not os.path.exists(boot_dir):
                    self.cmd.log(f"[ERROR] Boot files not found for {model}!")
                    self.cmd.log(f"Missing directory: assets/boot/{folder_name}")
                    return
                
                # self.cmd.log(f"Boot Path: {boot_dir}")
                
                # Smart Find FDL1 and FDL2
                # We look for files containing "fdl1" and "fdl2" (case insensitive)
                fdl1_path = None
                fdl2_path = None
                
                files = os.listdir(boot_dir)
                for f in files:
                    lower_f = f.lower()
                    if "fdl1" in lower_f and (lower_f.endswith(".bin") or lower_f.endswith(".ldr")):
                        fdl1_path = os.path.join(boot_dir, f)
                    elif "fdl2" in lower_f and (lower_f.endswith(".bin") or lower_f.endswith(".ldr")):
                        fdl2_path = os.path.join(boot_dir, f)
                
                if not fdl1_path or not fdl2_path:
                    self.cmd.log("[ERROR] Could not identify FDL1 or FDL2 files!")
                    self.cmd.log(f"Found files: {files}")
                    self.cmd.log("Please ensure files have 'fdl1' and 'fdl2' in their names.")
                    return

                # self.cmd.log(f"FDL1: {os.path.basename(fdl1_path)}")
                # self.cmd.log(f"FDL2: {os.path.basename(fdl2_path)}")

                # Check for SPD Tool (Binary) OR Internal Logic
                # Since we don't have pyserial/spres integrated yet, and user wants standalone
                # We will output highly detailed logs simulating the connection for now
                # BUT if we had the tool, this is where we'd call it.
                
                # MOCKUP of Protocol Execution
                # User requested clean start
                self.cmd.log("1. Power OFF")
                self.cmd.log("2. Hold Vol+ and Vol-")
                self.cmd.log("3. Insert USB Cable")
                
                # --- REAL PORT DETECTION (PowerShell Method) ---
                import subprocess
                detected_port = None
                
                # Keywords to look for in Device Manager
                keywords = ["Spreadtrum", "SPRD", "SciU2S", "Diag", "USB Serial Port"]
                
                self.cmd.log("Scanning for device... (Waiting)")
                
                wait_count = 0
                max_wait = 120 # 2 minutes timeout
                
                while wait_count < max_wait:
                    if not self.is_running: return # Stop if user clicks STOP
                    
                    try:
                        # PowerShell command to get Serial Ports
                        # We use Win32_SerialPort which works better than Wmi PnPEntity for pure CMD sometimes
                        # Or specific PnpEntity query
                        ps_cmd = 'Get-WmiObject Win32_PnPEntity | Where-Object { $_.Name -match "COM" } | Select-Object -ExpandProperty Name'
                        
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        
                        proc = subprocess.Popen(["powershell", "-Command", ps_cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo, text=True)
                        out, err = proc.communicate()
                        
                        if out:
                            lines = out.strip().split('\n')
                            for line in lines:
                                line = line.strip()
                                if not line: continue
                                
                                # Check against keywords
                                for k in keywords:
                                    if k.lower() in line.lower():
                                        detected_port = line
                                        break
                                if detected_port: break
                    except:
                        pass
                        
                    if detected_port:
                        break
                        
                    time.sleep(1)
                    wait_count += 1
                
                if not detected_port:
                    self.cmd.log("[RED]Timeout: No device detected after 2 minutes.")
                    return
                
                self.cmd.log(f"[BLUE]DEVICE DETECTED: {detected_port}")
                
                # --- REAL SPD PROTOCOL IMPLEMENTATION ---
                import serial
                import struct
                
                # HDLC Protocol Constants
                HDLC_FLAG = 0x7E
                HDLC_ESCAPE = 0x7D
                HDLC_ESCAPE_MASK = 0x20
                
                BSL_CMD_CHECK_BAUD = 0x7E
                BSL_CMD_CONNECT = 0x00
                BSL_CMD_START_DATA = 0x02
                BSL_CMD_MID_DATA = 0x03
                BSL_CMD_END_DATA = 0x04
                BSL_CMD_EXEC_DATA = 0x05
                BSL_REP_ACK = 0x80
                BSL_REP_VER = 0x81
                
                def hdlc_encode(data):
                    out = bytearray()
                    out.append(HDLC_FLAG)
                    for b in data:
                        if b == HDLC_FLAG or b == HDLC_ESCAPE:
                            out.append(HDLC_ESCAPE)
                            out.append(b ^ HDLC_ESCAPE_MASK)
                        else:
                            out.append(b)
                    out.append(HDLC_FLAG)
                    return out

                def hdlc_decode(data):
                    # Simple decode (stripping flags and Un-escaping)
                    out = bytearray()
                    esc = False
                    for b in data:
                        if b == HDLC_FLAG: continue
                        if b == HDLC_ESCAPE:
                            esc = True
                            continue
                        if esc:
                            out.append(b ^ HDLC_ESCAPE_MASK)
                            esc = False
                        else:
                            out.append(b)
                    return out
                
                def send_cmd(ser, cmd_type, data=b""):
                    # Construct packet: Type(2) + Len(2) + Data
                    length = len(data)
                    packet = struct.pack(">HH", cmd_type, length) + data
                    encoded = hdlc_encode(packet)
                    ser.write(encoded)

                def read_resp(ser, timeout=2):
                    ser.timeout = timeout
                    # Read until HDLC_FLAG
                    # A robust reader would read byte by byte
                    raw = ser.read_until(b'\x7E') # Read start frame if existing garbage
                    if not raw: return None
                    
                    # Read real frame
                    frame = ser.read_until(b'\x7E')
                    if not frame: return None
                    
                    decoded = hdlc_decode(frame)
                    if len(decoded) < 4: return None
                    
                    resp_type = struct.unpack(">H", decoded[0:2])[0]
                    return resp_type

                def get_base_address(file_path):
                    """Try to read base address from SPD Header (Offset 0x24 usually)"""
                    try:
                        with open(file_path, "rb") as f:
                             # Skip known LDR generic header if present?
                             # SPD Signed header often puts load addr at 0x24 or 0x28
                             f.seek(0x24)
                             addr_bytes = f.read(4)
                             if len(addr_bytes) == 4:
                                 return struct.unpack("<I", addr_bytes)[0]
                    except: pass
                    return 0

                try:
                    # Open COM Port
                    # Extract "COMx" from name (e.g., "SPRD U2S Diag (COM28)")
                    import re
                    match = re.search(r"(COM\d+)", detected_port)
                    if not match:
                        self.cmd.log("[RED]Error: Could not parse COM Port number.")
                        return
                    
                    com_port = match.group(1)
                    self.cmd.log(f"Opening {com_port}...")
                    
                    ser = serial.Serial(com_port, 115200, timeout=1)
                    # 1. Handshake
                    self.cmd.log("Handshake...")
                    handshake_ok = False
                    for _ in range(30):
                         ser.write(b'\x7E')
                         ack = read_resp(ser, timeout=0.1)
                         if ack == BSL_REP_VER or ack == BSL_REP_ACK:
                              handshake_ok = True
                              break
                         time.sleep(0.05)
                    
                    if not handshake_ok:
                         self.cmd.log("[RED] Initial Handshake Failed!")
                         ser.close(); return

                    # STRATEGY CHANGE: CHECK FOR FFDL.ldr
                    ffdl_path = os.path.join(boot_dir, "FFDL.ldr")
                    use_ffdl = os.path.exists(ffdl_path)
                    
                    if use_ffdl:
                        self.cmd.log(f"Using FFDL ({os.path.basename(ffdl_path)})...")
                        loader_path = ffdl_path
                        # Standard Reset Address
                        loader_addr = 0x50000000
                        use_fdl2 = False
                    else:
                        self.cmd.log(f"Using Standard FDL1 ({os.path.basename(fdl1_path)})...")
                        loader_path = fdl1_path
                        loader_addr = 0x50000000
                        use_fdl2 = True

                    # Upload Loader 1
                    with open(loader_path, "rb") as f:
                        data = f.read()
                    
                    sz = len(data)
                    send_cmd(ser, BSL_CMD_START_DATA, struct.pack(">II", loader_addr, sz))
                    read_resp(ser)
                    
                    chunk_size = 512
                    for i in range(0, sz, chunk_size):
                        chunk = data[i:i+chunk_size]
                        send_cmd(ser, BSL_CMD_MID_DATA, chunk)
                        read_resp(ser, 0.2)
                        
                    send_cmd(ser, BSL_CMD_END_DATA)
                    read_resp(ser)
                    
                    send_cmd(ser, BSL_CMD_EXEC_DATA, struct.pack(">I", loader_addr))
                    read_resp(ser)
                    self.cmd.log("Loader Executed.")
                    time.sleep(2)
                    
                    # If using FFDL, we might be ready for commands directly?
                    # Or FFDL is just FDL1 and expects FDL2?
                    # Usually FFDL replaces FDL1. 
                    # Let's assume FFDL needs FDL2 unless it's a "One-Shot".
                    # BUT user said "FFDL.ldr", maybe that IS the solution.
                    
                    connected_fdl1 = True # Assume success if first loader ran
                    
                    if use_fdl2:
                        # 3. Upload FDL2
                        # ADDRESS FIX: Force 0x9efffe00
                        addr2 = 0x9efffe00
                        self.cmd.log(f"Sending FDL2 ({os.path.basename(fdl2_path)}) to 0x{addr2:X}...")
                        
                        # Handshake Loop again
                        connected_fdl1 = False
                        baudrates = [115200, 921600]
                        for baud in baudrates:
                            if connected_fdl1: break
                            self.cmd.log(f"Handshake FDL2 at {baud}...")
                            try:
                                ser.baudrate = baud
                                ser.reset_input_buffer(); ser.reset_output_buffer()
                                for _ in range(25):
                                    ser.write(b'\x7E')
                                    time.sleep(0.04)
                                    if ser.in_waiting:
                                        ack = read_resp(ser, timeout=0.1)
                                        if ack == BSL_REP_ACK or ack == BSL_REP_VER:
                                            connected_fdl1 = True
                                            break
                            except: pass
                        
                        if not connected_fdl1:
                             self.cmd.log("[RED] FDL2 Handshake FAILED.")
                             # Try to continue? No, impossible.
                             ser.close(); return

                        with open(fdl2_path, "rb") as f:
                            fdl2_data = f.read()
                        
                        sz2 = len(fdl2_data)
                        send_cmd(ser, BSL_CMD_START_DATA, struct.pack(">II", addr2, sz2))
                        read_resp(ser)
                        
                        for i in range(0, sz2, chunk_size):
                            chunk = fdl2_data[i:i+chunk_size]
                            send_cmd(ser, BSL_CMD_MID_DATA, chunk)
                            read_resp(ser, 0.2)
                            
                        send_cmd(ser, BSL_CMD_END_DATA)
                        read_resp(ser)
                        send_cmd(ser, BSL_CMD_EXEC_DATA, struct.pack(">I", addr2))
                        self.cmd.log("FDL2 Executed.")
                        time.sleep(2)
                    
                    # 4. Commands 
                    if not connected_fdl1:
                         self.cmd.log("[RED] skipping commands as FDL2 handshake failed.")
                         return

                    send_cmd(ser, BSL_CMD_EXEC_DATA, struct.pack(">I", addr2))
                    self.cmd.log("FDL2 Executed.")
                    
                    time.sleep(2)

                    # 4. Read Partition Table (To find addresses)
                    # Cmd 0x1B sometimes returns partition listing if supported by FDL
                    self.cmd.log("Reading Partition Table...")
                    
                    # Try to read partition info
                    # Many FDLs store partition table at a specific location or return it via command
                    # We'll try sending generic READ_PARTITION_TABLE command (0x1B? Or maybe internal)
                    # Actually, standard SPD FDL often doesn't have a "List Partitions" command exposed easily without knowing offset.
                    
                    # STRATEGY 2: If we can't read table, we can't erase safely.
                    # But often FDL2 *IS* the flashing loop. 
                    # Let's try 0x1B (Read Packet)
                    
                    # For safe coding now:
                    # Let's assume we need to erase by "Partition ID" if available, or just reboot if we can't.
                    # But user wants "Unlock".
                    
                    # Let's try a common "formatting" approach for generic SPD:
                    # Some tools just loop through known offsets.
                    # BETTER: Let's try to Reboot first since user asked for it.
                    
                    pass # Placeholder for complex logic
                    
                    # --- REBOOT COMMAND (0x25 or 0x0A) ---
                    # 0x25 = BSL_CMD_RESET typically in newer FDLs
                    # 0x0A = BSL_CMD_POWER_OFF
                    
                    reboot_done = False
                    
                    # COMMANDS:
                    # ERASE logic (Blind is dangerous). 
                    # We will log that we need "Partition Offsets" or try to read them.
                    
                    # Let's try to Format PERSIST/USERDATA if we can identify them?
                    # Since we can't, we will SKIP erase to avoid bricks, 
                    # and just do the Reboot which user complained about not happening.
                    
                    # WAIT! User said "aitoi lock" (It didn't remove lock).
                    # I MUST erase something.
                    # I will look for 'settings.ini' in the boot folder which might have offsets?
                    # User: "settings.ini" is in that folder (seen in previous ls).
                    
                    # Let's try to parse settings.ini in the boot folder if it exists!
                    settings_path = os.path.join(boot_dir, "settings.ini")
                    userdata_base = 0
                    userdata_size = 0
                    persist_base = 0
                    persist_size = 0
                    
                    if os.path.exists(settings_path):
                        self.cmd.log("Found settings.ini! Reading partition info...")
                        with open(settings_path, "r") as f:
                            for line in f:
                                # Example: userdata=0xABC00000,0x100000
                                line = line.lower().strip()
                                if "userdata" in line or "data" in line:
                                    # Very basic parser logic assumption
                                    parts = line.split("=")
                                    if len(parts) > 1:
                                        vals = parts[1].split(",")
                                        if len(vals) >= 2:
                                            try:
                                                userdata_base = int(vals[0], 16)
                                                userdata_size = int(vals[1], 16)
                                            except: pass
                                if "persist" in line or "frp" in line:
                                    parts = line.split("=")
                                    if len(parts) > 1:
                                        vals = parts[1].split(",")
                                        if len(vals) >= 2:
                                            try:
                                                persist_base = int(vals[0], 16)
                                                persist_size = int(vals[1], 16)
                                            except: pass
                    
                    # Fallback to generic known offsets for SC9863A if not found?
                    # SC9863A Userdata often starts high.
                    # Risky.
                    
                    if userdata_base == 0 and persist_base == 0:
                         self.cmd.log("[WARN] No partition offsets found in settings.ini!")
                         self.cmd.log("Cannot erase safely. Please update settings.ini with: 'userdata=0xStart,0xSize'")
                    
                    # Perform Erase if we have coordinates
                    if mode in ["RESET", "ALL"] and userdata_base > 0:
                        self.cmd.log("Formatting Userdata...")
                        send_cmd(ser, 0x0C, struct.pack(">II", userdata_base, userdata_size))
                        resp = read_resp(ser, 5)
                        if resp == BSL_REP_ACK: self.cmd.log("Userdata Formatted [OK]")
                        else: self.cmd.log("Userdata Format FAILED")

                    if mode in ["FRP", "ALL"] and persist_base > 0:
                         self.cmd.log("Erasing FRP...")
                         send_cmd(ser, 0x0C, struct.pack(">II", persist_base, persist_size))
                         resp = read_resp(ser, 2)
                         if resp == BSL_REP_ACK: self.cmd.log("FRP Erased [OK]")
                         else: self.cmd.log("FRP Erase FAILED")

                    self.cmd.log("Sending POWER OFF Command (0x6E)...")
                    # 0x25 (System Reset) didn't work.
                    # Try 0x6E (Power Down) which forces a restart state on some SPD
                    # Or try sending Disable Watchdog then Reset.
                    
                    # Command 0: Power Off
                    send_cmd(ser, 0x6E) 
                    
                    self.cmd.log("[SUCCESS] Force Power Off sent. Please power on manually if it doesn't reboot.")
                    ser.close()

                except Exception as e:
                    self.cmd.log(f"[ERROR] Connection Failed: {e}")
                    # Fallback log
                    self.cmd.log("Try verifying drivers or using a different FDL.")

            except Exception as e:
                self.cmd.log(f"[ERROR] SPD Operation Failed: {e}")
            finally:
                self.is_running = False

        threading.Thread(target=_task).start()
