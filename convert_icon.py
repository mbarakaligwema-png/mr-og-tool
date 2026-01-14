from PIL import Image, ImageDraw
import os

img_path = r"C:\Users\mbara\Documents\MR_OG_TOOL\assets\logo.png"
ico_path = r"C:\Users\mbara\Documents\MR_OG_TOOL\assets\logo.ico"

if os.path.exists(img_path):
    try:
        img = Image.open(img_path).convert("RGBA")
        
        # Create a square canvas to ensure circle is round
        diff = abs(img.size[0] - img.size[1]) // 2
        # Crop or pad to square if strictly needed, but let's just make a mask for the current size
        # Better: resize to square 256x256 first for standard icon size
        img = img.resize((256, 256), Image.Resampling.LANCZOS)
        
        # Create circular mask
        mask = Image.new('L', (256, 256), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, 256, 256), fill=255)
        
        # Apply mask
        output = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
        output.paste(img, (0, 0), mask=mask)
        
        # Save as PNG (Round)
        png_round_path = r"C:\Users\mbara\Documents\MR_OG_TOOL\assets\logo_round.png"
        output.save(png_round_path, format='PNG')
        print(f"Created Circular PNG: {png_round_path}")

        # Save as ICO
        output.save(ico_path, format='ICO', sizes=[(256, 256)])
        print(f"Created Circular Icon: {ico_path}")
        
    except Exception as e:
        print(f"Error converting icon: {e}")
else:
    print("PNG logo not found!")
