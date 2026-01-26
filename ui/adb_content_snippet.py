
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
            ("Open YouTube", lambda: self.adb_manager.open_browser_mtp("youtube")),
            ("Open Maps", lambda: self.adb_manager.open_browser_mtp("maps"))
        ]
        
        for i, (text, cmd) in enumerate(buttons_data):
             btn = ctk.CTkButton(grid_frame, text=text, height=50, fg_color=styles.CARD_BG, hover_color=styles.ACCENT_COLOR, command=cmd)
             btn.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="ew")

        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        grid_frame.grid_columnconfigure(2, weight=1)
