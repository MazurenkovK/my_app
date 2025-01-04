# app/detectors.py

import cv2
from observer.observer import Observer, Subject

class MotionDetector(Subject):
    def __init__(self, min_area=500):
        super().__init__()
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2()
        self.min_area = min_area

    def process_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        fg_mask = self.bg_subtractor.apply(gray)
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        motion_detected = False
        for contour in contours:
            if cv2.contourArea(contour) > self.min_area:
                motion_detected = True
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        if motion_detected:
            self.notify("Motion detected in frame")
        return frame