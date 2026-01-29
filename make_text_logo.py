from PIL import Image, ImageDraw, ImageFont
import os

def create_mrog_logo():
    # 1. Create Black Background (256x256)
    size = (256, 256)
    img = Image.new('RGBA', size, (0, 0, 0, 255)) # Black
    draw = ImageDraw.Draw(img)
    
    # 2. Add Text "MR OG"
    try:
        # Try to use a system font
        font = ImageFont.truetype("arialbd.ttf", 80)
    except:
        font = ImageFont.load_default()
        
    text = "MR\nOG"
    
    # Calculate text position to center it
    # getbbox returns (left, top, right, bottom)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    x = (size[0] - text_w) // 2
    y = (size[1] - text_h) // 2
    
    # Draw Text (Blue Accent)
    draw.text((x, y), text, font=font, fill="#00BFFF", align="center")
    
    # 3. Save as PNG
    base_dir = r"c:\Users\mbara\Documents\MR_OG_TOOL\assets"
    if not os.path.exists(base_dir): os.makedirs(base_dir)
    
    png_path = os.path.join(base_dir, "logo.png")
    round_path = os.path.join(base_dir, "logo_round.png")
    ico_path = os.path.join(base_dir, "logo.ico")
    
    img.save(png_path)
    img.save(round_path) # Use square for now to ensure visibility
    print(f"Saved PNG: {png_path}")
    
    # 4. Save as ICO (Multi-size)
    img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"Saved ICO: {ico_path}")

if __name__ == "__main__":
    create_mrog_logo()
