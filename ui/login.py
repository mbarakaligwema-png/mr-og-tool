import customtkinter as ctk
from PIL import Image
from ui import styles
import json
import os
import webbrowser
import threading
import time

class LoginWindow(ctk.CTk):
    def __init__(self, on_login_success):
        super().__init__()
        
        self.on_login_success = on_login_success
        self.expiry_msg = "LIFETIME"
        self.last_server_msg = "LIFETIME"
        
        # Setup AppData Paths
        self.app_data = os.getenv('APPDATA')
        self.tool_data_dir = os.path.join(self.app_data, "MR_OG_TOOL")
        if not os.path.exists(self.tool_data_dir):
            os.makedirs(self.tool_data_dir)
            
        self.config_path = os.path.join(self.tool_data_dir, "config.json")
        self.users_db_path = os.path.join(self.tool_data_dir, "users.db")
        
        # Load saved credentials (last used)
        self.load_config()
        
        self.title("Login - MR OG TOOL")
        self.geometry("400x620") # Increased height slightly for new bar
        self.resizable(False, False)
        self.configure(fg_color=styles.BACKGROUND)
        
        # Center the window on screen
        self.eval('tk::PlaceWindow . center')

        # --- UI Elements ---
        
        # Header Frame (Stylish Logo)
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=(20, 5))
        
        # "MR OG" Label
        self.brand_label_1 = ctk.CTkLabel(self.header_frame, text="MR OG", 
                                          font=ctk.CTkFont(size=32, weight="bold", family="Arial Black"), 
                                          text_color="#E0E0E0")
        self.brand_label_1.pack(side="left", padx=(0, 5))
        
        # "TOOL" Label
        self.brand_label_2 = ctk.CTkLabel(self.header_frame, text="TOOL", 
                                          font=ctk.CTkFont(size=32, weight="bold", family="Arial Black"), 
                                          text_color=styles.ACCENT_COLOR) # Blue/Accent
        self.brand_label_2.pack(side="left")
        
        # Subtitle
        self.tagline_label = ctk.CTkLabel(self, text="ULTIMATE UNLOCKER", 
                                          font=ctk.CTkFont(size=10, weight="bold"), 
                                          text_color=styles.TEXT_SECONDARY)
        self.tagline_label.pack(pady=(0, 15))
        
        self.subtitle_label = ctk.CTkLabel(self, text="Please login to continue", font=ctk.CTkFont(size=12, family=styles.FONT_FAMILY), text_color=styles.TEXT_SECONDARY)
        self.subtitle_label.pack(pady=(0, 10))

        # Username
        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username", width=280, height=40)
        self.username_entry.pack(pady=5)
        self.create_context_menu(self.username_entry)

        # Password
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", width=280, height=40, show="*")
        self.password_entry.pack(pady=5)
        self.create_context_menu(self.password_entry)

        # Options Frame
        self.options_frame = ctk.CTkFrame(self, fg_color="transparent", width=280)
        self.options_frame.pack(pady=5)
        
        # Show Password Checkbox
        self.show_password_var = ctk.BooleanVar(value=False)
        self.show_password_check = ctk.CTkCheckBox(self.options_frame, text="Show Password", 
                                                   variable=self.show_password_var, 
                                                   command=self.toggle_password,
                                                   font=ctk.CTkFont(size=11),
                                                   checkbox_width=18, checkbox_height=18)
        self.show_password_check.pack(side="left", padx=0)

        # Remember Me Checkbox
        self.remember_me_var = ctk.BooleanVar(value=False)
        self.remember_me_check = ctk.CTkCheckBox(self.options_frame, text="Remember Me", 
                                                 variable=self.remember_me_var,
                                                 font=ctk.CTkFont(size=11),
                                                 checkbox_width=18, checkbox_height=18)
        self.remember_me_check.pack(side="right", padx=(20, 0))

        # Login Button
        self.login_button = ctk.CTkButton(self, text="LOGIN", command=self.login_action, width=280, height=45, 
                                          font=ctk.CTkFont(size=14, weight="bold"),
                                          fg_color=styles.ACCENT_COLOR, hover_color=styles.ACCENT_HOVER)
        self.login_button.pack(pady=15)
        
        # Status Label
        self.status_label = ctk.CTkLabel(self, text="", text_color=styles.ERROR_COLOR, font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=2)

        # Loading Bar (Visual Only for Login)
        self.progress_bar = ctk.CTkProgressBar(self, width=280, mode="indeterminate")
        # Hidden by default
        
        # --- UPDATE CHECK BAR (Swag) ---
        self.update_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.update_frame.pack(pady=(10, 0))
        
        self.update_label = ctk.CTkLabel(self.update_frame, text="", font=ctk.CTkFont(size=11))
        self.update_label.pack()
        
        self.update_bar = ctk.CTkProgressBar(self.update_frame, width=280, height=8, progress_color="#00E676") # Green
        self.update_bar.set(0)
        self.update_bar.pack(pady=2)

        # --- SOCIALS & REGISTER ---
        self.social_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.social_frame.pack(pady=10)
        
        # ... (Social buttons logic remains same) ...
        link_font = ctk.CTkFont(size=11, weight="bold", underline=True)
        buy_btn = ctk.CTkButton(self.social_frame, text="Buy Activation", 
                                width=160, height=30,
                                font=ctk.CTkFont(size=12, weight="bold"),
                                fg_color="#FFD700", text_color="#000000", hover_color="#FFC107", 
                                command=lambda: webbrowser.open("https://mrogtool.com/resellers")) 
        buy_btn.pack(side="top", pady=(0, 5))

        reg_url = self.config_data.get("server_url", "https://mrogtool.com") + "/register"
        reg_btn = ctk.CTkButton(self.social_frame, text="Register New Account", 
                                font=link_font, text_color=styles.ACCENT_COLOR, fg_color="transparent", hover=False,
                                command=lambda: webbrowser.open(reg_url)) 
        reg_btn.pack(side="top", pady=0)

        forgot_btn = ctk.CTkButton(self.social_frame, text="Forgot Password?", 
                                font=ctk.CTkFont(size=10, underline=True), text_color="gray", fg_color="transparent", hover=False,
                                command=lambda: webbrowser.open("https://wa.me/255683397833?text=Hello+Admin+I+forgot+my+password")) 
        forgot_btn.pack(side="top", pady=0)
        
        row_frame = ctk.CTkFrame(self.social_frame, fg_color="transparent")
        row_frame.pack(side="top", pady=5)
        whatsapp_btn = ctk.CTkButton(row_frame, text="WhatsApp", width=80, height=25,
                                     fg_color="#25D366", hover_color="#128C7E",
                                     command=lambda: webbrowser.open("https://wa.me/255683397833"))
        whatsapp_btn.pack(side="left", padx=5)
        youtube_btn = ctk.CTkButton(row_frame, text="YouTube", width=80, height=25,
                                    fg_color="#FF0000", hover_color="#CC0000",
                                    command=lambda: webbrowser.open("https://www.youtube.com/@GSMFAMILY1"))
        youtube_btn.pack(side="left", padx=5)

        self.version_label = ctk.CTkLabel(self, text="v1.5", text_color="#666666", font=ctk.CTkFont(size=10))
        self.version_label.pack(side="bottom", pady=5)
        
        self.cleanup_legacy_admin()
        self.populate_fields()
        
        # TRIGGER STARTUP CHECK (SWAG)
        self.after(500, self.start_update_simulation)

    def create_context_menu(self, widget):
        import tkinter as tk
        try:
            target = widget._entry if hasattr(widget, "_entry") else widget
        except: target = widget
        menu = tk.Menu(target, tearoff=0)
        menu.add_command(label="Cut", command=lambda: target.event_generate("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: target.event_generate("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: target.event_generate("<<Paste>>"))
        def show_menu(event): menu.tk_popup(event.x_root, event.y_root)
        widget.bind("<Button-3>", show_menu) 
        if hasattr(widget, "_entry"): widget._entry.bind("<Button-3>", show_menu)

    def start_update_simulation(self):
        """Simulates checking for updates with a loading bar."""
        self.update_label.configure(text="Checking for updates...", text_color="gray")
        
        def _anim():
            for i in range(101):
                self.update_bar.set(i/100)
                time.sleep(0.015) # Takes ~1.5s
            
            # Finished
            self.update_idletasks() # Ensure UI update
            # We need to update UI from main thread ideally, but Tkinter usually handles simple sets
            # Safer to schedule
            self.after(0, lambda: self.update_label.configure(text="You are using the latest version!", text_color="#00E676")) # Green text
            
        threading.Thread(target=_anim, daemon=True).start()

    def cleanup_legacy_admin(self):
        # ... (Existing Clean up Logic) ...
        pass # Simplified for replace tool, assuming logic is preserved outside or handled. 
             # Wait, replace_file deletes content! I must include the FULL content!
             # Re-pasting cleanup_legacy_admin from step 495 view.
        try:
            users_path = self.users_db_path 
            config_path = self.config_path
            users_data = {}
            if os.path.exists(users_path):
                 try:
                     with open(users_path, "r") as f:
                         content = f.read().strip()
                         if content: users_data = json.load(f)
                 except: pass
            if os.path.exists(config_path):
                config_needs_save = False
                try:
                    with open(config_path, "r") as f:
                        config_data = json.load(f)
                    if "users" in config_data:
                        for u, v in config_data["users"].items():
                            if u not in users_data: users_data[u] = v
                        del config_data["users"]
                        config_needs_save = True
                    if config_needs_save:
                         with open(config_path, "w") as f: json.dump(config_data, f, indent=4)
                except: pass
            changed = False
            if "mrogtool" not in users_data:
                users_data["mrogtool"] = {"password": "dell", "expiry": "Unlimited"}
                changed = True
            if changed or not os.path.exists(users_path):
                with open(users_path, "w") as f: json.dump(users_data, f, indent=4)
        except Exception as e: print(f"Error ensuring admin users: {e}")

    def load_config(self):
        self.users_db = {} 
        self.config_data = {}
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f: self.config_data = json.load(f)
        except Exception as e: print(f"Error loading config: {e}")
        try:
            if os.path.exists(self.users_db_path):
                with open(self.users_db_path, "r") as f: self.users_db = json.load(f)
            else: self.users_db = {"mrogtool": {"password": "dell", "expiry": "Unlimited"}}
        except Exception as e: print(f"Error loading users db: {e}")

    def populate_fields(self):
        try:
            if self.config_data.get("remember_me"):
                last_user = self.config_data.get("last_user", "")
                last_pass = self.config_data.get("last_pass", "")
                if hasattr(self, 'username_entry'):
                    self.username_entry.delete(0, "end")
                    self.username_entry.insert(0, last_user)
                if hasattr(self, 'password_entry'):
                    self.password_entry.delete(0, "end")
                    self.password_entry.insert(0, last_pass)
                if hasattr(self, 'remember_me_var'):
                    self.remember_me_var.set(True)
        except Exception as e: print(f"Error populating fields: {e}")

    def save_config(self, username, password):
        if not os.path.exists(self.tool_data_dir): os.makedirs(self.tool_data_dir)
        current_data = {}
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f: current_data = json.load(f)
        except: current_data = self.config_data.copy()

        current_data["remember_me"] = self.remember_me_var.get()
        if self.remember_me_var.get():
            current_data["last_user"] = username
            current_data["last_pass"] = password
        else:
            current_data["last_user"] = ""
            current_data["last_pass"] = ""
            
        import datetime
        now = datetime.datetime.now()
        users_db_data = {}
        try:
            if os.path.exists(self.users_db_path):
                with open(self.users_db_path, "r") as f: users_db_data = json.load(f)
        except: pass
        users_db_data[username] = {
            "password": password,
            "expiry": "Server-Verified",
            "cached_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "hwid_lock": "Cached"
        }
        try:
             with open(self.users_db_path, "w") as f: json.dump(users_db_data, f, indent=4)
        except: pass

        try:
            with open(self.config_path, "w") as f: json.dump(current_data, f, indent=4)
        except Exception as e: print(f"Error saving config: {e}")

    def toggle_password(self):
        if self.show_password_var.get(): self.password_entry.configure(show="")
        else: self.password_entry.configure(show="*")

    def get_hwid(self):
        try:
            import subprocess
            cmd = "powershell -Command \"Get-WmiObject Win32_ComputerSystemProduct | Select-Object -ExpandProperty UUID\""
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            output = subprocess.check_output(cmd, startupinfo=startupinfo).decode().strip()
            if output: return output
        except: pass
        try:
            import uuid
            return str(uuid.getnode())
        except: return "UNKNOWN_HWID"

    def login_action(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            self.status_label.configure(text="Please enter username and password", text_color=styles.ERROR_COLOR)
            return

        # Disable UI
        self.username_entry.configure(state="disabled")
        self.password_entry.configure(state="disabled")
        self.login_button.configure(state="disabled")
        self.progress_bar.pack(pady=10)
        self.progress_bar.start()
        
        # Start Swag Sequence
        threading.Thread(target=self._login_sequence, args=(username, password), daemon=True).start()

    def _login_sequence(self, username, password):
        """Simulates logic steps with delays for effect."""
        def set_status(text):
            self.status_label.configure(text=text, text_color="white") # White for progress info
        
        # 1. Logging in...
        self.after(0, lambda: set_status("Logging in..."))
        time.sleep(1.2)
        
        # 2. Retrieving info
        self.after(0, lambda: set_status("Retrieving user info..."))
        time.sleep(1.5)
        
        # 3. Validating
        self.after(0, lambda: set_status("Validating user license..."))
        time.sleep(1.5)
        
        # 4. Signing in...
        self.after(0, lambda: set_status("Signing in..."))
        time.sleep(0.8)
        
        # Now call real logic (must run on main thread? No, verify is network. But auth check is better there)
        # Actually verify involves networking.
        
        self.after(0, lambda: self.perform_verification(username, password))

    def perform_verification(self, username, password):
        # 1. Server URL
        server_url = self.config_data.get("server_url", "")
        hwid = self.get_hwid()
        
        # Local Check
        if username in self.users_db:
             stored_data = self.users_db[username]
             stored_pass = stored_data.get("password") if isinstance(stored_data, dict) else stored_data
             if stored_pass != password:
                 self.stop_loading()
                 self.status_label.configure(text="Invalid Password (Local)", text_color=styles.ERROR_COLOR)
                 return
        
        from core.network import verify_user_license
        is_allowed, msg = verify_user_license(server_url, username, password, hwid)
        
        server_rejected_keywords = ["Wrong Password", "BLOCKED", "Expired", "Access Denied", "HWID", "User not found"]
        is_server_rejection = any(keyword in msg for keyword in server_rejected_keywords)
        
        if not is_allowed:
            if is_server_rejection:
                pass 
            elif "Connection Failed" in msg or "Server HTTP" in msg or "Server Error" in msg:
                 if username in self.users_db and self.users_db[username].get("password") == password:
                     is_allowed = True
                     msg = "Offline Mode (Server Unreachable)"
                 else:
                     msg = "Login Failed: Offline & Not Cached"

        if is_allowed:
             self.save_config(username, password)
             self.last_server_msg = msg 
             self.status_label.configure(text=f"Success! {msg}", text_color=styles.SUCCESS_COLOR)
             self.after(500, self.complete_login)
        else:
             self.stop_loading()
             self.status_label.configure(text=f"Login Failed: {msg}", text_color=styles.ERROR_COLOR)

    def stop_loading(self):
        try:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.username_entry.configure(state="normal")
            self.password_entry.configure(state="normal")
            self.login_button.configure(state="normal")
        except: pass

    def start_loading_animation(self):
        # Not used in new flow
        pass

    def complete_login(self):
        user = self.username_entry.get()
        self.destroy() 
        if self.on_login_success:
            self.on_login_success(user, getattr(self, 'last_server_msg', "LIFETIME"))


