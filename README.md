# Virtual Mouse using Hand Tracking

---

## Project Overview

This project implements a virtual mouse system using hand gesture recognition. It uses computer vision and machine learning to track hand movements through a webcam and control the mouse cursor without physical input devices.

The system detects hand landmarks and interprets specific finger gestures to perform actions such as cursor movement and mouse clicking.

---

## Features

- Real-time hand tracking using MediaPipe  
- Cursor movement using index finger  
- Mouse click using index and middle finger gesture  
- Smooth cursor motion with interpolation  
- Frame reduction for better control accuracy  
- FPS display for performance monitoring  

---

## Technology Stack

- Python  
- OpenCV  
- MediaPipe  
- NumPy  
- PyAutoGUI  

---

## How It Works

1. The webcam captures live video input.  
2. MediaPipe detects hand landmarks in real time.  
3. The index finger controls cursor movement.  
4. The distance between index and middle fingers determines click action.  
5. Cursor movement is smoothed using interpolation for better usability.  

---

## Controls

| Gesture | Action |
|--------|--------|
| Index finger up | Move cursor |
| Index + Middle finger up | Click mode |
| Fingers close together | Perform mouse click |
| Q key | Quit application |

---

## Configuration

You can modify the following parameters in the code:

- `wCam`, `hCam` – Camera resolution  
- `frameR` – Active movement area  
- `smoothening` – Cursor smoothness factor  
- `detectionCon` – Detection confidence  
- `trackCon` – Tracking confidence  

---

## Output

- Live webcam feed with hand tracking  
- Cursor controlled via hand gestures  
- Visual indicators for gestures  
- FPS counter display  

---

## Use Cases

- Touchless human-computer interaction  
- Accessibility tools  
- Gesture-based control systems  
- Computer vision learning projects  

---

## Limitations

- Requires good lighting conditions  
- Accuracy depends on camera quality  
- May have slight latency on low-end systems  
- Gesture detection may vary across users  

---

## Future Improvements

- Add right-click and drag functionality  
- Multi-hand support  
- Gesture customization  
- GUI-based controls  
- Performance optimization  

---
