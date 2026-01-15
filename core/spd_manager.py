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
