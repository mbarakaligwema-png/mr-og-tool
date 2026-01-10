from core.utils import CommandRunner

class SPDManager:
    def __init__(self, log_callback):
        self.cmd = CommandRunner(log_callback)

    def enter_diag_mode(self):
        self.cmd.log("Switching to Diag Mode...")
        self.cmd.log("Trying standard SPD Diag commands...")

    def read_info(self):
        self.cmd.log("Reading SPD Device Info...")

    def remove_frp(self):
        self.cmd.log("Removing FRP (SPD)...")

    def format_userdata(self):
        self.cmd.log("Formatting Userdata...")

    def backup_nv(self):
        self.cmd.log("Backing up NV items...")

    def restore_nv(self):
        self.cmd.log("Restoring NV items...")

    def sim_unlock(self):
        self.cmd.log("SIM Unlocking...")
