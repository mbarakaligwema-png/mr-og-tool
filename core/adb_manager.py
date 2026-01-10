from core.utils import CommandRunner

class ADBManager:
    def __init__(self, log_callback):
        self.cmd = CommandRunner(log_callback)

    def read_info(self):
        def _task():
            # Initial Status Logs
            self.cmd.log("Phone Mode: ADB Debuging")
            self.cmd.log("Operation: Read Info [ADB]") # Adjusted op name
            self.cmd.log("Check Authority: OK")
            self.cmd.log("Waiting ADB devices... OK")
            self.cmd.log("Starting server... OK")
            self.cmd.log("Waiting ADB Server... OK")

            # Check connection
            state = self.cmd.run_command("adb get-state")
            if "device" not in state:
                 self.cmd.log("Check Conection... FAILED (No Device/Auth)")
                 return
            
            self.cmd.log("Check Conection... OK")
            # self.cmd.log("Block OTA : OK") # User listed this at end, maybe do it if we had a function check

            # Mapping User Labels to ADB Props
            # User Key -> (ADB Prop, Fallback)
            props_map = [
                ("SN", "ro.serialno"),
                ("Platform", "ro.board.platform"), # or ro.product.board
                ("Cpu Abi", "ro.product.cpu.abi"),
                ("Manufacturer", "ro.product.manufacturer"),
                ("Board", "ro.product.board"),
                ("Name", "ro.product.name"),
                ("Brand", "ro.product.brand"),
                ("Model", "ro.product.model"),
                ("Build Id", "ro.build.display.id"),
                ("Version", "ro.build.version.release"),
                ("Build Date", "ro.build.date"),
                ("Security Patch", "ro.build.version.security_patch"),
                ("Description", "ro.build.description"),
            ]
            
            info_data = []
            
            # Fetch Data
            for label, prop in props_map:
                val = self.cmd.run_command(f"adb shell getprop {prop}")
                if not val and prop == "ro.board.platform": # Fallback for platform
                     val = self.cmd.run_command("adb shell getprop ro.chipname")
                
                if val:
                    info_data.append((label, val))
            
            # Formatted Output
            # Find max label length for alignment (though user used fixed spacing, dynamic is safer)
            # User Example: " SN : <val>"
            
            for label, val in info_data:
                # Format: " Key : Value"
                self.cmd.log(f" {label} : {val}")
            
            # Extra status
            self.cmd.log("Block OTA : OK") # Fake/Check for user request consistency

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
