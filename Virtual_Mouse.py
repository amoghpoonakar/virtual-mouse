import cv2
import numpy as np
import time
import math
import sys
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

try:
    import mediapipe as mp
except ImportError:
    print("ERROR: mediapipe not installed. Run: pip install mediapipe")
    sys.exit(1)

try:
    import pyautogui
except ImportError:
    print("ERROR: pyautogui not installed. Run: pip install pyautogui")
    sys.exit(1)

# Disable pyautogui failsafe to prevent issues
pyautogui.FAILSAFE = False

# --- SETTINGS ---
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction (Active area)
smoothening = 7
pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

# Screen size detection with fallback
try:
    wScr, hScr = pyautogui.size()
    if wScr <= 0 or hScr <= 0:
        raise Exception("Invalid screen size")
except Exception as e:
    print(f"Warning: Could not detect screen size: {e}")
    print("Using default 1920x1080")
    wScr, hScr = 1920, 1080


class HandDetector:
    """
    A versatile hand detector class that works across different MediaPipe versions
    """
    
    def __init__(self, mode=False, maxHands=1, detectionCon=0.5, trackCon=0.5):
        """
        Initialize hand detector with compatibility for different MediaPipe versions
        
        Args:
            mode: Static image mode (False for video)
            maxHands: Maximum number of hands to detect
            detectionCon: Detection confidence threshold (0-1)
            trackCon: Tracking confidence threshold (0-1)
        """
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.results = None
        self.lmList = []
        
        # Tip IDs for fingers (consistent across versions)
        self.tipIds = [4, 8, 12, 16, 20]
        
        try:
            self.mpHands = mp.solutions.hands
            self.mpDraw = mp.solutions.drawing_utils
            
            # Try modern parameter names first (MediaPipe 0.8.11+)
            try:
                self.hands = self.mpHands.Hands(
                    static_image_mode=self.mode,
                    max_num_hands=self.maxHands,
                    min_detection_confidence=self.detectionCon,
                    min_tracking_confidence=self.trackCon
                )
            except TypeError:
                # Fallback for older versions with different parameter names
                try:
                    self.hands = self.mpHands.Hands(
                        static_image_mode=self.mode,
                        max_num_hands=self.maxHands,
                        min_detection_confidence=self.detectionCon,
                        min_tracking_confidence=self.trackCon,
                        model_complexity=0
                    )
                except TypeError:
                    # Ultimate fallback - use defaults and hope for the best
                    self.hands = self.mpHands.Hands()
            
            print("✓ MediaPipe Hands initialized successfully")
            
        except Exception as e:
            print(f"ERROR: Failed to initialize MediaPipe Hands: {e}")
            raise

    def findHands(self, img, draw=True):
        """
        Detect hands in image
        
        Args:
            img: Input image (BGR format)
            draw: Whether to draw landmarks
            
        Returns:
            Image with landmarks drawn (if draw=True)
        """
        try:
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            if self.hands is None:
                return img
            
            self.results = self.hands.process(imgRGB)
            
            if self.results is None:
                return img
            
            # Draw landmarks if requested and if hand is detected
            if draw and self.results.multi_hand_landmarks:
                for handLms in self.results.multi_hand_landmarks:
                    try:
                        self.mpDraw.draw_landmarks(
                            img, 
                            handLms, 
                            self.mpHands.HAND_CONNECTIONS
                        )
                    except Exception as e:
                        print(f"Warning: Could not draw landmarks: {e}")
                        
        except cv2.error as e:
            print(f"OpenCV error in findHands: {e}")
        except Exception as e:
            print(f"Error in findHands: {e}")
            
        return img

    def findPosition(self, img, handNo=0, draw=True):
        """
        Get landmark positions for detected hand
        
        Args:
            img: Input image
            handNo: Hand index (0 for first hand)
            draw: Whether to draw circles at landmarks
            
        Returns:
            List of landmark positions [[id, x, y], ...]
        """
        self.lmList = []
        
        try:
            if self.results is None or not hasattr(self.results, 'multi_hand_landmarks'):
                return self.lmList
            
            if self.results.multi_hand_landmarks and len(self.results.multi_hand_landmarks) > handNo:
                myHand = self.results.multi_hand_landmarks[handNo]
                h, w, c = img.shape
                
                for id, lm in enumerate(myHand.landmark):
                    try:
                        # Safely get coordinates
                        cx = int(lm.x * w) if hasattr(lm, 'x') else 0
                        cy = int(lm.y * h) if hasattr(lm, 'y') else 0
                        
                        # Clamp values to image bounds
                        cx = max(0, min(cx, w - 1))
                        cy = max(0, min(cy, h - 1))
                        
                        self.lmList.append([id, cx, cy])
                        
                        if draw:
                            cv2.circle(img, (cx, cy), 5, (255, 255, 0), cv2.FILLED)
                    except (AttributeError, ValueError) as e:
                        print(f"Warning: Could not process landmark {id}: {e}")
                        
        except Exception as e:
            print(f"Error in findPosition: {e}")
            
        return self.lmList

    def fingersUp(self):
        """
        Determine which fingers are up
        
        Returns:
            List of 5 binary values [thumb, index, middle, ring, pinky]
            where 1 = up, 0 = down
        """
        fingers = []
        
        try:
            if not self.lmList or len(self.lmList) < 21:
                return [0, 0, 0, 0, 0]
            
            # Thumb (horizontal comparison)
            if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
            
            # Other 4 fingers (vertical comparison)
            for id in range(1, 5):
                if id < len(self.tipIds):
                    tip_y = self.lmList[self.tipIds[id]][2]
                    pip_y = self.lmList[self.tipIds[id] - 2][2]
                    
                    if tip_y < pip_y:  # Tip above PIP = finger up
                        fingers.append(1)
                    else:
                        fingers.append(0)
                        
        except (IndexError, AttributeError) as e:
            print(f"Warning: Error checking fingers: {e}")
            return [0, 0, 0, 0, 0]
            
        return fingers

    def findDistance(self, p1, p2, img, draw=True):
        """
        Calculate distance between two landmarks
        
        Args:
            p1: First landmark ID
            p2: Second landmark ID
            img: Image to draw on
            draw: Whether to draw line and circle
            
        Returns:
            (distance, image, info_list)
        """
        try:
            if not self.lmList or len(self.lmList) <= max(p1, p2):
                return 0, img, [0, 0, 0, 0, 0, 0]
            
            x1, y1 = self.lmList[p1][1:]
            x2, y2 = self.lmList[p2][1:]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            
            length = math.hypot(x2 - x1, y2 - y1)
            
            if draw:
                try:
                    cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                    cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
                except cv2.error:
                    pass
                    
            return length, img, [x1, y1, x2, y2, cx, cy]
            
        except Exception as e:
            print(f"Warning: Error calculating distance: {e}")
            return 0, img, [0, 0, 0, 0, 0, 0]


