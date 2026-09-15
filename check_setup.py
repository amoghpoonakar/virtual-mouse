#!/usr/bin/env python3
"""
Virtual Mouse - Setup Validation Script
Checks all dependencies and system requirements before running
"""

import sys
import platform

print("=" * 60)
print("Virtual Mouse - Setup Validation")
print("=" * 60)
print()

# Python Version Check
print("📍 Python Information:")
print(f"  Version: {sys.version}")
print(f"  Platform: {platform.platform()}")
py_version = sys.version_info
if py_version.major < 3 or (py_version.major == 3 and py_version.minor < 6):
    print("  ⚠️  Warning: Python 3.6+ recommended")
else:
    print("  ✅ Python version compatible")
print()

# Module Checks
modules_to_check = {
    'cv2': ('OpenCV', '4.5.0'),
    'numpy': ('NumPy', '1.19.0'),
    'mediapipe': ('MediaPipe', '0.8.0'),
    'pyautogui': ('PyAutoGUI', '0.9.50'),
}

print("📦 Module Versions:")
all_modules_ok = True

for module_name, (display_name, min_version) in modules_to_check.items():
    try:
        module = __import__(module_name)
        version = getattr(module, '__version__', 'Unknown')
        print(f"  ✅ {display_name}: {version}")
    except ImportError:
        print(f"  ❌ {display_name}: NOT INSTALLED")
        all_modules_ok = False
    except Exception as e:
        print(f"  ⚠️  {display_name}: Error checking - {e}")

print()

# Camera Check
print("📹 Camera Check:")
try:
    import cv2
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("  ✅ Camera accessible")
        cap.release()
    else:
        print("  ❌ Camera NOT accessible")
        print("     - Check if camera is connected")
        print("     - Check camera permissions")
        all_modules_ok = False
except Exception as e:
    print(f"  ⚠️  Could not check camera: {e}")

print()

# Screen Detection
print("🖥️  Screen Information:")
try:
    import pyautogui
    wScr, hScr = pyautogui.size()
    print(f"  ✅ Screen size: {wScr}x{hScr}")
except Exception as e:
    print(f"  ⚠️  Could not detect screen: {e}")
    print("     Using default fallback: 1920x1080")

print()

# Final Status
print("=" * 60)
if all_modules_ok:
    print("✅ All checks passed! You're ready to run:")
    print()
    print("   python virtual_mouse_enhanced.py")
    print()
else:
    print("❌ Some issues found. Please install missing modules:")
    print()
    print("   pip install -r requirements.txt")
    print()

print("=" * 60)

# Provide helpful commands
print()
print("💡 Helpful Commands:")
print()
print("  Install dependencies:")
print("    pip install -r requirements.txt")
print()
print("  Update all modules:")
print("    pip install --upgrade -r requirements.txt")
print()
print("  Run virtual mouse:")
print("    python virtual_mouse_enhanced.py")
print()
print("  Read full guide:")
print("    cat SETUP_GUIDE.md")
print()

# Return exit code based on checks
sys.exit(0 if all_modules_ok else 1)
