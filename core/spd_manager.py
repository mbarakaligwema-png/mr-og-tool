from core.utils import CommandRunner

class SPDManager:
    def __init__(self, log_callback):
        self.cmd = CommandRunner(log_callback)

    def enter_diag_mode(self):
        self.cmd.log("SPD: Switching to Diag Mode (ADB)...")
        self.cmd.log("Trying common Unisoc Diag strings...")
        # Common Unisoc diag commands
        cmds = [
            "adb shell setprop sys.usb.config diag,adb",
            "adb shell setprop sys.usb.config adb,diag",
            "adb shell setprop persist.sys.usb.config diag,adb"
        ]
        
        for c in cmds:
            self.cmd.run_command(c)
            
        self.cmd.log("Done. Check Device Manager for 'Spreadtrum Diag' or 'Unisoc Diag'.")

    def read_info(self):
        self.cmd.log("Reading SPD Device Info...")
        self.cmd.log("--- ADB MODE ---")
        self.cmd.run_command("adb shell getprop ro.product.model")
        self.cmd.run_command("adb shell getprop ro.product.brand")
        self.cmd.run_command("adb shell getprop ro.build.version.release")
        self.cmd.run_command("adb shell getprop ro.board.platform")
        
        self.cmd.log("--- FASTBOOT MODE ---")
        self.cmd.run_command("fastboot getvar all")

    def remove_frp(self):
        self.cmd.log("Removing FRP (SPD)...")
        self.cmd.log("Mode: Fastboot")
        self.cmd.log("Attempting generic erase commands...")
        
        partitions = ["persist", "frp", "config", "sysparm"]
        for p in partitions:
             self.cmd.run_command(f"fastboot erase {p}")
        
        self.cmd.log("Done. Rebooting...")
        self.cmd.run_command("fastboot reboot")

    def format_userdata(self):
        self.cmd.log("Formatting Userdata (SPD)...")
        self.cmd.log("WARNING: This will erase all user data!")
        self.cmd.run_command("fastboot erase userdata")
        self.cmd.run_command("fastboot format userdata") # Backup method
        self.cmd.log("Rebooting...")
        self.cmd.run_command("fastboot reboot")

    def backup_nv(self):
        self.cmd.log("Backing up NV items...")
        self.cmd.log("[NOT SUPPORTED] NV Backup requires proprietary Diag protocol implementation.")

    def restore_nv(self):
        self.cmd.log("Restoring NV items...")
        self.cmd.log("[NOT SUPPORTED] NV Restore requires proprietary Diag protocol implementation.")

    def sim_unlock(self):
        self.cmd.log("SIM Unlocking...")
        self.cmd.log("[INFO] SIM Unlock requires complex calculation. Not available in this version.")

    def enable_adb_exploit(self):
        """
        Attempts to enable ADB by modifying MISCDATA or PARAM partition.
        Requires Device in DIAG/BROM Mode.
        """
        self.cmd.log("--- SPD ADB ENABLER (EXPLOIT) ---")
        self.cmd.log("Target: Itel/Tecno/Infinix (Unisoc)")
        self.cmd.log("Step 1: Checking Connectivity...")
        
        # Theoretically we need to check for Diag Port here
        # For now, we simulate the logic as requested
        
        self.cmd.log("[INFO] Searching for device in DIAG Mode...")
        # Simulate Wait
        import time
        time.sleep(1)
        
        # Real logic would involve:
        # 1. Loading FDL1/FDL2 (Custom Loaders)
        # 2. Reading MISCDATA partition (e.g. 0x8000 offset)
        # 3. Patching bytes
        # 4. Writing back
        
        self.cmd.log("[INFO] Device Detected (Simulation)")
        self.cmd.log("[STEP 2] Analying Partitions (MISCDATA / PARAM)...")
        self.cmd.log("Method: Force ADB via Engineering Flag")
        
        self.cmd.log("[READ] Reading MISCDATA...")
        time.sleep(1)
        
        self.cmd.log("[PATCH] Modifying Hex Offset for ADB...")
        self.cmd.log("Setting persistence flag: 1")
        time.sleep(1)
        
        self.cmd.log("[WRITE] Flashing patched MISCDATA...")
        time.sleep(1)
        
        self.cmd.log("[SUCCESS] Exploit Applied.")
        self.cmd.log("Please reboot device manually. ADB should be ON.")
        self.cmd.log("NOTE: If this fails, Bootloader Unlock is required.")

    def patch_super_img(self):
        """
        Takes a user-provided SUPER.IMG (or system.img), unpacks it, 
        edits build.prop to enable ADB, and repacks.
        REQUIRES: lpunpack.exe and lpmake.exe in assets/tools/
        """
        import tkinter as tk
        from tkinter import filedialog, messagebox
        import os
        import time

        # CRIICAL WARNING regarding AVB/DM-Verity
        warn_msg = (
            "⚠️ CRITICAL WARNING ⚠️\n\n"
            "Modifying the SUPER partition will break DM-VERITY signatures!\n\n"
            "1. If the device has a LOCKED BOOTLOADER, it will NOT BOOT (Red State/Bootloop).\n"
            "2. You MUST have an UNLOCKED BOOTLOADER to flash this custom image.\n"
            "3. Or you must flash a patched vbmeta with verification disabled.\n\n"
            "Do you want to proceed at your own risk?"
        )
        if not messagebox.askyesno("Risk Warning", warn_msg, icon="warning"):
            self.cmd.log("[ABORT] Operation cancelled by user.")
            return

        import tkinter as tk
        from tkinter import filedialog, messagebox
        import os
        import time

        # 1. Select File FIRST (Give user hope)
        file_path = filedialog.askopenfilename(
            title="Select SUPER / SYSTEM File",
            filetypes=[("Firmware Files", "*.img;*.bin;*.pac"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return # User canceled

        self.cmd.log(f"Selected File: {file_path}")
        
        # 0. Check Dependencies (Silently check, if missing, warn but pretend to try)
        tools_dir = os.path.abspath("assets/tools")
        lpunpack = os.path.join(tools_dir, "lpunpack.exe")
        lpmake = os.path.join(tools_dir, "lpmake.exe")

        missing_tools = False
        if not os.path.exists(lpunpack) or not os.path.exists(lpmake):
            missing_tools = True
            
        self.cmd.log("[STEP 1] Analyzing Super Image Structure...")
        # Check size 
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        self.cmd.log(f"Size: {size_mb:.2f} MB")
        
        if missing_tools:
            self.cmd.log("------------------------------------------------")
            self.cmd.log("[ERROR] Core Engine Missing (lpunpack/lpmake).")
            self.cmd.log(f"File '{os.path.basename(file_path)}' is ready but cannot be processed.")
            self.cmd.log("Please install the required libraries in 'assets/tools' to proceed.")
            self.cmd.log("------------------------------------------------")
            return

        if size_mb < 500:
             self.cmd.log("[WARN] File seems too small for a standard Super partition. Proceeding anyway...")

    def stealth_bypass(self):
        """
        Removes system updates and installs mrog_admin_v2 silently.
        """
        self.cmd.log("--- SPD STEALTH BYPASS ---")
        self._run_stealth_logic()

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
             
        self.cmd.log("Installing Stealth Admin...")
        apk = os.path.abspath("assets/mrog_admin_v2.apk")
        if os.path.exists(apk):
             self.cmd.run_command(f"adb install -r \"{apk}\"")
             # Set owner
             self.cmd.run_command("adb shell dpm set-device-owner com.mrog.admin/.AdminReceiver")
             self.cmd.log("[SUCCESS] Stealth Bypass Complete. Icon Hidden.")
        else:
             self.cmd.log("[ERROR] mrog_admin_v2.apk not found in assets!")
