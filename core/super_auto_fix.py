import os
import time

class SuperAutoFixManager:
    def __init__(self, append_log_callback):
        self.append_log = append_log_callback

    def run_super_auto_progress(self, progress_vars, percent, speed_mbs, eta_sec):
        if progress_vars:
            bar = progress_vars.get('bar')
            label = progress_vars.get('label')
            if bar:
                bar.set(percent / 100)
            if label:
                label.configure(text=f"Progress: {int(percent)}% - Speed: {speed_mbs:.2f} MB/s - ETA: {eta_sec}s")

    def run_fix(self, file_path, manual_start="", manual_end="", progress_vars=None):
        import threading
        def _task():
            self.append_log(f"\n[BLUE]=========================================")
            self.append_log(f"[HEADER] [PREMIUM] MR OG SUPER FIX ENGINE INITIALIZED 🔥")
            self.append_log(f"[INFO] Analyzing Target File: {os.path.basename(file_path)}...")
            
            try:
                if not os.path.exists(file_path):
                    self.append_log("[ERROR] File does not exist! Please check the path.")
                    if progress_vars and progress_vars.get('app'): progress_vars['app'].after(0, lambda: progress_vars['label'].configure(text="File not found!", text_color="red"))
                    return
                
                file_size = os.path.getsize(file_path)
                
                start_offset = -1
                end_offset = -1
                
                if manual_start and manual_end:
                    self.append_log(f"[INFO] OVERRIDE: Using MANUAL Offsets provided by User...")
                    try:
                        # Clean hex string
                        ms = manual_start.replace("0X", "").replace("0x", "")
                        me = manual_end.replace("0X", "").replace("0x", "")
                        start_offset = int(ms, 16)
                        end_offset = int(me, 16)
                    except ValueError:
                        self.append_log("[ERROR] Invalid Hex offsets provided! Please ensure they are valid hex strings (e.g. 1386F7F8A)")
                        if progress_vars and progress_vars.get('app'): progress_vars['app'].after(0, lambda: progress_vars['label'].configure(text="Invalid Hex input!", text_color="red"))
                        return
                    
                    self.append_log(f"[SUCCESS] Manual Target Zero-Fill Start: {hex(start_offset).upper()} 🎯")
                    self.append_log(f"[SUCCESS] Manual End boundary verified at offset {hex(end_offset).upper()} 🛡️")
                
                else:
                    self.append_log(f"[INFO] Initiating Dynamic Track & Trace Protocol...")
                    time.sleep(1) # Visual weight
                    
                    # Helper function for chunk-based searching
                    def find_in_file(f, search_term_lower, start_pos, label_msg):
                        f.seek(start_pos)
                        chunk_size = 1024 * 1024 * 50 # 50MB chunks for speed
                        overlap = len(search_term_lower)
                        search_start = time.time()
                        current_pos = start_pos
                        
                        while current_pos < file_size:
                            f.seek(current_pos)
                            chunk = f.read(chunk_size + overlap)
                            if not chunk:
                                break
                            
                            # Soft UI update
                            if progress_vars and (time.time() - search_start) > 0.5:
                                app = progress_vars.get('app')
                                if app:
                                    ratio = min(current_pos / file_size, 0.99)
                                    app.after(0, lambda r=ratio, m=label_msg: progress_vars.get('label').configure(text=f"{m} {int(r*100)}%", text_color="gray"))
                                    app.after(0, lambda r=ratio: progress_vars.get('bar').set(r))
                                search_start = time.time()
                                
                            # Use lower for case-insensitive search
                            idx = chunk.lower().find(search_term_lower)
                            if idx != -1:
                                return current_pos + idx
                                
                            current_pos += chunk_size
                        return -1

                    with open(file_path, "rb") as f:
                        # 1. Track SECURITYCOM.APK
                        self.append_log("[INFO] Loading MR OG Deep Scan Protocol for SECURITYCOM module 🕵️‍♂️...")
                        sec_term = b"securitycom.apk"
                        sec_offset = find_in_file(f, sec_term, 0, "Scanning for SECURITYCOM...")
                        
                        if sec_offset == -1:
                            self.append_log("[ERROR] Security module not found! Is this a valid MDM/Scorpio locked device?")
                            if progress_vars and progress_vars.get('app'): progress_vars['app'].after(0, lambda: progress_vars['label'].configure(text="Module not found!", text_color="red"))
                            return
                        
                        self.append_log(f"[SUCCESS] BINGO! SecurityCom Module captured at Sector {sec_offset // 512} (Offset {hex(sec_offset)}) ✅")
                        
                        # 2. Track nearest classes.dexdex
                        self.append_log("[INFO] Initializing Scorpio Hunter... Sniffing for footprint 🐾")
                        dex_term = b"classes.dexdex"
                        dex_offset = find_in_file(f, dex_term, sec_offset, "Tracking classes.dexdex...")
                        
                        if dex_offset == -1:
                            self.append_log("[WARNING] 'classes.dexdex' signature missing. Switching to standard 'classes.dex' footprint...")
                            dex_term = b"classes.dex"
                            dex_offset = find_in_file(f, dex_term, sec_offset, "Tracking classes.dex...")
                            
                            if dex_offset == -1:
                                self.append_log("[ERROR] Critical failure! No dex footprint found after SecurityCom.")
                                if progress_vars and progress_vars.get('app'): progress_vars['app'].after(0, lambda: progress_vars['label'].configure(text="Signature not found!", text_color="red"))
                                return
                        
                        # Align to sector boundaries based on HxD logic
                        start_offset = (dex_offset // 512) * 512
                        self.append_log(f"[SUCCESS] Gotcha! Nearest Scorpio footprint detected at Sector {dex_offset // 512}. Auto-Calculated Target Zero-Fill Start: {hex(start_offset).upper()} 🎯")
                        
                        # 3. Find META-INF/MANIFEST.MFPK for end boundary
                        self.append_log("[INFO] Injecting intelligent block boundaries... Searching for End Sector.")
                        end_term = b"meta-inf/manifest.mfpk"
                        end_offset = find_in_file(f, end_term, start_offset, "Calculating block boundary...")
                        
                        if end_offset == -1:
                            self.append_log("[ERROR] Boundary signature META-INF/MANIFEST.MFPK not found! Cannot safely bypass.")
                            if progress_vars and progress_vars.get('app'): progress_vars['app'].after(0, lambda: progress_vars['label'].configure(text="End Boundary not found!", text_color="red"))
                            return
                            
                        self.append_log(f"[SUCCESS] Perfect Match! End boundary strongly verified at offset {hex(end_offset).upper()} 🛡️")
                        
                # Zero-Fill Action
                fill_size = end_offset - start_offset
                if fill_size <= 0:
                    self.append_log("[ERROR] Critical Error: End offset is before Start offset. Aborting for safety!")
                    return
                    
                self.append_log(f"[YELLOW] >> INITIATING KERNEL-LEVEL BYPASS PROTOCOL ON {fill_size / (1024*1024):.2f} MB OF CLASSIFIED DATA <<")
                self.append_log(f"[INFO] Please wait, Forcing Low-Level sector erase. STRICTLY DO NOT INTERRUPT! ⌛")
                
                try:
                    import stat
                    # 1. Force remove Read-Only attributes if any
                    if not os.access(file_path, os.W_OK):
                        os.chmod(file_path, stat.S_IWRITE)
                        
                    # 2. Use Low-Level OS file descriptor for guaranteed unbuffered direct-to-disk writes
                    fd = os.open(file_path, os.O_RDWR | os.O_BINARY)
                    os.lseek(fd, start_offset, os.SEEK_SET)
                    
                    written = 0
                    zero_chunk = b'\x00' * (1024 * 1024 * 10) # 10MB chunk
                    last_update_time = time.time()
                    bytes_since_last_update = 0
                    
                    while written < fill_size:
                        rem = fill_size - written
                        write_amount = min(rem, len(zero_chunk))
                        
                        # os.write returns the number of bytes actually written
                        bytes_written = os.write(fd, zero_chunk[:write_amount])
                        if bytes_written == 0:
                            raise IOError("Low-level write failed (0 bytes written). Drive may be full or device disconnected.")
                            
                        written += bytes_written
                        bytes_since_last_update += bytes_written
                        
                        # Progress Update Logic
                        current_time = time.time()
                        elapsed = current_time - last_update_time
                        
                        if elapsed >= 0.2 or written == fill_size:
                            speed_bps = bytes_since_last_update / elapsed if elapsed > 0 else 0
                            speed_mbs = speed_bps / (1024 * 1024)
                            percent = (written / fill_size) * 100
                            rem_bytes = fill_size - written
                            eta_sec = int(rem_bytes / speed_bps) if speed_bps > 0 else 0
                            
                            if progress_vars:
                                app = progress_vars.get('app')
                                if app:
                                    app.after(0, lambda p=percent, s=speed_mbs, e=eta_sec: self.run_super_auto_progress(progress_vars, p, s, e))
                            
                            last_update_time = current_time
                            bytes_since_last_update = 0
                            
                    # Force Windows to save changes to hard drive immediately
                    os.fsync(fd)
                    os.close(fd)
                    
                except Exception as ex:
                    self.append_log(f"[ERROR] Kernel-Level Write Failed: {ex}")
                    return
                        
                self.append_log(f"[GREEN] BOOOOM! 💥")
                self.append_log(f"[GREEN] SECURITYCOM BYPASSED AUTOMATICALLY! 🔓")
                self.append_log(f"[INFO] Device is now 100% READY TO FLASH. Enjoy MR OG PREMIUM TOOL!")
                
                if progress_vars:
                     app = progress_vars.get('app')
                     if app:
                         app.after(0, lambda: progress_vars.get('label').configure(text="Patching Complete! 100%", text_color="#00FF00"))
                         app.after(0, lambda: progress_vars.get('bar').set(1.0))

            except Exception as e:
                self.append_log(f"[ERROR] Critical Engine Failure: {e}")
                if progress_vars:
                     app = progress_vars.get('app')
                     if app:
                         app.after(0, lambda: progress_vars.get('label').configure(text=f"Failed: {e}", text_color="red"))
                
            self.append_log(f"[BLUE]=========================================\n")
            
        threading.Thread(target=_task, daemon=True).start()
