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
