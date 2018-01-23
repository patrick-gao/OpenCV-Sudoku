# File containing all hand detection algorithms

class handTracking(object):
    import cv2
    import numpy
    import math

    def __init__(self):
        self.cv2 = handTracking.cv2
        self.np = handTracking.numpy
        self.math = handTracking.math
        self.cap = self.cv2.VideoCapture(0)                                                          # Initialize camera
        self.cap.set(3, 800)                                                                           # Set frame width
        self.cap.set(4, 300)                                                                          # Set frame height
        self.cap.set(5, 30)                                                                       # Set video frame rate
        self.min_YCrCb = self.np.array([0, 138, 77], self.np.uint8)                      # Minimum skin threshold values
        self.max_YCrCb = self.np.array([255, 183, 127], self.np.uint8)                   # Maximum skin threshold values

                                                                        # Initialize Haar cascade for facial recognition
        self.face_cascade = self.cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    def getScreenSize(self):
        height, width, channels = self.cap.read()[1].shape
        return (width, height)

    def loop(self):
        cv2 = self.cv2

        ret, frame = self.cap.read()                                  # Store each frame from the video capture in frame
        width, height, channels = frame.shape                                                 # Find dimensions of frame
        frame = handTracking.cv2.flip(frame, 1)                                                # Flips frame over y axis

        ### Face removal ###
        frame, faceRemoved = handTracking.removeFace(self, frame, frame.copy())

        ### Blur ###
        faceRemoved = cv2.medianBlur(faceRemoved, 7)

        ### Skin Mask ###
        frameYCrCb = cv2.cvtColor(faceRemoved, cv2.COLOR_BGR2YCR_CB)           # Converts frame from BGR to YCrCb format
                                               # Creates mask for only objects within the bounds of skin color set above
        skinRegion = cv2.inRange(frameYCrCb, self.min_YCrCb, self.max_YCrCb)

                                                                         # Performs Otsu thresholding on the skin region
        ret1, thresh = cv2.threshold(skinRegion, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        ### Erosion and Dilation ###
        erode1 = cv2.erode(thresh, None, iterations=2)
        dilate1 = cv2.dilate(erode1, None, iterations=1)

        ### Contours ###
        contours = cv2.findContours(dilate1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]
        contours.sort(key=cv2.contourArea, reverse=True)

        threshArea = 5000                                                  # Sets minimum threshold for the contour area
        filteredContours = []
        for i in range(len(contours)):                                  # Only contours with an area above 5000 are kept
            area = cv2.contourArea(contours[i])
            if area >= threshArea:
                filteredContours.append(contours[i])

        countList = []
        handList = []
        total = 0

        ### Two hands ###
        if len(filteredContours) >= 2:                              # Finds contours and number of fingers for each hand
            cnt1 = filteredContours[0]
            cnt2 = filteredContours[1]
            count1, hand1 = handTracking.trackHand(self, cnt1, frame, (50, 100), width)
            count2, hand2 = handTracking.trackHand(self, cnt2, frame, (50, 150), width)
            countList += [count1, count2]
            handList += [hand1, hand2]
            total = sum(countList)                                                             # Total number of fingers

        ### One hand ###
        elif len(filteredContours) >= 1:
            cnt1 = filteredContours[0]
            count1, hand1 = handTracking.trackHand(self, cnt1, frame, (50, 100), width)
            countList.append(count1)
            handList.append(hand1)
            total = sum(countList)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Converts frame from BGR to RGB format in preparation for Pygame

        cv2.imshow("thresh", erode1)
        return frame, erode1, total, handList

    def removeFace(self, original, copy):                                              # Removes the face from the frame
        cv2 = self.cv2

        gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)                                         # Convert to grayscale
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)                                            # Find faces
        for (x, y, w, h) in faces:
                                                                     # Draw black rectangle over face in grayscale image
            cv2.rectangle(copy, (x, y), (x + w, int(y + 1.2*h)), (0, 0, 0), -1)

        return original, copy

    def trackHand(self, cnt, frame, textPos, width):                        # Tracks hand position and number of fingers
        cv2 = self.cv2
        math = self.math

        count = 0
        side = 0
        moments = cv2.moments(cnt)
                                                                                     # Finds center coordinates for hand
        cx = int(moments['m10'] / moments['m00'])
        cy = int(moments['m01'] / moments['m00'])
        hull = cv2.convexHull(cnt, returnPoints = False)          # Finds convex hull of the hand contour (only indices)
        pointsHull = cv2.convexHull(cnt, returnPoints = True)    # Finds convex hull of the hand contour (actual points)

                                                # Finds shortest distance from the center of the hand to the convex hull
        radius = int(1.2*cv2.pointPolygonTest(pointsHull, (cx, cy), True))
                                                      # Draws largest circle inside the convex hull centered at (cx, cy)
        cv2.circle(frame, (cx, cy), radius, (255, 255, 255), 2)

        x, y, w, h = cv2.boundingRect(cnt)                                        # Draws bounding rectangle around hand
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                                                        # Finds convexity defects along contour based on its convex hull
        defects = cv2.convexityDefects(cnt, hull)

        if cx < width/2:                                          # Center of the hand is on the left side of the screen
            side = 0
        elif cx > width/2:                                       # Center of the hand is on the right side of the screen
            side = 1

        try:
            for i in range(defects.shape[0]):                                          # For all convexity defects found
                s, e, f, d = defects[i, 0]

                start = tuple(cnt[s][0])
                end = tuple(cnt[e][0])
                far = tuple(cnt[f][0])
                       # Find length of sides of triangle between two nearest points on convex hull and convexity defect
                a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)

                                                      # Use Law of Cosines to find angle of triangle at convexity defect
                angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57

                                         # Determines end points to draw lines that most closely approximate the fingers
                if side:              # If the hand is on the right side, use the closest right point on the convex hull
                    fingerLen = b
                    defectPoint = start
                else:                   # If the hand is on the left side, use the closest left point on the convex hull
                    fingerLen = c
                    defectPoint = end

                            # If the height of the bounding rectangle is smaller than the diameter of the center circle,
                                                      # then the hand must be in a fist, and therefore no fingers are up
                if h > 2.4*radius:
                    if fingerLen >= h/4 and angle < 90:
                        count += 1
                        # cv2.circle(frame, far, 1, [0, 0, 255], 6)
                        # cv2.circle(frame, end, 1, [0, 0, 255], 12)
                        cv2.line(frame, defectPoint, far, [255, 0, 0], 2)         # Draws lines that approximate fingers
                else:
                    return (0, (side, (cx, cy)))                         # No fingers are up, then the hand is in a fist

                cv2.line(frame, start, end, [0, 255, 0], 2)                                              #Draws contours
            return (count + 1, (side, (cx, cy)))

        except(AttributeError):
            print("No defects found")
            return (0, (side, (cx, cy)))