def main():
    """Main application loop"""
    
    # Initialize camera with error handling
    cap = None
    detector = None
    
    try:
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("ERROR: Could not open camera. Check if camera is connected.")
            return
        
        # Set camera properties with fallback
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, wCam)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, hCam)
        
        # Try to set FPS for stability
        try:
            cap.set(cv2.CAP_PROP_FPS, 30)
        except:
            pass
        
        # Initialize detector
        detector = HandDetector(maxHands=1)
        
        print("=" * 50)
        print("Virtual Mouse Started")
        print("=" * 50)
        print("Controls:")
        print("  - Index finger up: Move mouse")
        print("  - Index + Middle fingers up: Click (bring close together)")
        print("  - Press 'q' to quit")
        print("=" * 50)
        
        frame_count = 0
        fps = 0
        pTime = time.time()
        plocX, plocY = 0, 0
        clocX, clocY = 0, 0
        
        while True:
            try:
                success, img = cap.read()
                
                if not success or img is None:
                    print("Warning: Failed to read frame")
                    continue
                
                # Mirror the frame
                img = cv2.flip(img, 1)
                
                # Detect hands
                img = detector.findHands(img)
                lmList = detector.findPosition(img, draw=False)
                
                # Process hand gestures
                if len(lmList) != 0:
                    try:
                        x1, y1 = lmList[8][1:]  # Index finger tip
                        x2, y2 = lmList[12][1:]  # Middle finger tip
                        
                        fingers = detector.fingersUp()
                        
                        # Mode 1: Index finger up - Mouse moving mode
                        if len(fingers) > 1 and fingers[1] == 1 and fingers[2] == 0:
                            # Draw active rectangle
                            cv2.rectangle(img, (frameR, frameR), 
                                        (wCam - frameR, hCam - frameR), 
                                        (255, 0, 255), 2)
                            
                            # Map coordinates to screen size
                            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
                            
                            # Apply smoothening
                            clocX = plocX + (x3 - plocX) / smoothening
                            clocY = plocY + (y3 - plocY) / smoothening
                            
                            # Move mouse
                            try:
                                pyautogui.moveTo(int(clocX), int(clocY), duration=0)
                            except pyautogui.FailSafeException:
                                print("Mouse moved to corner - failsafe triggered")
                                break
                            except Exception as e:
                                print(f"Warning: Could not move mouse: {e}")
                            
                            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                            plocX, plocY = clocX, clocY
                        
                        # Mode 2: Index + Middle fingers up - Clicking mode
                        elif len(fingers) > 2 and fingers[1] == 1 and fingers[2] == 1:
                            length, img, lineInfo = detector.findDistance(8, 12, img)
                            
                            # Click if fingers are close enough
                            if length < 40:
                                cv2.circle(img, (lineInfo[4], lineInfo[5]), 
                                         15, (0, 255, 0), cv2.FILLED)
                                try:
                                    pyautogui.click()
                                    time.sleep(0.2)  # Debounce clicks
                                except Exception as e:
                                    print(f"Warning: Could not perform click: {e}")
                    
                    except (IndexError, ValueError) as e:
                        print(f"Warning: Hand tracking issue: {e}")
                
                # FPS Calculation
                cTime = time.time()
                fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
                pTime = cTime
                
                # Display FPS with error handling
                try:
                    cv2.putText(img, f'FPS: {int(fps)}', (20, 50), 
                              cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
                    cv2.putText(img, f'Screen: {wScr}x{hScr}', (20, 100),
                              cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
                except cv2.error:
                    pass
                
                # Display frame
                cv2.imshow("Virtual Mouse", img)
                
                # Check for exit key
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # 'q' or ESC
                    print("Shutting down...")
                    break
                
                frame_count += 1
                
            except KeyboardInterrupt:
                print("Interrupted by user")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                continue
    
    except Exception as e:
        print(f"Fatal error: {e}")
    
    finally:
        # Cleanup
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()
        print("Virtual Mouse closed")


if __name__ == "__main__":
    main()
