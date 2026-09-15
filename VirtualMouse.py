import cv2
import numpy as np
import time
import math
import sys
import os
import urllib.request

# ============================================================
# IMPORTS
# ============================================================

try:
    import mediapipe as mp
except ImportError:
    print("ERROR: MediaPipe is not installed.")
    print("Run: python -m pip install mediapipe")
    sys.exit(1)

try:
    import pyautogui
except ImportError:
    print("ERROR: PyAutoGUI is not installed.")
    print("Run: python -m pip install pyautogui")
    sys.exit(1)


# ============================================================
# PYAUTOGUI SETTINGS
# ============================================================

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0


# ============================================================
# MEDIAPIPE MODEL
# ============================================================

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/"
    "hand_landmarker.task"
)

MODEL_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "hand_landmarker.task"
)


def download_model():
    """
    Download the MediaPipe Hand Landmarker model
    automatically if it doesn't already exist.
    """

    if os.path.exists(MODEL_PATH):
        print("✅ Hand Landmarker model found.")
        return True

    print("📥 Hand Landmarker model not found.")
    print("   Downloading model...")

    try:
        os.makedirs(MODEL_DIR, exist_ok=True)

        urllib.request.urlretrieve(
            MODEL_URL,
            MODEL_PATH
        )

        if os.path.exists(MODEL_PATH):
            print("✅ Hand Landmarker model downloaded.")
            return True

    except Exception as e:
        print(f"❌ Could not download model: {e}")

    return False


# ============================================================
# MEDIAPIPE INITIALIZATION
# ============================================================

def create_hand_landmarker():

    if not download_model():

        print(
            "\nERROR: Could not obtain "
            "MediaPipe Hand Landmarker model."
        )

        return None

    try:

        BaseOptions = mp.tasks.BaseOptions

        HandLandmarker = (
            mp.tasks.vision.HandLandmarker
        )

        HandLandmarkerOptions = (
            mp.tasks.vision.HandLandmarkerOptions
        )

        VisionRunningMode = (
            mp.tasks.vision.RunningMode
        )

        options = HandLandmarkerOptions(

            base_options=BaseOptions(
                model_asset_path=MODEL_PATH
            ),

            running_mode=VisionRunningMode.VIDEO,

            num_hands=1,

            min_hand_detection_confidence=0.5,

            min_hand_presence_confidence=0.5,

            min_tracking_confidence=0.5
        )

        landmarker = (
            HandLandmarker.create_from_options(
                options
            )
        )

        print(
            "✅ MediaPipe Hand Landmarker initialized."
        )

        return landmarker

    except Exception as e:

        print(
            "❌ Failed to initialize "
            f"MediaPipe Hand Landmarker: {e}"
        )

        print("\nMediaPipe version:")
        print(mp.__version__)

        return None


# ============================================================
# HAND CONNECTIONS
# ============================================================

HAND_CONNECTIONS = [

    # Thumb
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),

    # Index
    (0, 5),
    (5, 6),
    (6, 7),
    (7, 8),

    # Middle
    (9, 10),
    (10, 11),
    (11, 12),

    # Palm
    (5, 9),
    (9, 13),
    (13, 17),

    # Ring
    (13, 14),
    (14, 15),
    (15, 16),

    # Pinky
    (17, 18),
    (18, 19),
    (19, 20),

    # Palm / thumb connection
    (0, 17)
]


# ============================================================
# HAND DETECTOR
# ============================================================

