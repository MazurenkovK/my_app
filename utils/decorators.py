from abc import ABC, abstractmethod
from observer.observer import Subject

class DetectorDecorator(Subject, ABC):
    def __init__(self, detector: Subject):
        super().__init__()
        self._detector = detector

    def attach(self, observer):
        self._detector.attach(observer)

    def detach(self, observer):
        self._detector.detach(observer)

    def notify(self, message: str):
        self._detector.notify(message)

    @abstractmethod
    def process_frame(self, frame):
        pass

class LoggingDetectorDecorator(DetectorDecorator):
    def process_frame(self, frame):
        print("LoggingDetectorDecorator: Processing frame")
        return self._detector.process_frame(frame)

class FilterDetectorDecorator(DetectorDecorator):
    def __init__(self, detector: Subject, keyword: str):
        super().__init__(detector)
        self.keyword = keyword

    def process_frame(self, frame):
        frame = self._detector.process_frame(frame)
        # Допустим, фильтруем кадры по некоторым критериям
        print(f"FilterDetectorDecorator: Filter applied with keyword '{self.keyword}'")
        return frame
