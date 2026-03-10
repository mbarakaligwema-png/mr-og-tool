import os
import subprocess
import shutil

def build_mdm_apk():
    print("--- MR OG MDM BUILDER ---")
    base_dir = r"c:\Users\mbara\Documents\MR_OG_TOOL"
    project_dir = os.path.join(base_dir, "assets", "mrog_dpc_project")
    
    # Use its own local gradle wrapper
    gradle_cmd = os.path.join(project_dir, "gradlew.bat")
    
    if not os.path.exists(gradle_cmd):
         print("Error: Gradle wrapper not found!")
         return

    print("Targeting: MR OG MDM PRO (Gold Logo)...")
    
    # Set JAVA_HOME to Android Studio's stable JBR (Java 21)
    # This avoids the "Unsupported class file major version 69" error from Java 25
    os.environ["JAVA_HOME"] = r"C:\Program Files\Android\Android Studio\jbr"
    
    # Set ANDROID_HOME
    sdk_path = os.path.join(os.environ["LOCALAPPDATA"], "Android", "Sdk")
    os.environ["ANDROID_HOME"] = sdk_path
    
    try:
        # Run build command
        # We use the gradlew from the other project but point to this project
        subprocess.run([gradle_cmd, "assembleDebug"], cwd=project_dir, check=True)
        
        # Locate generated APK
        generated_apk = os.path.join(project_dir, "app", "build", "outputs", "apk", "debug", "app-debug.apk")
        destination = os.path.join(base_dir, "assets", "mrog_mdm_pro.apk")
        
        if os.path.exists(generated_apk):
            if os.path.exists(destination): os.remove(destination)
            shutil.copy(generated_apk, destination)
            print(f"\nSUCCESS! APK generated: {destination}")
            return True
        else:
            print("Error: APK was not found after build.")
    except Exception as e:
        print(f"Build Failed: {e}")
    return False

if __name__ == "__main__":
    build_mdm_apk()
