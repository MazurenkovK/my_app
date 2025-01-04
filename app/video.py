import cv2

class VideoStream:
    def __init__(self, source=0):
        self.source = source
        self.stream = cv2.VideoCapture(self.source)
        if not self.stream.isOpened():
            raise ValueError(f"Cannot open video source {self.source}")

    def get_frame(self):
        ret, frame = self.stream.read()
        if not ret:
            return None
        return frame

    def release(self):
        self.stream.release()