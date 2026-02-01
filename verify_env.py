
import sys
import os
import shutil

def check_dependencies():
    print("Checking dependencies...")
    try:
        import PyQt6
        print(" [OK] PyQt6")
    except ImportError:
        print(" [FAIL] PyQt6 not installed")

    try:
        import exiftool
        print(" [OK] PyExifTool")
    except ImportError:
        print(" [FAIL] PyExifTool not installed")

    try:
        import cv2
        print(" [OK] opencv-python")
    except ImportError:
        print(" [FAIL] opencv-python not installed")
        
    try:
        import PIL
        print(" [OK] Pillow")
    except ImportError:
        print(" [FAIL] Pillow not installed")

def check_exiftool():
    print("\nChecking ExifTool...")
    path = shutil.which("exiftool")
    if path:
        print(f" [OK] Found in PATH: {path}")
        return True
    
    local_paths = [
        "exiftool.exe",
        "src/core/exiftool.exe",
        "src/libs/exiftool.exe",
        "libs/exiftool.exe"
    ]
    for p in local_paths:
        if os.path.exists(p):
            print(f" [OK] Found local: {os.path.abspath(p)}")
            return True
            
    print(" [WARNING] ExifTool not found!")
    print("   Please download from https://exiftool.org/ and place 'exiftool.exe' in this project folder.")
    return False

if __name__ == "__main__":
    check_dependencies()
    check_exiftool()
    print("\nDone.")
