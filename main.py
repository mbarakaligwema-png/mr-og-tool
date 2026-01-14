from ui.gui_main import OGServiceToolApp
from ui.login import LoginWindow
import customtkinter as ctk

from core.network import check_internet_connection, verify_server_access
import json
import tkinter.messagebox
def start_main_app(username):
    app = OGServiceToolApp(username)
    app.mainloop()

def main():
    # 1. Single Instance Check (Windows)
    import ctypes
    kernel32 = ctypes.windll.kernel32
    mutex_name = "MR_OG_TOOL_MUTEX_UNIQUE_ID_v1"
    
    # Create Named Mutex
    mutex = kernel32.CreateMutexW(0, False, mutex_name)
    last_error = kernel32.GetLastError()
    
    # ERROR_ALREADY_EXISTS = 183
    if last_error == 183:
        # Already running
        # Create a hidden root just to show messagebox/dialog
        root = ctk.CTk()
        root.withdraw()
        tkinter.messagebox.showerror("MR OG TOOL", "Tool is already running!\nTool hii imeshafunguliwa.")
        root.destroy()
        return

    # 2. Internet Connection Check
    if not check_internet_connection():
        # Create a hidden root just to show messagebox/dialog
        root = ctk.CTk()
        root.withdraw()
        tkinter.messagebox.showerror("Connection Error", "Internet inahitajika ili kutumia tool hii")
        root.destroy()
        return

    # 3. Server Verification & Config Setup (AppData)
    import shutil
    import os
    
    app_data = os.getenv('APPDATA')
    tool_data_dir = os.path.join(app_data, "MR_OG_TOOL")
    if not os.path.exists(tool_data_dir):
        os.makedirs(tool_data_dir)
        
    config_path = os.path.join(tool_data_dir, "config.json")
    local_config = "config.json" # In install dir
    
    # Init Config in AppData if missing (Copy from Install Dir)
    if not os.path.exists(config_path):
        if os.path.exists(local_config):
            try:
                shutil.copy(local_config, config_path)
            except: pass
            
    # Load from AppData
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
            server_url = config.get("server_url", "")
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback to local if AppData fails
         try:
            with open(local_config, "r") as f:
                config = json.load(f)
                server_url = config.get("server_url", "")
         except:
            server_url = ""
    
    if not verify_server_access(server_url):
         # Create a hidden root just to show messagebox/dialog
        root = ctk.CTk()
        root.withdraw()
        tkinter.messagebox.showwarning("Server Warning", "Server verification failed.\nStarting Offline Mode.\n(Haiwezi kuunganishwa na server - Inaendelea)")
        root.destroy()

    # Set global theme before creating any window
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    # Pass    
    def start_main_app(username, expiry_msg=""):
        app = OGServiceToolApp(username, expiry_msg) # Assuming OGServiceToolApp is now MainWindow or has been renamed
        app.mainloop()

    login_window = LoginWindow(on_login_success=start_main_app)
    login_window.mainloop()

if __name__ == "__main__":
    main()
