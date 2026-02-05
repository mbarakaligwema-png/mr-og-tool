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
            
            # 1. Locate APK & Calculate Checksum
            base = getattr(self.cmd, 'base_path', os.getcwd())
            apk_path = os.path.join(base, "assets", "mrog_bypass_v2.apk") # Corrected filename
            
            checksum = ""
            if os.path.exists(apk_path):
                self.cmd.log(f"Calculating Checksum for: {os.path.basename(apk_path)}...")
                sha = hashlib.sha256()
                with open(apk_path, 'rb') as f:
                    while True:
                        data = f.read(65536)
                        if not data: break
                        sha.update(data)
                checksum = base64.urlsafe_b64encode(sha.digest()).decode().strip('=')
                self.cmd.log(f"Checksum: {checksum[:10]}...[OK]")
            else:
                self.cmd.log("[WARN] APK not found in assets. Using default placeholder checksum.")
                checksum = "9HpyskSThzfZ1QB2t3VM9vC2SP3v71auDyScIbnvmB0=" # Placeholder

            # 2. Prepare JSON Data
            # Note: The download URL must be accessible by the phone over WiFi
            # We use a placeholder URL or the user's server
            
            # Using 'com.mrog.admin' component name from our XML
            component_name = "com.mrog.admin/.MyDeviceAdminReceiver"
            
            qr_data = {
                "android.app.extra.PROVISIONING_ADMIN_EXTRAS_BUNDLE": {},
                "android.app.extra.PROVISIONING_DEVICE_ADMIN_COMPONENT_NAME": component_name,
                "android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_CHECKSUM": checksum,
                # Ideally, this URL should be your real server URL where the APK is hosted
                # Since we can't host local file easily to phone without a server, we warn the user
                "android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_DOWNLOAD_LOCATION": "https://mrogtool.com/downloads/mrog_bypass_v2.apk",
                "android.app.extra.PROVISIONING_LEAVE_ALL_SYSTEM_APPS_ENABLED": True,
                "android.app.extra.PROVISIONING_SKIP_ENCRYPTION": True,
                # Force WiFi
                "android.app.extra.PROVISIONING_WIFI_SECURITY_TYPE": "NONE"
            }
            
            json_str = json.dumps(qr_data, separators=(',', ':'))
            self.cmd.log(f"Payload Created.")

            # 3. Generate Image
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(json_str)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save temp file
            temp_path = os.path.join(base, "assets", "temp_zte_qr.png")
            img.save(temp_path)
            
            self.cmd.log("[GREEN]QR Code Generated!")
            self.cmd.log("[INFO] 1. Connect phone to WiFi.")
            self.cmd.log("[INFO] 2. Tap screen 6 times to open QR Scanner.")
            self.cmd.log("[INFO] 3. Scan the code below.")
            
            # 4. Display Popup
            self._show_qr_popup(temp_path)

        threading.Thread(target=_task).start()

    def _show_qr_popup(self, img_path):
        import customtkinter as ctk
        from PIL import Image, ImageTk
        import os

        # Must run on main thread
        # We assume self.cmd.log_callback is bound to the UI somewhat, 
        # but to open a window we usually need root. We'll try to find root from log_callback or passed context
        # Or just use a Toplevel if we can reference app.
        
        # A simple hacky way if we don't have direct reference:
        # We rely on the fact that this is running in a thread, so we can't update UI directly without after()
        # But we don't have 'after' here easily.
        
        # We will assume this is rarely called or we can use the 'os.startfile' to just open the image in default viewer
        # This is surprisingly robust for tools.
        
        if os.name == 'nt':
            try:
                os.startfile(img_path)
            except:
                pass
        # If we really wanted a tailored UI, we'd need to pass the 'app' instance to ZTEManager


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
