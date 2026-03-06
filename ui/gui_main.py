import customtkinter as ctk
from PIL import Image
import os
import json
from ui import styles
from core.adb_manager import ADBManager
from core.fastboot_manager import FastbootManager
from core.mtk_manager import MTKManager
from core.samsung_manager import SamsungManager
from core.spd_manager import SPDManager
from core.zte_manager import ZTEManager

ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class OGServiceToolApp(ctk.CTk):
    VERSION = "1.7.1"

    def __init__(self, username="User", expiry_msg="LIFETIME"):
        super().__init__()

        self.username = username
        self.expiry_msg = expiry_msg.replace("Expires: ", "") if "Expires: " in expiry_msg else expiry_msg


        # Window Setup
        self.title("MR OG TOOL - Ultimate Phone Repair")
        
        # Center Window logic
        width = styles.WINDOW_WIDTH
        height = styles.WINDOW_HEIGHT
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        self.configure(fg_color=styles.BACKGROUND)

        # --- Set Icon (Robust Method) ---
        import sys
        if getattr(sys, 'frozen', False):
             if hasattr(sys, '_MEIPASS'):
                 base_path = sys._MEIPASS
             else:
                 base_path = os.path.dirname(sys.executable)
        else:
             base_path = os.getcwd()

        # 1. Taskbar Icon (.ico)
        ico_path = os.path.join(base_path, "assets", "logo.ico")
        if os.path.exists(ico_path):
            try: self.iconbitmap(ico_path)
            except: pass
            
        # 2. Title Bar Icon (.png via iconphoto) - Fixes "C" logo
        png_path = os.path.join(base_path, "assets", "logo_round.png")
        if os.path.exists(png_path):
            try:
                from PIL import ImageTk, Image
                # Use standard Tkinter PhotoImage for iconphoto
                icon_img = ImageTk.PhotoImage(file=png_path)
                self.iconphoto(False, icon_img)
            except Exception as e:
                print(f"Icon Error: {e}")

        # --- Set Icon for Main Window ---
        import sys
        if getattr(sys, 'frozen', False):
             if hasattr(sys, '_MEIPASS'):
                 base_path = sys._MEIPASS
             else:
                 base_path = os.path.dirname(sys.executable)
        else:
             base_path = os.getcwd()
        
        icon_path = os.path.join(base_path, "assets", "logo.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except: pass

        # Taskbar ID
        try:
            import ctypes
            myappid = 'mrog.tool.repair.v1.7'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except: pass

        # Force Update Icon
        self.after(200, self.force_icon_update)

        # Layout Configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def force_icon_update(self):
        """Forces the icon application after window is mapped."""
        import sys
        if getattr(sys, 'frozen', False):
             if hasattr(sys, '_MEIPASS'):
                 base_path = sys._MEIPASS
             else:
                 base_path = os.path.dirname(sys.executable)
        else:
             base_path = os.getcwd()
        
        # 1. ICO (Taskbar)
        ico_path = os.path.join(base_path, "assets", "logo.ico")
        if os.path.exists(ico_path):
            try: self.iconbitmap(ico_path)
            except: pass
            
        # 2. PNG (Title Bar)
        png_path = os.path.join(base_path, "assets", "logo_round.png")
        if os.path.exists(png_path):
            try:
                from PIL import ImageTk, Image
                icon_img = ImageTk.PhotoImage(file=png_path)
                self.iconphoto(False, icon_img)
            except Exception as e: print(f"Icon Error: {e}")

        # Create Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=styles.SIDEBAR_WIDTH, corner_radius=0, fg_color=styles.SIDEBAR_BG)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(15, weight=1) # Spacer at very bottom

        # Sidebar Title (Stylish Text)
        self.logo_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.logo_frame.grid(row=0, column=0, padx=20, pady=(30, 10), sticky="ew")
        
        ctk.CTkLabel(self.logo_frame, text="MR OG", 
                     font=ctk.CTkFont(size=28, weight="bold", family="Arial Black"), 
                     text_color="#FFFFFF").pack(anchor="w")
                     
        ctk.CTkLabel(self.logo_frame, text="TOOL", 
                     font=ctk.CTkFont(size=28, weight="bold", family="Arial Black"), 
                     text_color=styles.ACCENT_COLOR).pack(anchor="w")

        ctk.CTkLabel(self.logo_frame, text="PREMIUM UNLOCKER", 
                     font=ctk.CTkFont(size=10, weight="bold"), 
                     text_color=styles.TEXT_SECONDARY).pack(anchor="w", pady=(0, 0))
        # Version Label
        self.version_label = ctk.CTkLabel(self.sidebar_frame, text=f"v{self.VERSION}", font=ctk.CTkFont(size=12, weight="bold"), text_color="#666")
        self.version_label.grid(row=1, column=0, padx=20, pady=(0, 10))
        
        # User Info (New)
        expiry_text = "LIFETIME" # Default
        # Try to parse expiry from passed argument or network check if possible
        # For now, we will update this text if passed in constructor
        
        self.user_info_label = ctk.CTkLabel(self.sidebar_frame, text=f"User: {self.username}\nExp: {self.expiry_msg}", 
                                            font=ctk.CTkFont(size=11, weight="bold"), text_color="#FFD700")
        self.user_info_label.grid(row=2, column=0, padx=20, pady=(0, 10))

        # Separator Line
        self.sidebar_separator = ctk.CTkFrame(self.sidebar_frame, height=2, fg_color=styles.ACCENT_COLOR)
        self.sidebar_separator.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))

        # Sidebar Buttons
        self.sidebar_buttons = []
        self.sidebar_button_dashboard = self.create_sidebar_button("DASHBOARD", command=self.show_dashboard)
        self.sidebar_button_dashboard.grid(row=4, column=0, padx=20, pady=5)

        self.sidebar_button_adb = self.create_sidebar_button("ANDROID", command=self.show_adb)
        self.sidebar_button_adb.grid(row=5, column=0, padx=20, pady=5)

        self.sidebar_button_mtk = self.create_sidebar_button("MEDIATEK", command=self.show_mtk)
        self.sidebar_button_mtk.grid(row=6, column=0, padx=20, pady=5)

        self.sidebar_button_samsung = self.create_sidebar_button("SAMSUNG", command=self.show_samsung)
        self.sidebar_button_samsung.grid(row=7, column=0, padx=20, pady=5)

        self.sidebar_button_spd = self.create_sidebar_button("SPD / UNISOC", command=self.show_spd)
        self.sidebar_button_spd.grid(row=8, column=0, padx=20, pady=5)

        self.sidebar_button_zte = self.create_sidebar_button("ZTE", command=self.show_zte)
        self.sidebar_button_zte.grid(row=9, column=0, padx=20, pady=5)
        
        self.sidebar_button_downgrade = self.create_sidebar_button("DOWNGRADE", command=self.show_downgrade)
        self.sidebar_button_downgrade.grid(row=10, column=0, padx=20, pady=5)

        self.sidebar_button_apps = self.create_sidebar_button("APP MANAGER", command=self.show_apps)
        self.sidebar_button_apps.grid(row=11, column=0, padx=20, pady=5)



        # Status Footer (Detailed)
        self.status_bar = ctk.CTkFrame(self, height=30, corner_radius=0, fg_color="#2D2D30")
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        # Left: Port Info
        self.port_label = ctk.CTkLabel(self.status_bar, text="Port: Scanning...", font=ctk.CTkFont(size=12, family="Consolas"), text_color="#00FF00")
        self.port_label.pack(side="left", padx=20)
        
        # Separator
        ctk.CTkLabel(self.status_bar, text="|", text_color="#555555").pack(side="left", padx=5)

        # Middle: User Info
        user_text = f"User: {self.username}"
        self.user_status_label = ctk.CTkLabel(self.status_bar, text=user_text, font=ctk.CTkFont(size=12, weight="bold"), text_color="#FFFFFF")
        self.user_status_label.pack(side="left", padx=10)

        # Separator
        ctk.CTkLabel(self.status_bar, text="|", text_color="#555555").pack(side="left", padx=5)


        # Separator
        ctk.CTkLabel(self.status_bar, text="|", text_color="#555555").pack(side="left", padx=5)

        # Device Model Label (Auto-Detect)
        self.model_label = ctk.CTkLabel(self.status_bar, text="Model: Waiting...", font=ctk.CTkFont(size=12, weight="bold"), text_color="#00FFFF")
        self.model_label.pack(side="left", padx=10)

        # Live Screen Button (SCRCPY)
        self.scrcpy_btn = ctk.CTkButton(self.status_bar, text="LIVE SCREEN", width=80, height=22, 
                                      fg_color="#673AB7", hover_color="#512DA8",
                                      font=ctk.CTkFont(size=11, weight="bold"),
                                      command=self.launch_scrcpy)
        self.scrcpy_btn.pack(side="left", padx=5, pady=4)

        # Right: Stop Button
        self.stop_btn = ctk.CTkButton(self.status_bar, text="STOP", width=80, height=22, 
                                      fg_color=styles.ERROR_COLOR, hover_color="#D32F2F",
                                      font=ctk.CTkFont(size=11, weight="bold"),
                                      command=self.stop_all_operations)
        self.stop_btn.pack(side="right", padx=10, pady=4)

        # Main Content Area (Split into Content + Console)
        self.right_side_panel = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.right_side_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.right_side_panel.grid_rowconfigure(0, weight=4) # Content area (Gave more weight)
        self.right_side_panel.grid_rowconfigure(1, weight=1) # Console area
        self.right_side_panel.grid_columnconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self.right_side_panel, corner_radius=10, fg_color=styles.BACKGROUND) # Transparent container
        self.main_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        # Console Area
        self.console_frame = ctk.CTkFrame(self.right_side_panel, corner_radius=10, fg_color="#111111")
        self.console_frame.grid(row=1, column=0, sticky="nsew")
        
        self.console_label = ctk.CTkLabel(self.console_frame, text="Log Output", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray")
        self.console_label.pack(anchor="w", padx=10, pady=(5,0))
        
        self.console_text = ctk.CTkTextbox(self.console_frame, font=ctk.CTkFont(family="Consolas", size=12), text_color="#00FF00", fg_color="transparent")
        self.console_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.console_text.configure(state="disabled")

        # Initialize Managers
        self.adb_manager = ADBManager(self.append_log)
        
        # Start Auto-Detect Thread
        self.start_device_monitor()

    def start_device_monitor(self):
        import threading
        import time
        import subprocess

        def monitor():
            # Give UI time to render first
            time.sleep(3)
            
            # ADB Server Reset (Fix for connection issues)
            try:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.run(["adb", "kill-server"], startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
                subprocess.run(["adb", "start-server"], startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
            except: pass

            last_model = ""
            while True:
                try:
                    # Use Smart Status from ADB Manager
                    status = self.adb_manager.get_smart_status()
                    
                    if status['adb_state'] == "ONLINE":
                        model = status['model']
                        self.port_label.configure(text=f"Port: ADB ({model})", text_color="#00FF00")
                        self.model_label.configure(text=f"Model: {model}")
                        last_model = model
                    else:
                        # Check Fastboot
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        proc = subprocess.Popen(["fastboot", "devices"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo, text=True)
                        fb_out, _ = proc.communicate()
                        
                        if fb_out.strip():
                            fb_id = fb_out.split()[0]
                            self.port_label.configure(text=f"Port: FASTBOOT ({fb_id})", text_color="#00BFFF")
                            self.model_label.configure(text="Model: [FASTBOOT]")
                        else:
                            self.port_label.configure(text="Port: Disconnected", text_color="red")
                            self.model_label.configure(text="Model: -")
                            last_model = ""

                except Exception:
                    pass
                time.sleep(5)

        threading.Thread(target=monitor, daemon=True).start()
        self.fastboot_manager = FastbootManager(self.append_log)
        self.mtk_manager = MTKManager(self.append_log)
        self.samsung_manager = SamsungManager(self.append_log)
        self.spd_manager = SPDManager(self.append_log)
        self.zte_manager = ZTEManager(self.append_log)

        # Initialize Defaults
        self.select_frame_by_name("DASHBOARD")

        # Start Port Scanner (Threaded)
        self.start_port_scanner()
        
        # Check for Updates (Threaded)
        self.check_for_updates()

    def launch_scrcpy(self):
        self.append_log("[HEADER] [TOOLS] LAUNCHING SCRCPY (LIVE SCREEN)")
        
        # Paths to check
        assets = os.path.join(os.getcwd(), 'assets')
        tools_dir = os.path.join(assets, "tools")
        
        target = None
        
        # 1. Check known paths first (Fast)
        known_paths = [
            os.path.join(tools_dir, "scrcpy", "scrcpy.exe"),
            os.path.join(tools_dir, "scrcpy.exe")
        ]
        
        for p in known_paths:
            if os.path.exists(p):
                target = p
                break
                
        # 2. Deep Search in tools (Smart)
        if not target and os.path.exists(tools_dir):
            for root, dirs, files in os.walk(tools_dir):
                if "scrcpy.exe" in files:
                    target = os.path.join(root, "scrcpy.exe")
                    break
        
        if not target:
            self.append_log("[RED]SCRCPY not found!")
            self.append_log("[INFO] Please download Scrcpy and place it in:")
            self.append_log(f"[INFO] {paths[0]}")
            self.append_log("[INFO] Or: assets/tools/scrcpy.exe")
            return

        self.append_log("Launching Scrcpy...")
        
        # Launch non-blocking
        import threading
        import subprocess
        
        def _run():
            try:
                # Use os.startfile on Windows for "native" launch (handles paths/environment better)
                if os.name == 'nt':
                    self.append_log(f"Initializing Video Stream... [BLUE]WAIT")
                    # Change CWD temporarily to tool dir
                    old_wd = os.getcwd()
                    tool_dir = os.path.dirname(target)
                    try:
                        os.chdir(tool_dir)
                        os.startfile("scrcpy.exe")
                    finally:
                        os.chdir(old_wd)
                    
                    self.append_log("LIVE SCREEN... [GREEN]ACTIVE")
                else:
                    subprocess.Popen([target], cwd=os.path.dirname(target), shell=True)
            except Exception as e:
                self.append_log(f"[RED]Failed to launch: {e}")
        
        threading.Thread(target=_run, daemon=True).start()

    def check_for_updates(self):
        import threading
        import requests
        import webbrowser
        
        def check():
            try:
                # Assuming config.json has server_url, we need to load it again or pass it
                # For now, let's try to get it from self.username if we stored it? No.
                # Let's read config safely
                server_url = "https://mrogtool.com" # Default
                try:
                    app_data = os.getenv('APPDATA')
                    config_path = os.path.join(app_data, "MR_OG_TOOL", "config.json")
                    if os.path.exists(config_path):
                        with open(config_path, "r") as f:
                            data = json.load(f)
                            server_url = data.get("server_url", server_url)
                except: pass
                
                api_url = f"{server_url}/api/v1/latest_version"
                response = requests.get(api_url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    server_ver = data.get("version", "1.0.0")
                    download_url = data.get("download_url", "")
                    changelog = data.get("changelog", "")
                    
                    # Simple Version Compare (String compare is risky for 1.10 vs 1.2, but ok for now)
                    # Better: split by dot
                    def parse_version(v):
                        return tuple(map(int, (v.split("."))))
                        
                    local_v = parse_version(self.VERSION.replace("v",""))
                    server_v = parse_version(server_ver.replace("v",""))
                    
                    if server_v > local_v:
                        # Update Available!
                        self.after(2000, lambda: self.show_update_dialog(server_ver, download_url, changelog))
            except Exception as e:
                print(f"Update Check User Error: {e}")

        t = threading.Thread(target=check, daemon=True)
        t.start()

    def show_update_dialog(self, version, url, changelog):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Update Available 🚀")
        dialog.geometry("400x350")
        dialog.attributes("-topmost", True)
        dialog.configure(fg_color=styles.BACKGROUND)
        
        ctk.CTkLabel(dialog, text="NEW UPDATE AVAILABLE!", font=ctk.CTkFont(size=18, weight="bold"), text_color="#00FF00").pack(pady=(20, 10))
        ctk.CTkLabel(dialog, text=f"Version: v{version}", font=ctk.CTkFont(size=14)).pack(pady=5)
        
        log_box = ctk.CTkTextbox(dialog, height=100)
        log_box.pack(padx=20, pady=10, fill="x")
        log_box.insert("1.0", f"Changelog:\n{changelog}")
        log_box.configure(state="disabled")
        
        import webbrowser
        def open_url():
            webbrowser.open(url)
            dialog.destroy()
            
        ctk.CTkButton(dialog, text="DOWNLOAD NOW", command=open_url, fg_color=styles.ACCENT_COLOR, height=40).pack(pady=20)

    def start_port_scanner(self):
        import threading
        import time
        import subprocess
        
        def scan():
            while True:
                status_text = "Port: No Device"
                color = "gray"
                found = False

                # 1. Check ADB
                try:
                    # startupinfo to hide window
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    
                    adb_res = subprocess.check_output("adb devices", startupinfo=startupinfo).decode()
                    lines = adb_res.strip().split('\n')
                    for line in lines:
                        if "\tdevice" in line or "\trecovery" in line:
                            dev_id = line.split('\t')[0]
                            status_text = f"ADB: {dev_id}"
                            color = "#00FF00" # Green
                            found = True
                            break
                except: pass
                
                # 2. Check COM Ports (if no ADB found yet)
                if not found:
                    try:
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        
                        cmd = 'wmic path Win32_PnPEntity where "Caption like \'%(COM%)\'" get Caption'
                        com_res = subprocess.check_output(cmd, startupinfo=startupinfo).decode()
                        
                        lines = [x.strip() for x in com_res.split('\n') if x.strip() and "Caption" not in x]
                        
                        # Priority for known drivers
                        priority_drivers = ["Mediatek", "Samsung", "Spreadtrum", "Qualcomm", "Unisoc", "Android", "USB Serial"]
                        
                        best_port = None
                        for p in lines:
                            for d in priority_drivers:
                                if d.lower() in p.lower():
                                    best_port = p
                                    break
                            if best_port: break
                        
                        if not best_port and lines:
                            best_port = lines[0] # Grab first available if no priority match

                        if best_port:
                            # Truncate if too long
                            if len(best_port) > 40:
                                best_port = best_port[:37] + "..."
                            status_text = f"{best_port}"
                            color = "#00BFFF"
                            found = True
                    except: pass
                
                # Update UI
                try:
                    self.port_label.configure(text=status_text, text_color=color)
                except: 
                    break # Exit thread if UI dead
                
                time.sleep(5) # Reduced polling frequency to prevent ADB conflicts
        
        t = threading.Thread(target=scan, daemon=True)
        t.start()

    def append_log(self, text):
        import re
        if hasattr(self, 'console_text'):
            self.console_text.configure(state="normal")
            
            # --- Configure Styles (Hacker / Pro Theme) ---
            # Header: Blue block with white text
            self.console_text.tag_config("HEADER", background="#007ACC", foreground="white", spacing1=5, spacing3=5)
            
            # Colors
            self.console_text.tag_config("GREEN", foreground="#00FF00")   # Success / Go
            self.console_text.tag_config("BLUE", foreground="#00BFFF")    # Info / Data
            self.console_text.tag_config("RED", foreground="#FF4444")     # Error / Stop
            self.console_text.tag_config("YELLOW", foreground="#FFD700")  # Warning / Process
            self.console_text.tag_config("WHITE", foreground="#FFFFFF")   # Standard Text
            self.console_text.tag_config("GRAY", foreground="#888888")    # Debug / Low priority
            
            # --- Parse & Insert ---
            # Split by tags: [TAG]
            parts = re.split(r'(\[(?:HEADER|GREEN|BLUE|RED|YELLOW|WHITE|GRAY)\])', text)
            
            current_tag = "GRAY" # Default color for lines without tags
            
            # Special case: If line starts with [HEADER], apply to whole line usually, 
            # but our loop handles it chunk by chunk.
            
            for part in parts:
                if part.startswith("[") and part.endswith("]"):
                    tag_candidate = part[1:-1]
                    if tag_candidate in ["HEADER", "GREEN", "BLUE", "RED", "YELLOW", "WHITE", "GRAY"]:
                        current_tag = tag_candidate
                else:
                    if part:
                        self.console_text.insert("end", part, current_tag)
            
            self.console_text.insert("end", "\n")
            self.console_text.see("end")
            self.console_text.configure(state="disabled")
        else:
            # Fallback for CLI debugging
            clean = re.sub(r'\[.*?\]', '', text)
            print(clean)

    def create_sidebar_button(self, text, command):
        """Helper to create consistent sidebar buttons."""
        return ctk.CTkButton(self.sidebar_frame, text=text, command=command,
                             height=40,
                             corner_radius=8,
                             font=ctk.CTkFont(size=13, weight="bold"),
                             fg_color="transparent",
                             text_color=styles.TEXT_SECONDARY,
                             hover_color=styles.CARD_BG,
                             anchor="w")

    def stop_all_operations(self):
        """Stops any running command in all managers."""
        self.append_log("[USER] STOP REQUESTED...")
        
        stopped_something = False
        managers = [self.adb_manager, self.fastboot_manager, self.mtk_manager, self.samsung_manager, self.spd_manager, self.zte_manager]
        
        for mgr in managers:
            if hasattr(mgr, 'cmd'):
                # We check if it WAS running before stopping
                if mgr.cmd.process and mgr.cmd.process.poll() is None:
                     mgr.cmd.stop_current_process()
                     stopped_something = True
                
            # Also reset flags like 'is_running' for threaded tasks
            if hasattr(mgr, 'is_running'):
                if mgr.is_running:
                    mgr.is_running = False
                    stopped_something = True

        if stopped_something:
            self.append_log("[RED]🛑 ALL OPERATIONS STOPPED.")
        else:
            self.append_log("[GRAY]No active operations to stop.")

    def select_frame_by_name(self, name):
        # Reset button styles
        buttons = [self.sidebar_button_dashboard, self.sidebar_button_adb, 
                   self.sidebar_button_mtk, self.sidebar_button_samsung, self.sidebar_button_spd, 
                   self.sidebar_button_zte, self.sidebar_button_downgrade, self.sidebar_button_apps]
        for btn in buttons:
            if btn.cget("text") == name:
                 btn.configure(fg_color=styles.ACCENT_COLOR, text_color="white")
            else:
                 btn.configure(fg_color="transparent", text_color=styles.TEXT_SECONDARY)
        
        # Clear main frame (Simple approach for now, usually we use grid_forget)
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Show content based on name
        if name == "DASHBOARD":
            self.show_dashboard_content()
        elif name == "ANDROID":
            self.show_adb_content()
        elif name == "FASTBOOT":
            self.show_fastboot_content()
        elif name == "MEDIATEK":
            self.show_mtk_content()
        elif name == "SAMSUNG":
            self.show_samsung_content()
        elif name == "SPD / UNISOC":
            self.show_spd_content()
        elif name == "ZTE":
            self.show_zte_content()
        elif name == "DOWNGRADE":
            self.show_downgrade_content()
        elif name == "APP MANAGER":
            self.show_apps_content()
        elif name == "SETTINGS":
            self.show_settings_content(self.main_frame)

    def show_dashboard(self):
        self.select_frame_by_name("DASHBOARD")

    def show_adb(self):
        self.select_frame_by_name("ANDROID")

    def show_fastboot(self):
        self.select_frame_by_name("FASTBOOT")

    def show_mtk(self):
        self.select_frame_by_name("MEDIATEK")

    def show_samsung(self):
        self.select_frame_by_name("SAMSUNG")

    def show_spd(self):
        self.select_frame_by_name("SPD / UNISOC")
    
    def show_zte(self):
        self.select_frame_by_name("ZTE")
        
    def show_downgrade(self):
        self.select_frame_by_name("DOWNGRADE")

    def show_apps(self):
        self.select_frame_by_name("APP MANAGER")



    # --- Content Populators ---
    
    def show_dashboard_content(self):
        # Header Info
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(header_frame, text="SMART DASHBOARD", 
                     font=ctk.CTkFont(size=24, weight="bold"), 
                     text_color=styles.ACCENT_COLOR).pack(side="left")
        
        self.db_adb_status = ctk.CTkLabel(header_frame, text="ADB: DISCONNECTED", 
                                        font=ctk.CTkFont(size=12, weight="bold"), 
                                        text_color="gray")
        self.db_adb_status.pack(side="right")

        # Cards Grid
        grid_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=20, pady=10)
        grid_frame.grid_columnconfigure((0, 1), weight=1)

        def create_status_card(parent, title, value="N/A", row=0, col=0):
            card = ctk.CTkFrame(parent, fg_color=styles.CARD_BG, corner_radius=10, height=120)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            card.grid_propagate(False)
            
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color="gray").pack(pady=(15, 0))
            lbl = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=20, weight="bold"), text_color="white")
            lbl.pack(pady=(10, 0))
            return lbl

        self.lbl_db_model = create_status_card(grid_frame, "DEVICE MODEL", row=0, col=0)
        self.lbl_db_kg = create_status_card(grid_frame, "KG / KNOX STATUS", row=0, col=1)
        self.lbl_db_frp = create_status_card(grid_frame, "FRP LOCK STATE", row=1, col=0)
        self.lbl_db_security = create_status_card(grid_frame, "SECURITY PATCH", row=1, col=1)

        # Quick Actions
        ctk.CTkLabel(self.main_frame, text="RECOMMENDED ACTIONS", font=ctk.CTkFont(size=14, weight="bold"), text_color="gray").pack(pady=(20, 5))
        
        self.recommendation_label = ctk.CTkLabel(self.main_frame, text="Connect a device to see recommendations.", font=ctk.CTkFont(size=13))
        self.recommendation_label.pack(pady=5)

        # Start Update Loop if not already running
        if not hasattr(self, '_db_update_running'):
            self._db_update_running = True
            self.update_dashboard_status()

    def update_dashboard_status(self):
        """Periodically refreshes the dashboard UI with device data."""
        if not hasattr(self, 'lbl_db_model') or not self.lbl_db_model.winfo_exists():
            # If dashboard is not visible or destroyed, stop or wait
            self.after(5000, self.update_dashboard_status)
            return

        def _bg_task():
            status = self.adb_manager.get_smart_status()
            
            # Update UI safely
            self.after(0, lambda s=status: self._apply_status_to_ui(s))

        import threading
        threading.Thread(target=_bg_task, daemon=True).start()
        
        # Schedule next update
        self.after(5000, self.update_dashboard_status)

    def _apply_status_to_ui(self, s):
        try:
            # Update Labels
            self.lbl_db_model.configure(text=s['model'])
            self.lbl_db_security.configure(text=s['security_patch'])
            
            # KG Status with Colors
            kg = s['kg_status']
            self.lbl_db_kg.configure(text=kg)
            if "PRENORMAL" in kg: self.lbl_db_kg.configure(text_color="#FFA500") # Orange
            elif "LOCKED" in kg or "ACTIVE" in kg: self.lbl_db_kg.configure(text_color="#FF4444") # Red
            elif "COMPLETED" in kg or "OFFLINE" not in kg: self.lbl_db_kg.configure(text_color="#00FF00")
            
            # FRP Status
            frp = s['frp_status']
            self.lbl_db_frp.configure(text=frp, text_color="#FF4444" if frp == "LOCKED" else "#00FF00")
            
            # ADB Header
            self.db_adb_status.configure(text=f"ADB: {s['adb_state']}", text_color="#00FF00" if s['adb_state'] == "ONLINE" else "gray")
            
            # Recommendations
            if s['adb_state'] == "ONLINE":
                if frp == "LOCKED":
                    self.recommendation_label.configure(text="TIP: Go to ANDROID tab and use 'Remove FRP' if you are stuck.", text_color="#00BFFF")
                else:
                    self.recommendation_label.configure(text="Device status is healthy. Ready for operations.", text_color="#00FF00")
            else:
                self.recommendation_label.configure(text="Connect a device via USB and enable ADB.", text_color="gray")
                
        except Exception:
            pass


    def show_adb_content(self):
        ctk.CTkLabel(self.main_frame, text="ADB OPERATIONS", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=10)
        
        grid_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True)

        buttons_data = [
            ("Read Info", self.adb_manager.read_info),
            ("Reboot System", self.adb_manager.reboot_device),
            ("Reboot Bootloader", self.adb_manager.reboot_bootloader),
            ("Reboot Recovery", self.adb_manager.reboot_recovery),
            ("Remove FRP (Generic)", self.adb_manager.remove_frp_persistent),
            ("A16 OEM UNLOCK", self.adb_manager.android16_oem_unlock)
        ]
        
        for i, (text, cmd) in enumerate(buttons_data):
             btn = ctk.CTkButton(grid_frame, text=text, height=50, fg_color=styles.CARD_BG, hover_color=styles.ACCENT_COLOR, command=cmd)
             btn.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="ew")

        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        grid_frame.grid_columnconfigure(2, weight=1)


    def show_fastboot_content(self):
        ctk.CTkLabel(self.main_frame, text="FASTBOOT OPERATIONS", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=10)
        
        grid_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True)

        buttons_data = [
            ("Read Info", self.fastboot_manager.read_info),
            ("Reboot System", self.fastboot_manager.reboot_system),
            ("Reboot EDL", self.fastboot_manager.reboot_edl),
            ("Unlock Bootloader", self.fastboot_manager.unlock_bootloader),
            ("Relock Bootloader", self.fastboot_manager.relock_bootloader),
            ("Erase FRP", self.fastboot_manager.erase_frp),
            ("Wipe Userdata", self.fastboot_manager.wipe_userdata)
        ]
        
        for i, (text, cmd) in enumerate(buttons_data):
             btn = ctk.CTkButton(grid_frame, text=text, height=50, fg_color=styles.CARD_BG, hover_color=styles.ACCENT_COLOR, command=cmd)
             btn.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="ew")

        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        grid_frame.grid_columnconfigure(2, weight=1)

    def show_mtk_content(self):
         ctk.CTkLabel(self.main_frame, text="MEDIATEK (BROM/PRELOADER)", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=10)
         
         grid_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
         grid_frame.pack(fill="both", expand=True)

         buttons_data = [
            ("Keypad Mobile", self.mtk_manager.open_keypad_tool),
            ("BYPASS", self.mtk_manager.stealth_bypass)
         ]
         
         for i, (text, cmd) in enumerate(buttons_data):
             btn = ctk.CTkButton(grid_frame, text=text, height=50, fg_color=styles.CARD_BG, hover_color=styles.ACCENT_COLOR, command=cmd)
             btn.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="ew")

         grid_frame.grid_columnconfigure(0, weight=1)
         grid_frame.grid_columnconfigure(1, weight=1)
         grid_frame.grid_columnconfigure(2, weight=1)

    def show_samsung_content(self):
         ctk.CTkLabel(self.main_frame, text="SAMSUNG OPERATIONS", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=10)
         
         tabview = ctk.CTkTabview(self.main_frame)
         tabview.pack(fill="both", expand=True)
         
         tab_main = tabview.add("Main")
         tab_odin = tabview.add("Odin Flash")
         
         # --- MAIN TAB UI ---
         grid_frame = ctk.CTkFrame(tab_main, fg_color="transparent")
         grid_frame.pack(fill="both", expand=True)
         
         # Remove FIX LOG from general grid and add special row for it
         buttons_data = [
            ("Read Info (MTP)", self.samsung_manager.read_info_mtp),
            ("Reboot Download", self.samsung_manager.reboot_download),
            ("Factory Reset", self.samsung_manager.factory_reset),
            ("Enable ADB (QR)", self.samsung_manager.enable_adb_qr),
            ("Remove FRP (2024)", self.samsung_manager.remove_frp_2024),
            ("Exit Download Mode", self.samsung_manager.exit_download_mode),
            ("KG UNLOCK 2026", self.samsung_manager.kg_bypass_android_15_16),
            ("NEW FIRE 🔥", self.samsung_manager.new_fire_security_patch)
         ]
         
         row_idx = 0
         for i, (text, cmd) in enumerate(buttons_data):
             btn = ctk.CTkButton(grid_frame, text=text, height=50, fg_color=styles.CARD_BG, hover_color=styles.ACCENT_COLOR, command=cmd)
             btn.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="ew")
             row_idx = i//3

         # --- SPECIAL FIX LOG SECTION (Kishimo) ---
         fix_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
         fix_frame.grid(row=row_idx+1, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
         
         ctk.CTkLabel(fix_frame, text="FIX LOG:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 10))
         
         self.fix_log_model_var = ctk.StringVar(value="A05")
         model_menu = ctk.CTkOptionMenu(fix_frame, variable=self.fix_log_model_var, 
                                        values=["A05", "A06"],
                                        fg_color=styles.CARD_BG, button_color=styles.ACCENT_COLOR, width=200)
         model_menu.pack(side="left", padx=10)
         
         def run_fix_log():
             model = self.fix_log_model_var.get()
             self.samsung_manager.fix_stuck_logo(model)
             
         ctk.CTkButton(fix_frame, text="RUN FIX", width=100, fg_color=styles.ACCENT_COLOR, command=run_fix_log).pack(side="left")
        
         grid_frame.grid_columnconfigure(0, weight=1)
         grid_frame.grid_columnconfigure(1, weight=1)
         grid_frame.grid_columnconfigure(2, weight=1)

         # --- ODIN FLASH UI ---
         odin_frame = ctk.CTkFrame(tab_odin, fg_color="transparent")
         odin_frame.pack(fill="both", expand=True, padx=20, pady=20)
         
         # Description
         ctk.CTkLabel(odin_frame, text="Samsung Odin Flash Tool", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(40, 10))
         ctk.CTkLabel(odin_frame, text="Click below to open independent Odin Flash Tool", text_color="gray").pack(pady=(0, 30))

         # Flash Button
         flash_btn = ctk.CTkButton(odin_frame, text="OPEN ODIN", height=60, fg_color=styles.ACCENT_COLOR, 
                                   font=ctk.CTkFont(size=16, weight="bold"),
                                   command=self.perform_odin_flash)
         flash_btn.pack(fill="x", padx=50)

    def show_fix_logo_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Select Model - Fix Stuck Logo")
        dialog.geometry("400x500")
        dialog.attributes("-topmost", True)
        dialog.configure(fg_color=styles.BACKGROUND)
        
        ctk.CTkLabel(dialog, text="SELECT MODEL TO FIX", font=ctk.CTkFont(size=18, weight="bold"), text_color="#00BFFF").pack(pady=(20, 10))
        
        scroll_frame = ctk.CTkScrollableFrame(dialog, width=350, height=350, fg_color="transparent")
        scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)

        models = [
            "Samsung A05 (Root/Exploit)",
            "Samsung A06 (Root/Exploit)"
        ]

        def run_fix(model_name):
            dialog.destroy()
            self.samsung_manager.fix_stuck_logo(model_name)

        for model in models:
            ctk.CTkButton(scroll_frame, text=model, height=40, 
                          fg_color=styles.CARD_BG, hover_color=styles.ACCENT_COLOR,
                          command=lambda m=model: run_fix(m)).pack(pady=5, fill="x")

        ctk.CTkButton(dialog, text="CANCEL", fg_color=styles.ERROR_COLOR, command=dialog.destroy).pack(pady=10)

    def browse_odin_file(self, file_type):
        pass # Deprecated

    def perform_odin_flash(self):
        # Directly launch Odin manager with empty files, which triggers the GUI launcher we implemented
        files = {"BL": "", "AP": "", "CP": "", "CSC": ""} 
        self.samsung_manager.flash_odin(files)



    def show_spd_content(self):
         ctk.CTkLabel(self.main_frame, text="SPD / UNISOC DIAGNOSTIC", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=10)
         
         grid_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
         grid_frame.pack(fill="both", expand=True)

         # Map actions to functions
         buttons_data = [
            ("BYPASS", self.spd_manager.stealth_bypass),
            ("FIX SUPER", self.spd_manager.patch_super_img),
            ("FIX USB / DIAG", self.spd_manager.fix_usb_diag)
         ]
         
         for i, (text, cmd) in enumerate(buttons_data):
             btn = ctk.CTkButton(grid_frame, text=text, height=50, fg_color=styles.CARD_BG, hover_color=styles.ACCENT_COLOR, command=cmd)
             btn.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="ew")

         grid_frame.grid_columnconfigure(0, weight=1)
         grid_frame.grid_columnconfigure(1, weight=1)
         grid_frame.grid_columnconfigure(2, weight=1)

    def show_zte_content(self):
         ctk.CTkLabel(self.main_frame, text="ZTE / OTHER OPERATIONS", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=10)
         
         grid_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
         grid_frame.pack(fill="both", expand=True)

         buttons_data = [
            ("A34 (ADB)", self.zte_manager.a34_bypass),
            ("A35 (ADB)", self.zte_manager.a35_bypass),
            ("A75 (ADB)", self.zte_manager.a75_bypass),
            ("QR Code", self.show_zte_qr_window),
         ]
         
         for i, (text, cmd) in enumerate(buttons_data):
             btn = ctk.CTkButton(grid_frame, text=text, height=50, fg_color=styles.CARD_BG, hover_color=styles.ACCENT_COLOR, command=cmd)
             btn.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="ew")

         grid_frame.grid_columnconfigure(0, weight=1)
         grid_frame.grid_columnconfigure(1, weight=1)
         grid_frame.grid_columnconfigure(2, weight=1)

         # --- SPD BOOT SERVICE SECTION (New) ---
         boot_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
         # Place it below the grid buttons (which take up rows 0 and 1 usually)
         boot_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=(20, 10))
         
         # Header
         ctk.CTkLabel(boot_frame, text="SPD BOOT MODE:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 10))
         
         # Model Dropdown
         self.zte_spd_model_var = ctk.StringVar(value="ZTE A35")
         model_menu = ctk.CTkOptionMenu(boot_frame, variable=self.zte_spd_model_var, 
                                        values=["ZTE A35"],
                                        fg_color=styles.CARD_BG, button_color=styles.ACCENT_COLOR, width=200)
         model_menu.pack(side="left", padx=10)
         
         # Helper to run commands with model
         def run_spd_master_reset():
             self.zte_manager.spd_boot_operation(self.zte_spd_model_var.get(), "ALL")

         # Buttons
         ctk.CTkButton(boot_frame, text="RESET + FRP", width=150, fg_color=styles.ACCENT_COLOR, command=run_spd_master_reset).pack(side="left", padx=5)

    def show_downgrade_content(self):
        ctk.CTkLabel(self.main_frame, text="DOWNLOAD CENTER", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=10)
        
        grid_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True)
        
        # Link 2: ZTE
        url = "https://www.mediafire.com/file/baymgqjav6vyfxk/A35+SULUTION+SOLVED+QR+CODE+BROCKED.rar/file"
        import webbrowser
        
        # Button 2 (ZTE)
        btn = ctk.CTkButton(grid_frame, text="ZTE A35 DOWNGRADE FILE", height=50, 
                            fg_color=styles.CARD_BG, hover_color=styles.ACCENT_COLOR, 
                            command=lambda: webbrowser.open(url))
        btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        grid_frame.grid_columnconfigure(2, weight=1)

    def show_zte_qr_window(self):
        try:
            # Create Toplevel Window
            qr_window = ctk.CTkToplevel(self)
            qr_window.title("ZTE QR Code Operations")
            qr_window.geometry("400x500")
            qr_window.configure(fg_color=styles.BACKGROUND)
            qr_window.attributes("-topmost", True)

            # Title
            ctk.CTkLabel(qr_window, text="SCAN QR CODE", font=ctk.CTkFont(size=20, weight="bold"), text_color=styles.ACCENT_COLOR).pack(pady=(20, 10))
            
            # Load Image
            image_path = os.path.join("assets", "zte_qr.png")
            if os.path.exists(image_path):
                # Standard PIL Image Loading
                pil_image = Image.open(image_path)
                # Resize for display if needed, e.g. 300x300
                pil_image = pil_image.resize((300, 300), Image.Resampling.LANCZOS)
                
                qr_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(300, 300))
                
                img_label = ctk.CTkLabel(qr_window, text="", image=qr_image)
                img_label.pack(pady=10)
                
                ctk.CTkLabel(qr_window, text="Scan with your device to proceed.", text_color=styles.TEXT_SECONDARY).pack(pady=10)
            else:
                ctk.CTkLabel(qr_window, text="[ERROR] QR Code Image Not Found!", text_color=styles.ERROR_COLOR).pack(pady=40)
                ctk.CTkLabel(qr_window, text=f"Missing: {image_path}", text_color="gray", font=ctk.CTkFont(size=10)).pack(pady=5)

            # Close Button
            ctk.CTkButton(qr_window, text="Close", fg_color=styles.ERROR_COLOR, command=qr_window.destroy).pack(pady=20)
            
        except Exception as e:
            self.append_log(f"[ERROR] Failed to open QR Window: {e}")

    def show_settings_content(self, parent):
        title = ctk.CTkLabel(parent, text="SETTINGS", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)
        
        # Only ADMIN can see User Management (Case Insensitive & Stripped)
        # Only ADMIN can see User Management (Case Insensitive & Stripped)
        if str(self.username).strip().lower() in ["mrogtool", "admin"]:
            # User Manager Section
            user_frame = ctk.CTkFrame(parent)
            user_frame.pack(fill="x", padx=20, pady=10)
            
            # EXPLICIT CONFIRMATION LABEL
            ctk.CTkLabel(user_frame, text="✅ ADMIN ACCESS GRANTED", text_color="green", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
            
            ctk.CTkLabel(user_frame, text="User Manager", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
            
            input_frame = ctk.CTkFrame(user_frame, fg_color="transparent")
            input_frame.pack(fill="x", padx=20, pady=5)
            
            self.new_user_entry = ctk.CTkEntry(input_frame, placeholder_text="New Username", width=150)
            self.new_user_entry.pack(side="left", padx=(0, 10))
            
            self.new_pass_entry = ctk.CTkEntry(input_frame, placeholder_text="New Password", width=150)
            self.new_pass_entry.pack(side="left", padx=(0, 10))
            
            self.duration_var = ctk.StringVar(value="6 Hours")
            duration_combo = ctk.CTkComboBox(input_frame, values=["6 Hours", "3 Months", "6 Months", "12 Months"], variable=self.duration_var, width=120)
            duration_combo.pack(side="left", padx=(0, 10))
            
            add_btn = ctk.CTkButton(input_frame, text="Add User", fg_color=styles.ACCENT_COLOR, command=self.add_new_user)
            add_btn.pack(side="left")
            
            # Delete User Section
            delete_frame = ctk.CTkFrame(user_frame, fg_color="transparent")
            delete_frame.pack(fill="x", padx=20, pady=(10, 0))
            
            self.del_user_entry = ctk.CTkEntry(delete_frame, placeholder_text="Username to Delete", width=200)
            self.del_user_entry.pack(side="left", padx=(0, 10))
            
            del_btn = ctk.CTkButton(delete_frame, text="Delete User", fg_color=styles.ERROR_COLOR, hover_color="#D32F2F", command=self.delete_user)
            del_btn.pack(side="left")
            
            # User List Display
            ctk.CTkLabel(user_frame, text="Existing Users (Name | Pass | Expiry | HWID)", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=20, pady=(20, 5))
            
            self.user_list_text = ctk.CTkTextbox(user_frame, height=150, font=ctk.CTkFont(family="Consolas", size=11))
            self.user_list_text.pack(fill="x", padx=20, pady=(0, 20))
            self.user_list_text.configure(state="disabled")
            
            # Initial Load
            self.load_users_list()
        else:
            # Non-Admin View
            info_frame = ctk.CTkFrame(parent)
            info_frame.pack(fill="x", padx=20, pady=10)
            ctk.CTkLabel(info_frame, text=f"Logged in as: {self.username}", font=ctk.CTkFont(size=14)).pack(pady=20)
            ctk.CTkLabel(info_frame, text="Standard User Restricted Mode", text_color="gray").pack(pady=5)
            # Debug hint
            ctk.CTkLabel(info_frame, text=f"(Debug: System sees user as '{self.username}', expected 'mrogtool' or 'admin')", text_color="red", font=ctk.CTkFont(size=10)).pack(pady=5)

    def delete_user(self):
        user_to_del = self.del_user_entry.get()
        if not user_to_del:
            self.append_log("[ERROR] Enter username to delete.")
            return
            
        if user_to_del == "admin":
            self.append_log("[ERROR] Cannot delete default Admin.")
            return

        try:
            users_path = "users.db"
            if os.path.exists(users_path):
                with open(users_path, "r") as f:
                    users = json.load(f)
                
                if user_to_del in users:
                    del users[user_to_del]
                    with open(users_path, "w") as f:
                        json.dump(users, f, indent=4)
                    
                    self.append_log(f"[SUCCESS] User '{user_to_del}' deleted.")
                    self.del_user_entry.delete(0, "end")
                    self.load_users_list()
                else:
                    self.append_log(f"[ERROR] User '{user_to_del}' not found.")
        except Exception as e:
            self.append_log(f"[EXCEPTION] Failed to delete: {e}")

    def load_users_list(self):
        self.user_list_text.configure(state="normal")
        self.user_list_text.delete("1.0", "end")
        
        try:
            users_path = "users.db"
            users = {}
            if os.path.exists(users_path):
                with open(users_path, "r") as f:
                    users = json.load(f)
                    
            if not users:
                self.user_list_text.insert("end", "No users found.")
            else:
                self.user_list_text.insert("end", f"{'USERNAME':<15} | {'PASSWORD':<15} | {'EXPIRY':<20} | {'HWID'}\n")
                self.user_list_text.insert("end", "-"*80 + "\n")
                
                for user, info in users.items():
                    pwd = "???"
                    expiry = "N/A"
                    hwid_status = "Unbound"
                    
                    if isinstance(info, dict):
                        pwd = info.get("password", "???")
                        expiry = info.get("expiry", "Unlimited")
                        if info.get("hwid"):
                            hwid_status = "LOCKED"
                    else:
                        pwd = str(info) # Legacy string format
                    
                    # Check expiry status for display
                    status_marker = ""
                    if expiry != "Unlimited" and expiry != "N/A" and "Server" not in expiry:
                        import datetime
                        try:
                            exp_dt = datetime.datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S")
                            if datetime.datetime.now() > exp_dt:
                                status_marker = " [EXPIRED]"
                        except: pass

                    line = f"{user:<15} | {pwd:<15} | {expiry:<20} | {hwid_status}{status_marker}\n"
                    self.user_list_text.insert("end", line)
                        
        except Exception as e:
            self.user_list_text.insert("end", f"Error loading users: {e}")
            
        self.user_list_text.configure(state="disabled")

    def add_new_user(self):
        user = self.new_user_entry.get()
        pwd = self.new_pass_entry.get()
        duration_str = self.duration_var.get()
        
        if not user or not pwd:
            self.append_log("[ERROR] Username and Password cannot be empty.")
            return
            
        try:
            import datetime
            
            # Calculate Expiry
            now = datetime.datetime.now()
            if "Hours" in duration_str:
                hours = int(duration_str.split()[0])
                expiry_dt = now + datetime.timedelta(hours=hours)
            elif "Months" in duration_str:
                months = int(duration_str.split()[0])
                # Approximate 30 days per month
                expiry_dt = now + datetime.timedelta(days=months*30)
            
            expiry_str = expiry_dt.strftime("%Y-%m-%d %H:%M:%S")

            users_path = "users.db"
            data = {}
            if os.path.exists(users_path):
                with open(users_path, "r") as f:
                    data = json.load(f)
            
            # Ensure admin exists if not present
            if "mrogtool" not in data:
                 data["mrogtool"] = {"password": "dell", "expiry": "Unlimited"}

            if user in data:
                self.append_log(f"[ERROR] User '{user}' already exists.")
                return
            
            # Save structured data
            data[user] = {
                "password": pwd,
                "expiry": expiry_str,
                "created_at": now.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(users_path, "w") as f:
                json.dump(data, f, indent=4)
                
            self.append_log(f"[SUCCESS] User '{user}' added! Expires: {expiry_str}")
            self.new_user_entry.delete(0, "end")
            self.new_pass_entry.delete(0, "end")
            self.load_users_list() # Refresh list
            
        except Exception as e:
            self.append_log(f"[EXCEPTION] Failed to add user: {e}")
    # --- FEATURE: APP MANAGER ---
    def show_apps_content(self):
        ctk.CTkLabel(self.main_frame, text="ADVANCED APP MANAGER", font=ctk.CTkFont(size=20, weight="bold"), text_color=styles.ACCENT_COLOR).pack(anchor="w", pady=10, padx=20)
        
        # Search & Filter Frame
        top_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=5)
        
        self.app_search_var = ctk.StringVar()
        self.app_search_var.trace_add("write", lambda *args: self.filter_apps())
        
        search_entry = ctk.CTkEntry(top_frame, placeholder_text="Search apps...", width=200, textvariable=self.app_search_var)
        search_entry.pack(side="left", padx=(0, 5))
        
        self.app_filter_var = ctk.StringVar(value="All Apps")
        filter_menu = ctk.CTkOptionMenu(top_frame, values=["All Apps", "User Apps", "System Apps"], 
                                        width=120,
                                        variable=self.app_filter_var, command=lambda x: self.refresh_apps_list())
        filter_menu.pack(side="left", padx=5)
        
        refresh_btn = ctk.CTkButton(top_frame, text="REFRESH", width=80, command=self.refresh_apps_list)
        refresh_btn.pack(side="right", padx=2)

        install_btn = ctk.CTkButton(top_frame, text="INSTALL APK", width=100, fg_color=styles.SUCCESS_COLOR, hover_color="#388E3C", command=self.select_and_install_apk)
        install_btn.pack(side="right", padx=2)

        # Scrollable List
        self.app_list_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color=styles.CARD_BG, corner_radius=10)
        self.app_list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.refresh_apps_list()

    def refresh_apps_list(self):
        # Clear current list
        for widget in self.app_list_frame.winfo_children():
            widget.destroy()
            
        filter_val = self.app_filter_var.get()
        f_type = "all"
        if filter_val == "User Apps": f_type = "user"
        elif filter_val == "System Apps": f_type = "system"
        
        def _fetch():
            self.append_log("[INFO] Fetching package list... [BLUE]WAIT")
            packages = self.adb_manager.get_installed_packages(f_type)
            self.after(0, lambda: self.populate_apps(packages))
            
        import threading
        threading.Thread(target=_fetch, daemon=True).start()

    def populate_apps(self, packages):
        self.all_packages_cache = packages
        self.filter_apps()

    def filter_apps(self):
        if not hasattr(self, 'all_packages_cache'): return
        
        search_term = self.app_search_var.get().lower()
        
        for widget in self.app_list_frame.winfo_children():
            widget.destroy()
            
        count = 0
        for pkg in self.all_packages_cache:
            if search_term and search_term not in pkg.lower():
                continue
                
            row = ctk.CTkFrame(self.app_list_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=pkg, font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
            
            # Action Buttons
            btn_frame = ctk.CTkFrame(row, fg_color="transparent")
            btn_frame.pack(side="right")
            
            ctk.CTkButton(btn_frame, text="UNINSTALL", width=80, height=24, 
                          fg_color=styles.ERROR_COLOR, hover_color="#D32F2F",
                          font=ctk.CTkFont(size=10, weight="bold"),
                          command=lambda p=pkg: self.adb_manager.uninstall_package(p)).pack(side="left", padx=5)
            
            count += 1
            if count > 100: # Limit display for performance
                ctk.CTkLabel(self.app_list_frame, text=f"... and {len(self.all_packages_cache) - 100} more apps. Use search to find specific ones.", 
                             text_color="gray").pack(pady=10)
                break
        
        if count == 0:
            ctk.CTkLabel(self.app_list_frame, text="No apps found or device disconnected.", text_color="gray").pack(pady=20)

    def select_and_install_apk(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select APK File",
            filetypes=[("APK Files", "*.apk")]
        )
        
        if file_path:
            self.adb_manager.install_custom_apk(file_path)
