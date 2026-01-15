from core.utils import CommandRunner

class FastbootManager:
    def __init__(self, log_callback):
        self.cmd = CommandRunner(log_callback)

    def read_info(self):
        def _task():
            # Header
            self.cmd.log("[HEADER] [FASTBOOT] READ DEVICE INFO ")
            self.cmd.log("Waiting for Fastboot Device... [GREEN]OK")
            
            # Check Connection
            devices = self.cmd.run_command("fastboot devices")
            if not devices.strip():
                 self.cmd.log("Connecting to device... [RED]FAILED (No Device Detected)")
                 self.cmd.log("[YELLOW]Check drivers or put device in Fastboot Mode.")
                 return
            
            self.cmd.log("Connecting to device... [GREEN]OK")
            self.cmd.log("Reading Information... [GREEN]OK")
            
            # Get All Vars
            raw_vars = self.cmd.run_command("fastboot getvar all")
            
            # Parse getvar all output
            # Format usually: "(bootloader) var: value" or just "var: value"
            data_map = {}
            for line in raw_vars.split('\n'):
                line = line.strip()
                if "Finished." in line: continue
                
                parts = line.split(':')
                if len(parts) >= 2:
                    key = parts[0].replace("(bootloader)", "").strip()
                    val = ":".join(parts[1:]).strip()
                    data_map[key] = val
                    
            # Display Keys
            display_keys = [
                ("Product", "product"),
                ("Model", "model"),
                ("Serial No", "serialno"),
                ("Secure Boot", "secure"),
                ("Unlocked", "unlocked"),
                ("Battery Soc", "battery-soc-ok"),
                ("Voltage", "battery-voltage"),
                ("Ver-Bootloader", "version-bootloader"),
                ("Ver-Baseband", "version-baseband"),
            ]
            
            has_data = False
            for label, key in display_keys:
                if key in data_map:
                    val = data_map[key]
                    if val:
                        has_data = True
                        self.cmd.log(f"{label} : [BLUE]{val}")
            
            if has_data:
                self.cmd.log("Operation Finished. [GREEN]OK")
            else:
                self.cmd.log("[YELLOW]Device returned no standard variables.")
                # Dump raw if empty?
                # self.cmd.log(raw_vars)

        import threading
        threading.Thread(target=_task).start()

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
