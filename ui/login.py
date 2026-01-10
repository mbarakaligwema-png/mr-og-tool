import customtkinter as ctk
from PIL import Image
from ui import styles
import json
import os
import webbrowser

class LoginWindow(ctk.CTk):
    def __init__(self, on_login_success):
        super().__init__()
        
        self.on_login_success = on_login_success
        
        # Load saved credentials (last used) - MOVED TO TOP
        self.load_config()
        
        self.title("Login - MR OG TOOL")
        self.title("Login - MR OG TOOL")
        self.geometry("400x580") # Reduced height
        self.resizable(False, False)
        self.configure(fg_color=styles.BACKGROUND)
        
        # Center the window on screen
        self.eval('tk::PlaceWindow . center')

        # --- UI Elements ---
        
        # Header Frame (Stylish Logo)
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=(20, 5)) # Reduced top padding
        
        # "MR OG" Label - White/Grey
        self.brand_label_1 = ctk.CTkLabel(self.header_frame, text="MR OG", 
                                          font=ctk.CTkFont(size=32, weight="bold", family="Arial Black"), 
                                          text_color="#E0E0E0")
        self.brand_label_1.pack(side="left", padx=(0, 5))
        
        # "TOOL" Label - Accent Color
        self.brand_label_2 = ctk.CTkLabel(self.header_frame, text="TOOL", 
                                          font=ctk.CTkFont(size=32, weight="bold", family="Arial Black"), 
                                          text_color=styles.ACCENT_COLOR) # Blue/Accent
        self.brand_label_2.pack(side="left")
        
        # Subtitle "ULTIMATE UNLOCKER"
        self.tagline_label = ctk.CTkLabel(self, text="ULTIMATE UNLOCKER", 
                                          font=ctk.CTkFont(size=10, weight="bold"), 
                                          text_color=styles.TEXT_SECONDARY)
        self.tagline_label.pack(pady=(0, 15)) # Reduced bottom padding
        
        self.subtitle_label = ctk.CTkLabel(self, text="Please login to continue", font=ctk.CTkFont(size=12, family=styles.FONT_FAMILY), text_color=styles.TEXT_SECONDARY)
        self.subtitle_label.pack(pady=(0, 10)) # Reduced bottom padding

        # Username
        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username", width=280, height=40)
        self.username_entry.pack(pady=5) # Reduced

        # Password
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", width=280, height=40, show="*")
        self.password_entry.pack(pady=5) # Reduced

        # Options Frame (Show Pass & Remember Me)
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

        # Loading Bar (Hidden by default)
        self.progress_bar = ctk.CTkProgressBar(self, width=280, mode="determinate")
        self.progress_bar.set(0)
        
        # --- SOCIALS & REGISTER ---
        self.social_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.social_frame.pack(pady=5) # Reduced
        
        link_font = ctk.CTkFont(size=11, weight="bold", underline=True)
        
        # Buy Activation Button (Golden/Premium Look)
        buy_btn = ctk.CTkButton(self.social_frame, text="Buy Activation", 
                                width=160, height=30,
                                font=ctk.CTkFont(size=12, weight="bold"),
                                fg_color="#FFD700", text_color="#000000", hover_color="#FFC107", # Gold background, black text
                                command=lambda: webbrowser.open("http://127.0.0.1:8000/sellers")) 
        buy_btn.pack(side="top", pady=(0, 5)) # Reduced

        # Register Link
        # Dynamic URL from config
        reg_url = self.config_data.get("server_url", "https://mr-og-tool.onrender.com") + "/register"
        reg_btn = ctk.CTkButton(self.social_frame, text="Register New Account", 
                                font=link_font, text_color=styles.ACCENT_COLOR, fg_color="transparent", hover=False,
                                command=lambda: webbrowser.open(reg_url)) 
        reg_btn.pack(side="top", pady=0)
        
        # Icons/Buttons Row
        row_frame = ctk.CTkFrame(self.social_frame, fg_color="transparent")
        row_frame.pack(side="top", pady=5)
        
        # WhatsApp
        whatsapp_btn = ctk.CTkButton(row_frame, text="WhatsApp", width=80, height=25,
                                     fg_color="#25D366", hover_color="#128C7E",
                                     command=lambda: webbrowser.open("https://wa.me/255683397833"))
        whatsapp_btn.pack(side="left", padx=5)
        
        # YouTube
        youtube_btn = ctk.CTkButton(row_frame, text="YouTube", width=80, height=25,
                                    fg_color="#FF0000", hover_color="#CC0000",
                                    command=lambda: webbrowser.open("https://www.youtube.com/@GSMFAMILY1"))
        youtube_btn.pack(side="left", padx=5)

        # Load saved credentials (last used)
        self.load_config()

    def load_config(self):
        self.users_db = {"admin": "admin"} # Default
        self.config_data = {}
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    self.config_data = json.load(f)
                    # Load users
                    if "users" in self.config_data:
                        self.users_db.update(self.config_data["users"])
                    
                    # Remember me
                    if self.config_data.get("remember_me"):
                        self.username_entry.insert(0, self.config_data.get("last_user", ""))
                        self.password_entry.insert(0, self.config_data.get("last_pass", ""))
                        self.remember_me_var.set(True)
        except Exception as e:
            print(f"Error loading config: {e}")

    def save_config(self, username, password):
        data = self.config_data
        data["remember_me"] = self.remember_me_var.get()
        if self.remember_me_var.get():
            data["last_user"] = username
            data["last_pass"] = password
        else:
            data["last_user"] = ""
            data["last_pass"] = ""
            
        # Ensure users db is saved
        data["users"] = self.users_db
        
        try:
            with open("config.json", "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def toggle_password(self):
        if self.show_password_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")

    def get_hwid(self):
        try:
            # Try getting UUID via PowerShell (more reliable on modern Windows)
            import subprocess
            cmd = "powershell -Command \"Get-WmiObject Win32_ComputerSystemProduct | Select-Object -ExpandProperty UUID\""
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            output = subprocess.check_output(cmd, startupinfo=startupinfo).decode().strip()
            if output:
                return output
        except Exception:
            pass

        try:
            # Fallback to UUID module (Mac address based)
            import uuid
            return str(uuid.getnode())
        except Exception:
            return "UNKNOWN_HWID"

    def login_action(self):
        # NOTE: Internet Connection was already checked at Startup (main.py).
        # However, for License Verification, we DO need to hit the server now.
        
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # Basic validation
        if not username or not password:
            self.status_label.configure(text="Please enter username and password", text_color=styles.ERROR_COLOR)
            return

        self.start_loading_animation()
        # Force UI update so loader appears before blocking call
        self.update_idletasks()
        
        # 1. Get Server URL
        server_url = self.config_data.get("server_url", "")
        
        # 2. Get HWID
        hwid = self.get_hwid()
        
        # 3. Call Server API
        from core.network import verify_user_license
        
        # Local Auth Check (Password)
        if username in self.users_db:
             stored_data = self.users_db[username]
             stored_pass = stored_data.get("password") if isinstance(stored_data, dict) else stored_data
             
             if stored_pass != password:
                 self.stop_loading()
                 self.status_label.configure(text="Invalid Password (Local)", text_color=styles.ERROR_COLOR)
                 return
        
        # Server verification
        # In offline mode or if server error, we might want to fail gracefully or allow if local is OK?
        # User prompt implies "cannot connect to server" is the issue.
        # If verify_user_license returns False because of connection error, user is blocked.
        # Let's Modify logic: If connection failed, but local auth is OK, maybe allow with warning?
        # But verify_user_license returns (False, error_msg).
        # Check if error message is connection related.
        
        is_allowed, msg = verify_user_license(server_url, username, hwid)
        
        # BYPASS FOR OFFLINE DEVELOPMENT if server is unreachable
        if not is_allowed and ("Connection Failed" in msg or "Server HTTP" in msg):
             # For now, allow offline login if local password was correct
             is_allowed = True
             msg = "Offline Mode (Server Unreachable)"

        if is_allowed:
             self.save_config(username, password)
             self.last_server_msg = msg # Store for passing to main app
             self.status_label.configure(text=f"Success! {msg}", text_color=styles.SUCCESS_COLOR)
             # Give time for success msg to show
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
        self.progress_bar.pack(pady=10)
        self.progress_bar.start()

    # Removed recursive step_loading to prevent 'invalid command name' error 
    # since we are doing blocking calls mainly.
    # If we needed async animation, we'd use threading.


    def complete_login(self):
        user = self.username_entry.get()
        self.destroy() # Close login window
        # msg is stored in self.last_msg or similar? No, let's store it in instance
        self.on_login_success(user, self.last_server_msg) # Callback to start main app with username


