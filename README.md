# Virtual Mouse

A real-time computer vision-based virtual mouse that allows users to control the cursor and perform mouse clicks using hand gestures captured through a webcam.

The project uses OpenCV for video capture and image processing, MediaPipe's Hand Landmarker for real-time hand tracking, and PyAutoGUI for controlling the system mouse.

## Features

* Real-time hand tracking using a webcam
* Index finger-based cursor movement
* Index and middle finger gesture for mouse clicking
* Smooth cursor movement with configurable smoothing
* Adjustable active tracking area
* Automatic hand landmark visualization
* Real-time FPS display
* Automatic download of the MediaPipe Hand Landmarker model
* Compatible with modern MediaPipe Tasks API
* Supports Python 3.13
* Multiple exit methods:

  * `Q`
  * `ESC`
  * Window close button (`X`)

## How It Works

The application captures frames from the webcam and processes them using MediaPipe's Hand Landmarker.

The detected hand landmarks are used to determine finger positions and gestures.

### Cursor Movement

When only the index finger is raised, the tip of the index finger is tracked.

Its coordinates within the camera's active region are mapped to the corresponding coordinates on the computer screen.

A smoothing algorithm is applied to reduce unwanted cursor movement.

```text
Webcam
   |
   v
OpenCV Frame Capture
   |
   v
MediaPipe Hand Landmarker
   |
   v
Hand Landmark Detection
   |
   v
Gesture Recognition
   |
   v
Coordinate Mapping
   |
   v
PyAutoGUI
   |
   v
System Cursor
```

### Mouse Click

When the index and middle fingers are raised, the distance between their fingertips is calculated.

When the fingertips move sufficiently close together, the application interprets the gesture as a mouse click.

```text
Index + Middle Finger
          |
          v
Distance between fingertips
          |
          v
Distance < Threshold
          |
          v
     Mouse Click
```

## Controls

| Gesture / Input       | Action      |
| --------------------- | ----------- |
| Index finger only     | Move cursor |
| Index + middle finger | Click       |
| `Q`                   | Exit        |
| `ESC`                 | Exit        |
| Window `X` button     | Exit        |

## Technologies Used

| Technology | Purpose                                           |
| ---------- | ------------------------------------------------- |
| Python     | Core programming language                         |
| OpenCV     | Webcam capture and image processing               |
| MediaPipe  | Real-time hand landmark detection                 |
| NumPy      | Coordinate interpolation and numerical operations |
| PyAutoGUI  | System mouse control                              |

## Requirements

* Python 3.13 or compatible Python version
* Working webcam
* Windows, macOS, or Linux system capable of running the required dependencies

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/virtual-mouse.git
cd virtual-mouse
```

Replace `your-username/virtual-mouse` with the actual repository URL.

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The project uses the following dependencies:

```text
opencv-python>=4.8.0
mediapipe>=0.10.30,<1.0.0
numpy>=1.24.0
pyautogui>=0.9.54
```

### 3. Run the application

```bash
python VirtualMouse.py
```

On the first launch, the application automatically downloads the MediaPipe Hand Landmarker model and stores it in the local `models` directory.

The resulting project structure will look like:

```text
Virtual-Mouse/
│
├── VirtualMouse.py
├── requirements.txt
├── README.md
│
└── models/
    └── hand_landmarker.task
```

## Configuration

Several parameters can be adjusted directly in `VirtualMouse.py`.

### Camera Resolution

```python
wCam = 640
hCam = 480
```

### Active Tracking Area

```python
frameR = 100
```

A larger value reduces the active area of the camera frame.

### Cursor Smoothing

```python
smoothening = 7
```

Higher values produce smoother but slower cursor movement.

Lower values make the cursor more responsive but can introduce more jitter.

### Click Threshold

```python
if length < 40:
```

This controls how close the index and middle fingertips must be before a click is triggered.

### Click Cooldown

```python
click_cooldown = 0.25
```

This prevents multiple clicks from being generated continuously while the fingers remain close together.

## Project Structure

```text
Virtual-Mouse/
│
├── VirtualMouse.py
│   ├── MediaPipe initialization
│   ├── HandDetector
│   ├── Landmark processing
│   ├── Finger detection
│   ├── Gesture recognition
│   ├── Cursor mapping
│   ├── Mouse control
│   └── Application loop
│
├── requirements.txt
│   └── Python dependencies
│
├── models/
│   └── hand_landmarker.task
│
└── README.md
```

## MediaPipe Architecture

This project uses MediaPipe's modern Tasks API rather than the deprecated `mp.solutions.hands` interface.

The application initializes:

```python
mp.tasks.vision.HandLandmarker
```

and processes webcam frames using video mode:

```python
landmarker.detect_for_video(...)
```

This allows the project to work with newer MediaPipe releases that no longer expose the legacy `mp.solutions` interface.

## Performance

The application displays the current frames-per-second value directly in the camera window.

Performance depends on:

* CPU performance
* Camera resolution
* Webcam frame rate
* MediaPipe processing time
* Background applications
* Cursor smoothing configuration

For better performance, the default camera resolution is set to `640 × 480`.

## Troubleshooting

### MediaPipe installation error

Make sure the dependencies are installed using the Python interpreter that runs the project:

```bash
python -m pip install -r requirements.txt
```

Check the installed MediaPipe version:

```bash
python -c "import mediapipe as mp; print(mp.__version__)"
```

### Camera does not open

The application initially attempts to use camera index `0`.

If the camera cannot be opened, try changing:

```python
cap = cv2.VideoCapture(0)
```

to:

```python
cap = cv2.VideoCapture(1)
```

You can also check whether another application is currently using the webcam.

### Cursor movement is too sensitive

Increase:

```python
smoothening = 7
```

For example:

```python
smoothening = 10
```

### Cursor movement is too slow

Decrease the smoothing value:

```python
smoothening = 5
```

### Multiple clicks are triggered

Increase:

```python
click_cooldown = 0.25
```

For example:

```python
click_cooldown = 0.4
```

## Future Improvements

Potential improvements for future versions include:

* Right-click gesture
* Double-click gesture
* Drag-and-drop gesture
* Scroll gesture
* Volume control gestures
* Customizable gestures
* Gesture configuration through a settings interface
* Multi-hand support
* Improved cursor stabilization
* Application-specific gesture profiles
* Performance optimization

## License

This project is distributed under the license specified in the repository's `LICENSE` file.

If no license file is present, all rights are reserved by the author.

## Author

**Amogh V P**

Developed as a computer vision and human-computer interaction project exploring real-time hand tracking and gesture-based system control.
