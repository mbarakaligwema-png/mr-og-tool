import os
from PIL import Image

# Path to the uploaded image (The circular logo)
input_image = r"C:\Users\mbara\.gemini\antigravity\brain\4e0e07c0-faf5-4b34-9333-e98b11092d8f\media__1772378494259.png"
res_dir = r"c:\Users\mbara\Documents\MR_OG_TOOL\assets\android_project\app\src\main\res"

sizes = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192
}

try:
    img = Image.open(input_image)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
        
    for folder, size in sizes.items():
        target_path = os.path.join(res_dir, folder)
        if not os.path.exists(target_path):
            os.makedirs(target_path)
        
        # Resize to standard icon size
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        
        # Save both square and round versions
        # Since the logo itself is circular, just saving it works for both
        resized.save(os.path.join(target_path, "ic_launcher.png"))
        resized.save(os.path.join(target_path, "ic_launcher_round.png"))
        
    print("SUCCESS: Icons updated with circular logo.")
except Exception as e:
    print(f"ERROR: {e}")
