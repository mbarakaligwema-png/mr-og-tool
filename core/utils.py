import subprocess
import threading
import tkinter as tk

class CommandRunner:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        self.current_process = None

    def log(self, message):
        if self.log_callback:
            self.log_callback(message + "\n")
        else:
            print(message)

    def stop_current_process(self):
        """Kills the currently running process."""
        if self.current_process:
            self.log("[STOP] Attempting to terminate process...")
            try:
                self.current_process.kill() # Force kill
                self.log("[STOP] Process terminated by user.")
            except Exception as e:
                self.log(f"[STOP ERROR] Failed to kill process: {e}")
            self.current_process = None
        else:
            self.log("[STOP] No active process to stop.")

    def run_command(self, command, log_output=True):
        """Runs a command blocking, returns output."""
        if log_output:
            self.log(f"[EXEC] {command}")
        try:
            # shell=True required for some commands, but careful with security. 
            # For this tool, we assume local usage.
            # startupinfo to hide window on Windows
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            self.current_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                       text=True, shell=True, startupinfo=startupinfo)
            
            stdout, stderr = self.current_process.communicate()
            self.current_process = None # Reset after completion
            
            if stdout and log_output:
                self.log(stdout.strip())
            if stderr and log_output:
                self.log(f"[ERROR] {stderr.strip()}")
            
            return stdout.strip()
        except Exception as e:
            self.log(f"[EXCEPTION] {str(e)}")
            return ""

    def run_async(self, command):
        """Runs command in a separate thread to keep UI responsive."""
        thread = threading.Thread(target=self.run_command, args=(command,))
        thread.start()
