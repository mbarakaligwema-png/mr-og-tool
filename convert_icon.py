import os
import shutil

# User provided a ready-made icon named "yenye.ico" in assets
input_ico = r"C:\Users\mbara\Documents\MR_OG_TOOL\assets\yenye.ico"
target_ico = r"C:\Users\mbara\Documents\MR_OG_TOOL\assets\logo.ico"
target_png = r"C:\Users\mbara\Documents\MR_OG_TOOL\assets\logo_round.png"

def use_user_icon():
    if os.path.exists(input_ico):
        try:
            # 1. Replace logo.ico
            shutil.copy(input_ico, target_ico)
            print(f"Updated logo.ico from {input_ico}")
            
            # 2. Try to make a PNG from it if needed, or just let the app use what it has.
            # Usually we need a PNG for the UI Image. 
            # If the user only gave ICO, we can try to extract PNG or just assume they have one.
            # But let's just finish the ICO part first.
            
            # If you want to convert ICO to PNG for the internal UI:
            from PIL import Image
            img = Image.open(input_ico)
            img.save(target_png, format="PNG")
            print(f"Updated logo_round.png from ICO")
            
        except Exception as e:
            print(f"Error copying icon: {e}")
    else:
        print("yenye.ico not found!")

if __name__ == "__main__":
    use_user_icon()
