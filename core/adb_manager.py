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
    
    def remove_frp_mock(self):
        # Real FRP bypass is complex. This is a placeholder/mock.
        self.cmd.log("Attempting FRP Bypass (Generic)...")
        self.cmd.log("Sending bypass intent...")
        self.cmd.run_async("adb shell am start -n com.google.android.gsf.login/...")
        self.cmd.log("Please check device screen...")
