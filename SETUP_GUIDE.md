# Virtual Mouse - Setup & Troubleshooting Guide

## ✅ Installation

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install opencv-python
pip install mediapipe
pip install numpy
pip install pyautogui
```

### Step 2: Run the Application
```bash
python virtual_mouse_enhanced.py
```

---

## 🎮 How to Use

1. **Move Mouse**: Hold up your **index finger only**
   - You'll see a purple rectangle (active area)
   - Move your index finger to control the cursor

2. **Click**: Hold up both **index and middle fingers** close together
   - When they get close (< 40 pixels), it clicks
   - Green circle shows click position

3. **Quit**: Press **'q'** or **ESC** key

---

## 🔧 Version Compatibility

This enhanced version works with:
- **Python**: 3.6 - 3.12+
- **OpenCV**: 4.5.0+
- **MediaPipe**: 0.8.0+
- **NumPy**: 1.19.0+
- **PyAutoGUI**: 0.9.50+

### What's Different from Original?

1. **Auto-detection of API versions** - Handles MediaPipe API changes
2. **Comprehensive error handling** - Won't crash on common issues
3. **Fallback mechanisms** - If one method fails, tries alternatives
4. **Better bounds checking** - Prevents array index errors
5. **Camera robustness** - Handles camera disconnects gracefully
6. **Screen detection** - Fallback if screen size detection fails

---

## ⚠️ Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'mediapipe'"

**Solution:**
```bash
pip install --upgrade mediapipe
```

If that doesn't work, try:
```bash
pip install mediapipe --no-cache-dir
```

---

### Problem: Camera Won't Open

**Solution:**
1. Check if camera is physically connected
2. Try this to test camera:
   ```python
   import cv2
   cap = cv2.VideoCapture(0)
   print(cap.isOpened())
   ```
3. If it prints `False`, camera is not accessible
4. On Linux, might need: `sudo usermod -a -G video $USER`
5. Try different camera index: Change `cv2.VideoCapture(0)` to `1`, `2`, etc.

---

### Problem: Mouse Not Moving or Erratic Movement

**Solution:**
1. Ensure good lighting - hand detection needs good lighting
2. Adjust `smoothening` value (line ~16 in code):
   - Lower = faster but jerky (try 5)
   - Higher = smoother but laggy (try 10-15)
3. Adjust `frameR` (detection area):
   - Smaller = less area needed (try 50)
   - Larger = more area to move in (try 150)

---

### Problem: Hand Detection Not Working

**Solution:**
1. Adjust detection confidence thresholds:
   ```python
   detector = HandDetector(detectionCon=0.3, trackCon=0.3)  # More lenient
   detector = HandDetector(detectionCon=0.7, trackCon=0.7)  # More strict
   ```
2. Check lighting - detection works best with good lighting
3. Show your entire hand (all 21 landmarks)
4. Try moving closer/farther from camera

---

### Problem: Clicks Not Working

**Solution:**
1. The distance threshold is 40 pixels - if too strict:
   ```python
   if length < 50:  # Change from 40 to 50
   ```
2. Make sure both index and middle fingers are clearly visible
3. Add debounce delay if clicking too fast:
   ```python
   time.sleep(0.3)  # Increase click delay
   ```

---

### Problem: "FailSafeException" or Mouse Goes to Corner

**Solution:**
This is intentional - move your mouse away from the corner. The failsafe is disabled in the enhanced version, but Python/OS might still have it.

---

### Problem: Low FPS / Laggy Performance

**Solution:**
1. Reduce camera resolution:
   ```python
   wCam, hCam = 320, 240  # Instead of 640, 480
   ```
2. Try disabling hand drawing:
   ```python
   img = detector.findHands(img, draw=False)
   ```
3. Close other applications
4. Try different Python version (3.9-3.11 usually fastest)

---

## 📊 Performance Tips

1. **Optimal Settings for Smooth Operation:**
   ```python
   wCam, hCam = 640, 480      # Default is good
   frameR = 100               # Active area
   smoothening = 7            # Smoothness
   ```

2. **For Faster Tracking:**
   ```python
   detector = HandDetector(detectionCon=0.5, trackCon=0.3)
   ```

3. **For Better Accuracy:**
   ```python
   detector = HandDetector(detectionCon=0.7, trackCon=0.7)
   ```

---

## 🐛 Getting Debug Info

Add this at the start of main():
```python
print(f"Python: {sys.version}")
print(f"OpenCV: {cv2.__version__}")
print(f"MediaPipe: {mp.__version__}")  # Might not work in all versions
```

---

## 📝 Common Modifications

### Add Drag Functionality
```python
# In the click mode section:
if fingers[1] == 1 and fingers[2] == 1:
    length, img, lineInfo = detector.findDistance(8, 12, img)
    if length < 40:
        # Drag instead of click
        pyautogui.mouseDown()
        time.sleep(0.1)
        pyautogui.mouseUp()
```

### Add Right-Click
```python
# Use ring finger + pinky for right-click
if len(fingers) > 4 and fingers[3] == 1 and fingers[4] == 1:
    pyautogui.rightClick()
```

### Add Volume Control
```python
# Use hand size for volume
if len(lmList) > 0:
    hand_size = detector.findDistance(0, 9, img, draw=False)[0]
    volume = np.interp(hand_size, [30, 300], [0, 100])
```

---

## ✨ Tips for Best Performance

1. **Lighting**: Good natural or office lighting works best
2. **Contrast**: Wear contrasting colors (dark hand, light background)
3. **Distance**: Keep hand 30-60cm from camera
4. **Angle**: Face camera directly, not at an angle
5. **Steady Movement**: Slow, deliberate movements work better than jerky ones
6. **Full Hand**: Always show all 5 fingers for best detection

---

## 🆘 Still Having Issues?

1. Try running with verbose output:
   ```bash
   python -u virtual_mouse_enhanced.py
   ```

2. Check MediaPipe version:
   ```bash
   pip show mediapipe
   ```

3. Try reinstalling everything fresh:
   ```bash
   pip uninstall -y opencv-python mediapipe numpy pyautogui
   pip install -r requirements.txt
   ```

4. On macOS: You might need to give camera permissions
   - System Preferences → Security & Privacy → Camera

5. On Linux: 
   ```bash
   sudo usermod -a -G video $USER
   # Log out and back in
   ```

---

## 📚 Code Structure

- **HandDetector class**: Handles all hand detection logic
- **findHands()**: Detects hands in frame
- **findPosition()**: Gets exact landmark coordinates
- **fingersUp()**: Detects which fingers are raised
- **findDistance()**: Calculates distance between landmarks
- **main()**: Main application loop with error handling

All methods have error handling and return sensible defaults on failure.

---

**Enjoy your virtual mouse! 🖱️✨**
