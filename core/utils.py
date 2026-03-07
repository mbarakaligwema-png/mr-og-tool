import subprocess
import threading
import tkinter as tk

class CommandRunner:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        self.active_processes = []
        self.lock = threading.Lock()
        self.adb_path = "adb" # Default to system path
        self._resolve_adb_path()
        
        # Force Restart ADB Server on Tool Start to clear conflicts
        self._reset_adb_server()

    def _resolve_adb_path(self):
        import os
        import sys
        
        # Determine Base Path (Root of the App)
        if getattr(sys, 'frozen', False):
            # If running as compiled .exe
            self.base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        else:
            # If running as script, use CWD (run.bat sets this)
            self.base_path = os.getcwd()

        # Update paths to look in base_path for adb.exe
        possible_paths = [
            os.path.join(self.base_path, "adb.exe"), # Bundle Root
            os.path.join(self.base_path, "assets", "adb.exe"), # Inside Assets
            os.path.join(self.base_path, "assets", "platform-tools", "adb.exe"),
            os.path.join(self.base_path, "assets", "tools", "adb.exe"),
        ]
        
        # Also check inside scrcpy folder or other sub-tools
        tools_dir = os.path.join(self.base_path, "assets", "tools")
        if os.path.exists(tools_dir):
            for root, dirs, files in os.walk(tools_dir):
                if "adb.exe" in files:
                    possible_paths.append(os.path.join(root, "adb.exe"))
        
        # Try finding in the project root if the current base_path doesn't have it (fallback)
        if not getattr(sys, 'frozen', False):
            possible_paths.append(os.path.join(os.getcwd(), "adb.exe"))

        for p in possible_paths:
            if os.path.exists(p):
                self.adb_path = f'"{p}"' # Quote it for paths with spaces
                break
        
        # Final fallback to system path if nothing found
        if self.adb_path == "adb":
             # Try to find it in the current system path and use absolute path if found
             import shutil
             sys_adb = shutil.which("adb")
             if sys_adb:
                 self.adb_path = f'"{sys_adb}"'

    def _reset_adb_server(self):
        try:
             startupinfo = subprocess.STARTUPINFO()
             startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
             # Kill existing server (from other tools)
             subprocess.run(f"{self.adb_path} kill-server", shell=True, startupinfo=startupinfo)
             # Start fresh server
             subprocess.run(f"{self.adb_path} start-server", shell=True, startupinfo=startupinfo)
        except:
             pass
    
    def log(self, message):
        if self.log_callback:
            self.log_callback(message + "\n")
        else:
            print(message)

    def stop_current_process(self):
        """Kills all currently running processes managed by this runner."""
        with self.lock:
            if not self.active_processes:
                self.log("[STOP] No active processes to stop.")
                return
                
            self.log(f"[STOP] Attempting to terminate {len(self.active_processes)} active processes...")
            for proc in self.active_processes:
                try:
                    proc.kill()
                except:
                    pass
            self.active_processes = []
            self.log("[STOP] All processes terminated.")

    def run_command(self, command, log_output=True):
        """Runs a command blocking, returns output."""
        
        # Inject Bundled ADB Path
        if command.strip().startswith("adb "):
             command = command.replace("adb ", f"{self.adb_path} ", 1)
        
        if log_output and "start-server" not in command:
            display_cmd = command
            if self.adb_path in command and len(self.adb_path) > 10:
                display_cmd = command.replace(self.adb_path, "adb")
            self.log(f"[EXEC] {display_cmd}")
            
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                   text=True, shell=True, startupinfo=startupinfo, encoding='utf-8', errors='ignore')
            
            with self.lock:
                self.active_processes.append(proc)
                
            stdout, stderr = proc.communicate()
            
            with self.lock:
                if proc in self.active_processes:
                    self.active_processes.remove(proc)
            
            raw_out = (stdout if stdout else "")
            raw_err = (stderr if stderr else "")
            combined = (raw_out + "\n" + raw_err)

            # --- NUCLEAR NOISE FILTER ---
            junk_patterns = [
                "* daemon", "adb: no devices", "error: no devices", 
                "adb server version", "protocol fault", "vendor_keys", 
                "kill-server", "confirmation dialog", "performing streamed install"
            ]
            
            clean_lines = []
            for line in combined.splitlines():
                line_lower = line.lower()
                if any(p in line_lower for p in junk_patterns):
                    continue
                if "unauthorized" in line_lower and len(line) > 60:
                    continue
                
                cleaned = line.strip().replace("adb.exe: ", "").replace("adb: ", "")
                if cleaned:
                    clean_lines.append(cleaned)
            
            cleaned_result = "\n".join(clean_lines).strip()

            if log_output and cleaned_result:
                self.log(cleaned_result)
            
            return cleaned_result
        except Exception as e:
            if log_output:
                self.log(f"[EXCEPTION] {str(e)}")
            return ""

    def run_async(self, command):
        """Runs command in a separate thread."""
        thread = threading.Thread(target=self.run_command, args=(command,))
        thread.start()
