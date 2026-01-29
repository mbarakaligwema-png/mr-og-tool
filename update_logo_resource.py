import shutil
import os
import sys

# Source path from user upload
source_path = r"C:/Users/mbara/.gemini/antigravity/brain/3a0af603-9e43-47e6-ba35-bade2680bdf9/uploaded_media_1769674666110.png"
# Destination
dest_path = r"c:\Users\mbara\Documents\MR_OG_TOOL\assets\logo.png"

try:
    if os.path.exists(source_path):
        print(f"Found source image: {source_path}")
        shutil.copy2(source_path, dest_path)
        print(f"Successfully updated logo.png at: {dest_path}")
    else:
        print(f"Error: Source file not found: {source_path}")
        # Validating current directory
        print(f"CWD: {os.getcwd()}")
except Exception as e:
    print(f"Failed to copy logo: {e}")
