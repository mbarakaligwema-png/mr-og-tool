from core.utils import CommandRunner

class FastbootManager:
    def __init__(self, log_callback):
        self.cmd = CommandRunner(log_callback)

    def read_info(self):
        self.cmd.log("Reading Fastboot Device Info...")
        self.cmd.run_async("fastboot getvar all")

    def reboot_system(self):
        self.cmd.log("Rebooting to System...")
        self.cmd.run_async("fastboot reboot")

    def reboot_edl(self):
        self.cmd.log("Rebooting to EDL (Emergency Download Mode)...")
        self.cmd.run_async("fastboot oem edl")

    def unlock_bootloader(self):
        self.cmd.log("Attempting to Unlock Bootloader...")
        self.cmd.log("WARNING: This will wipe data on most devices.")
        self.cmd.run_async("fastboot flashing unlock")
        # Fallback for older devices
        self.cmd.run_async("fastboot oem unlock")

    def relock_bootloader(self):
        self.cmd.log("Relocking Bootloader...")
        self.cmd.run_async("fastboot flashing lock")
        self.cmd.run_async("fastboot oem lock")

    def erase_frp(self):
        self.cmd.log("Erasing FRP Partition...")
        # Common FRP partition names
        self.cmd.run_async("fastboot erase config")
        self.cmd.run_async("fastboot erase frp")
        self.cmd.run_async("fastboot erase persistent")

    def wipe_userdata(self):
        self.cmd.log("Wiping Userdata...")
        self.cmd.run_async("fastboot erase userdata")
        self.cmd.run_async("fastboot -w")
