import os
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import speech_recognition as sr

# Variables
width, height = 1280, 720
gestureThreshold = 300
folderPath = "Presentation"

# Camera Setup
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Get the list of presentation images
pathImages = sorted(os.listdir(folderPath), key=len)
# print(pathImages)

# Variables
imgList = []
delay = 30
buttonPressed = False
counter = 0
drawMode = False
imgNumber = 0
delayCounter = 0
annotations = [[]]
annotationNumber = 0
annotationStart = False
hs, ws = int(120 * 1), int(213 * 1)  # width and height of small image

# Hand Detector
detector = HandDetector(detectionCon=0.8, maxHands=2)

# Speech Recognizer
recognizer = sr.Recognizer()

# Zoom Parameters
zoomScale = 1.0
zoomSpeed = 0.02

while True:
    # Import Images
    success, img = cap.read()
    img = cv2.flip(img, 1)
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)

    hands, img = detector.findHands(img)
    cv2.line(img,(0, gestureThreshold), (width, gestureThreshold), (0, 255, 0), 10)

    if hands and buttonPressed is False:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        cx, cy = hand['center']
        lmList = hand['lmList']

        # Constrain values for easier drawing
        xVal = int(np.interp(lmList[8][0], [width//2, width], [0, width]))
        yVal = int(np.interp(lmList[8][1], [150, height-150], [0, height]))
        indexFinger = xVal, yVal

        if cy <= gestureThreshold: # if hand is at the height of the face
            annotationStart = False
            # Gesture 1 - Left
            if fingers == [1, 0, 0, 0, 0]:
                annotationStart = False
                print ("Left")
                if imgNumber > 0:
                    buttonPressed = True
                    annotations = [[]]
                    annotationNumber = 0
                    imgNumber -= 1

            # Gesture 2 - Right
            if fingers == [0, 0, 0, 0, 1]:
                annotationStart = False
                print("Right")
                if imgNumber < len(pathImages)-1:
                    buttonPressed = True
                    annotations = [[]]
                    annotationNumber = 0
                    imgNumber += 1

        # Gesture 3 - Show Pointer
        if fingers == [0, 1, 1, 0, 0]:
            cv2.circle(imgCurrent, indexFinger, 12,(0, 0, 255), cv2.FILLED)
            annotationStart = False

        # Gesture 4 - Draw Pointer
        if fingers == [0, 1, 0, 0, 0]:
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
            annotations[annotationNumber].append(indexFinger)
        else:
            annotationStart = False

        # Gesture 5 - Erase
        if fingers == [0, 1, 1, 1, 0]:
            if annotations:
                if annotationNumber >= 0:
                    annotations.pop(-1)
                    annotationNumber -= 1
                    buttonPressed = True

        # Gesture 6 - Zoom in/out
        if fingers == [0, 1, 1, 1, 1]:
            zoomScale += zoomSpeed
            print("Zoom In:", zoomScale)
        if fingers == [1, 1, 1, 1, 1]:
            zoomScale -= zoomSpeed
            if zoomScale < 1.0:
                zoomScale = 1.0
            print("Zoom Out:", zoomScale)

        # Gesture 7 - "Go to Slide No. __ "
        if cy > gestureThreshold:
            if fingers == [1, 0, 0, 0, 0]:
                buttonPressed = True
                print("Go to specific slide gesture detected")
                try:
                    # Prompt user for slide number using voice command
                    with sr.Microphone() as source:
                        print("Listening for slide number...")
                        recognizer.pause_threshold = 1
                        audio = recognizer.listen(source)
                        # Recognize the voice command
                        command = recognizer.recognize_google(audio, language="en-in").lower()
                        print(f"Voice Command: {command}")
                        # Extract slide number from command
                        slide_number = int(command.split("slide")[-1].strip())
                        # Verify and navigate to the desired slide
                        if 0 < slide_number <= len(pathImages):
                            imgNumber = slide_number -1
                            annotations = [[]]
                            annotationNumber = -1
                            annotationStart = False
                            print(f"Going to slide {slide_number}")
                            for path in pathImages:
                                if (path == imgNumber):
                                    cv2.imshow("Image", img)

                        else:
                            print("Invalid slide number")
                            exit()

                except sr.UnknownValueError:
                    print("Could not understand audio")

                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")
                    exit()

    else:
        annotationStart = False

    # Button Pressed Iterations
    if buttonPressed:
        counter += 1
        if counter > delay:
            counter = 0
            buttonPressed = False

    for i in range(len(annotations)):
        for j in range(len(annotations[i])):
            if j != 0:
                cv2.line(imgCurrent, annotations[i][j-1], annotations[i][j], (0, 0, 200), 12)

    imgCurrent = cv2.resize(imgCurrent, None, fx=zoomScale, fy=zoomScale)

    # Adding Webcam image on the slides
    imgSmall = cv2.resize(img, (ws, hs))
    h, w, _ = imgCurrent.shape
    imgCurrent[0:hs,w-ws:w] = imgSmall

    cv2.imshow("Image", img)
    cv2.imshow("Slides", imgCurrent)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cv2.destroyAllWindows()