class HandDetector:

    def __init__(
        self,
        landmarker,
        maxHands=1
    ):

        self.landmarker = landmarker

        self.maxHands = maxHands

        self.results = None

        self.lmList = []

        self.tipIds = [
            4,
            8,
            12,
            16,
            20
        ]

        self.timestamp_ms = 0


    # ========================================================
    # DETECT HANDS
    # ========================================================

    def findHands(
        self,
        img,
        draw=True
    ):

        try:

            # OpenCV BGR → RGB
            imgRGB = cv2.cvtColor(
                img,
                cv2.COLOR_BGR2RGB
            )

            # Create MediaPipe image
            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=imgRGB
            )

            # Timestamp must continuously increase
            self.timestamp_ms += 33

            self.results = (
                self.landmarker.detect_for_video(
                    mp_image,
                    self.timestamp_ms
                )
            )

            # Draw hand landmarks
            if (
                draw
                and self.results
                and self.results.hand_landmarks
            ):

                for hand_landmarks in (
                    self.results.hand_landmarks
                ):

                    h, w, _ = img.shape

                    points = []

                    # Convert normalized coordinates
                    for landmark in hand_landmarks:

                        x = int(
                            landmark.x * w
                        )

                        y = int(
                            landmark.y * h
                        )

                        x = max(
                            0,
                            min(x, w - 1)
                        )

                        y = max(
                            0,
                            min(y, h - 1)
                        )

                        points.append(
                            (x, y)
                        )

                    # Draw connections
                    for start, end in HAND_CONNECTIONS:

                        if (
                            start < len(points)
                            and end < len(points)
                        ):

                            cv2.line(
                                img,
                                points[start],
                                points[end],
                                (255, 0, 255),
                                2
                            )

                    # Draw landmarks
                    for x, y in points:

                        cv2.circle(
                            img,
                            (x, y),
                            4,
                            (0, 255, 0),
                            cv2.FILLED
                        )

        except Exception as e:

            print(
                f"⚠️ Hand detection error: {e}"
            )

        return img


    # ========================================================
    # GET LANDMARK POSITIONS
    # ========================================================

    def findPosition(
        self,
        img,
        handNo=0,
        draw=True
    ):

        self.lmList = []

        try:

            if (
                self.results is None
                or not self.results.hand_landmarks
            ):

                return self.lmList

            if handNo >= len(
                self.results.hand_landmarks
            ):

                return self.lmList

            myHand = (
                self.results.hand_landmarks[handNo]
            )

            h, w, _ = img.shape

            for id, landmark in enumerate(myHand):

                cx = int(
                    landmark.x * w
                )

                cy = int(
                    landmark.y * h
                )

                # Keep coordinates inside frame
                cx = max(
                    0,
                    min(cx, w - 1)
                )

                cy = max(
                    0,
                    min(cy, h - 1)
                )

                self.lmList.append(
                    [id, cx, cy]
                )

                if draw:

                    cv2.circle(
                        img,
                        (cx, cy),
                        5,
                        (255, 255, 0),
                        cv2.FILLED
                    )

        except Exception as e:

            print(
                f"⚠️ Error in findPosition: {e}"
            )

        return self.lmList


    # ========================================================
    # DETERMINE WHICH FINGERS ARE UP
    # ========================================================

    def fingersUp(self):

        fingers = []

        try:

            if len(self.lmList) < 21:

                return [
                    0,
                    0,
                    0,
                    0,
                    0
                ]

            # ------------------------------------------------
            # THUMB
            # ------------------------------------------------

            if (
                self.lmList[self.tipIds[0]][1]
                >
                self.lmList[
                    self.tipIds[0] - 1
                ][1]
            ):

                fingers.append(1)

            else:

                fingers.append(0)


            # ------------------------------------------------
            # OTHER FOUR FINGERS
            # ------------------------------------------------

            for id in range(1, 5):

                tip = self.tipIds[id]

                tip_y = self.lmList[tip][2]

                pip_y = self.lmList[tip - 2][2]

                if tip_y < pip_y:

                    fingers.append(1)

                else:

                    fingers.append(0)

        except (
            IndexError,
            AttributeError
        ):

            return [
                0,
                0,
                0,
                0,
                0
            ]

        return fingers


    # ========================================================
    # DISTANCE BETWEEN TWO LANDMARKS
    # ========================================================

    def findDistance(
        self,
        p1,
        p2,
        img,
        draw=True
    ):

        try:

            if (
                len(self.lmList) <= p1
                or
                len(self.lmList) <= p2
            ):

                return (
                    0,
                    img,
                    [
                        0,
                        0,
                        0,
                        0,
                        0,
                        0
                    ]
                )

            x1, y1 = self.lmList[p1][1:]

            x2, y2 = self.lmList[p2][1:]

            cx = (
                x1 + x2
            ) // 2

            cy = (
                y1 + y2
            ) // 2

            length = math.hypot(
                x2 - x1,
                y2 - y1
            )

            if draw:

                cv2.line(
                    img,
                    (x1, y1),
                    (x2, y2),
                    (255, 0, 255),
                    3
                )

                cv2.circle(
                    img,
                    (cx, cy),
                    10,
                    (0, 255, 0),
                    cv2.FILLED
                )

            return (
                length,
                img,
                [
                    x1,
                    y1,
                    x2,
                    y2,
                    cx,
                    cy
                ]
            )

        except Exception as e:

            print(
                f"⚠️ Distance error: {e}"
            )

            return (
                0,
                img,
                [
                    0,
                    0,
                    0,
                    0,
                    0,
                    0
                ]
            )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("                 VIRTUAL MOUSE")
    print("=" * 60)

    print(
        f"🐍 Python: "
        f"{sys.version.split()[0]}"
    )

    print(
        f"📦 MediaPipe: "
        f"{mp.__version__}"
    )

    print("=" * 60)


    # ========================================================
    # CAMERA SETTINGS
    # ========================================================

    wCam = 640
    hCam = 480

    frameR = 100

    smoothening = 7


    # ========================================================
    # SCREEN SIZE
    # ========================================================

    try:

        wScr, hScr = pyautogui.size()

        print(
            f"🖥️ Screen: "
            f"{wScr}x{hScr}"
        )

    except Exception as e:

        print(
            f"⚠️ Could not detect screen size: {e}"
        )

        wScr = 1920
        hScr = 1080


    # ========================================================
    # INITIALIZE MEDIAPIPE
    # ========================================================

    landmarker = create_hand_landmarker()

    if landmarker is None:

        print(
            "\n❌ Virtual Mouse could not start."
        )

        return


    detector = HandDetector(
        landmarker,
        maxHands=1
    )


    # ========================================================
    # INITIALIZE CAMERA
    # ========================================================

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():

        print(
            "\n❌ ERROR: Could not open camera."
        )

        print(
            "Check camera permissions "
            "or try changing VideoCapture(0) "
            "to VideoCapture(1)."
        )

        landmarker.close()

        return


    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        wCam
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        hCam
    )

    cap.set(
        cv2.CAP_PROP_FPS,
        30
    )


    # ========================================================
    # MOUSE VARIABLES
    # ========================================================

    plocX = 0
    plocY = 0

    clocX = 0
    clocY = 0

    pTime = time.time()

    last_click_time = 0

    click_cooldown = 0.25


    # ========================================================
    # START MESSAGE
    # ========================================================

    print()
    print("=" * 60)
    print("           ✅ VIRTUAL MOUSE STARTED")
    print("=" * 60)

    print("Controls:")
    print("  ☝️  Index finger        → Move mouse")
    print("  🤌 Index + Middle      → Click")
    print("  Q                      → Quit")
    print("  ESC                    → Quit")
    print("  X button               → Quit")

    print("=" * 60)
    print()


    # ========================================================
    # MAIN LOOP
    # ========================================================

    try:

        while True:

            # ------------------------------------------------
            # READ CAMERA
            # ------------------------------------------------

            success, img = cap.read()

            if not success:

                print(
                    "⚠️ Failed to read camera frame."
                )

                continue


            # Mirror camera
            img = cv2.flip(
                img,
                1
            )


            # ------------------------------------------------
            # HAND DETECTION
            # ------------------------------------------------

            img = detector.findHands(
                img,
                draw=True
            )

            lmList = detector.findPosition(
                img,
                draw=False
            )


            # ------------------------------------------------
            # PROCESS HAND
            # ------------------------------------------------

            if len(lmList) >= 21:

                try:

                    # Index fingertip
                    x1, y1 = lmList[8][1:]

                    # Middle fingertip
                    x2, y2 = lmList[12][1:]

                    fingers = detector.fingersUp()


                    # =================================================
                    # MODE 1
                    # INDEX FINGER ONLY = MOVE
                    # =================================================

                    if (
                        fingers[1] == 1
                        and fingers[2] == 0
                    ):

                        # Active camera area

                        cv2.rectangle(
                            img,
                            (
                                frameR,
                                frameR
                            ),
                            (
                                wCam - frameR,
                                hCam - frameR
                            ),
                            (255, 0, 255),
                            2
                        )


                        # Map camera coordinates
                        # to screen coordinates

                        x3 = np.interp(
                            x1,
                            (
                                frameR,
                                wCam - frameR
                            ),
                            (
                                0,
                                wScr
                            )
                        )

                        y3 = np.interp(
                            y1,
                            (
                                frameR,
                                hCam - frameR
                            ),
                            (
                                0,
                                hScr
                            )
                        )


                        # Smooth movement

                        clocX = (
                            plocX
                            +
                            (
                                x3 - plocX
                            )
                            /
                            smoothening
                        )

                        clocY = (
                            plocY
                            +
                            (
                                y3 - plocY
                            )
                            /
                            smoothening
                        )


                        # Move mouse

                        pyautogui.moveTo(
                            int(clocX),
                            int(clocY),
                            duration=0
                        )


                        # Draw cursor point

                        cv2.circle(
                            img,
                            (x1, y1),
                            15,
                            (255, 0, 255),
                            cv2.FILLED
                        )


                        plocX = clocX
                        plocY = clocY


                    # =================================================
                    # MODE 2
                    # INDEX + MIDDLE = CLICK
                    # =================================================

                    elif (
                        fingers[1] == 1
                        and fingers[2] == 1
                    ):

                        length, img, lineInfo = (
                            detector.findDistance(
                                8,
                                12,
                                img
                            )
                        )


                        # Fingers close together
                        # = click

                        if length < 40:

                            cv2.circle(
                                img,
                                (
                                    lineInfo[4],
                                    lineInfo[5]
                                ),
                                15,
                                (0, 255, 0),
                                cv2.FILLED
                            )


                            current_time = (
                                time.time()
                            )


                            # Click cooldown

                            if (
                                current_time
                                -
                                last_click_time
                                >
                                click_cooldown
                            ):

                                pyautogui.click()

                                last_click_time = (
                                    current_time
                                )


                except (
                    IndexError,
                    ValueError
                ):

                    pass


            # =================================================
            # FPS
            # =================================================

            cTime = time.time()

            fps = (
                1 / (cTime - pTime)
                if cTime - pTime > 0
                else 0
            )

            pTime = cTime


            # =================================================
            # UI
            # =================================================

            cv2.putText(
                img,
                f"FPS: {int(fps)}",
                (20, 50),
                cv2.FONT_HERSHEY_PLAIN,
                2,
                (255, 0, 0),
                2
            )

            cv2.putText(
                img,
                f"Screen: {wScr}x{hScr}",
                (20, 85),
                cv2.FONT_HERSHEY_PLAIN,
                1.5,
                (0, 255, 0),
                2
            )

            cv2.putText(
                img,
                "Q / ESC / X = Quit",
                (20, 120),
                cv2.FONT_HERSHEY_PLAIN,
                1.5,
                (0, 255, 255),
                2
            )


            # =================================================
            # SHOW WINDOW
            # =================================================

            cv2.imshow(
                "Virtual Mouse",
                img
            )


            # =================================================
            # KEYBOARD EXIT
            # =================================================

            key = (
                cv2.waitKey(1)
                & 0xFF
            )

            # Q or ESC
            if (
                key == ord("q")
                or key == 27
            ):

                print(
                    "\n👋 Shutting down..."
                )

                break


            # =================================================
            # X BUTTON EXIT
            # =================================================

            try:

                window_visible = (
                    cv2.getWindowProperty(
                        "Virtual Mouse",
                        cv2.WND_PROP_VISIBLE
                    )
                )

                if window_visible < 1:

                    print(
                        "\n❌ Virtual Mouse window closed."
                    )

                    break

            except cv2.error:

                # Window no longer exists
                break


    except KeyboardInterrupt:

        print(
            "\n⏹️ Interrupted by user."
        )


    except Exception as e:

        print(
            f"\n❌ Fatal error: {e}"
        )


    finally:

        # =====================================================
        # CLEANUP
        # =====================================================

        print(
            "\n🧹 Cleaning up..."
        )

        try:
            cap.release()
        except Exception:
            pass

        try:
            cv2.destroyAllWindows()
        except Exception:
            pass

        try:
            landmarker.close()
        except Exception:
            pass

        print(
            "👋 Virtual Mouse closed."
        )


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":

    main()
