import cv2
import numpy as np
import time
import math
import mediapipe as mp
import pyautogui

# --- SETTINGS ---
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction (Active area)
smoothening = 7
pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

# Screen size detection
wScr, hScr = pyautogui.size()

class HandDetector():
    def __init__(self, mode=False, maxHands=1, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        # Yahan parameters explicitly define kiye hain error se bachne ke liye
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 255, 0), cv2.FILLED)
        return self.lmList

    def fingersUp(self):
        fingers = []
        # Thumb
        if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        # 4 Fingers
        for id in range(1, 5):
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def findDistance(self, p1, p2, img, draw=True):
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        length = math.hypot(x2 - x1, y2 - y1)
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
        return length, img, [x1, y1, x2, y2, cx, cy]

# --- MAIN LOOP ---
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = HandDetector(maxHands=1)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1) # Mirror flip
    img = detector.findHands(img)
    lmList = detector.findPosition(img)

    if len(lmList) != 0:
        x1, y1 = lmList[8][1:] # Index finger tip
        x2, y2 = lmList[12][1:] # Middle finger tip
        
        fingers = detector.fingersUp()

        # 1. Sirf Index Finger Up: Mouse Moving Mode
        if fingers[1] == 1 and fingers[2] == 0:
            # Active rectangle draw karo
            cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)
            
            # Coordinates map karo screen size ke hisaab se
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

            # Smoothening apply karo
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            pyautogui.moveTo(clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

        # 2. Index + Middle Finger Up: Clicking Mode
        if fingers[1] == 1 and fingers[2] == 1:
            length, img, lineInfo = detector.findDistance(8, 12, img)
            # Agar ungliyan pas hain toh click karo
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                pyautogui.click()

    # FPS Calculation
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    cv2.imshow("Virtual Mouse", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()