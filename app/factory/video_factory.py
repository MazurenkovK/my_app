from abc import ABC, abstractmethod
from app.video import VideoStream
from enum import Enum
import cv2


class MediaSource(Enum):
    WEB_CAM = "WebCam"
    FILE_VIDEO = "FileVideo"
    IMAGE_FILE = "ImageFile"

# Абстрактный базовый класс для обработчиков видеопотока
class VideoStreamHandler(ABC):
    @abstractmethod
    def get_stream(self):
        pass

# Обработчик веб-камеры
class WebcamHandler(VideoStreamHandler):
    def __init__(self, source=0):
        self.source = source

    def get_stream(self):
        return VideoStream(self.source)

# Обработчик RTSP-потока
class RTSPHandler(VideoStreamHandler):
    def __init__(self, url):
        self.url = url

    def get_stream(self):
        return VideoStream(self.url)

# Фабрика для создания обработчиков видеопотока
class VideoStreamHandlerFactory:
    @staticmethod
    def create_handler(stream_type: str, **kwargs) -> VideoStreamHandler:
        if stream_type == "Webcam":
            return WebcamHandler(kwargs.get('source', 0))
        elif stream_type == "RTSP":
            if 'url' not in kwargs:
                raise ValueError("RTSP stream requires 'url' parameter")
            return RTSPHandler(kwargs.get('url'))
        else:
            raise ValueError("Unknown stream type")

"""
# Абстрактный класс-обработчик видеопотока
class StreamHandlerBase(ABC):
    
    @abstractmethod
    def get_frame(self):
        pass

class WebCamStreamHandler(StreamHandlerBase):
    def __init__(self, cam_id=0):
        self.cap = cv2.VideoCapture(cam_id)

    def get_frame(self):
        success, frame = self.cap.read()
        return frame if success else None

class FileVideoStreamHandler(StreamHandlerBase):
    def __init__(self, file_path):
        self.cap = cv2.VideoCapture(file_path)

    def get_frame(self):
        success, frame = self.cap.read()
        return frame if success else None

class ImageFileStreamHandler(StreamHandlerBase):
    def __init__(self, img_path):
        self.img = cv2.imread(img_path)

    def get_frame(self):
        return self.img.copy()

class VideoStreamHandlerFactory:
    @staticmethod
    def create_handler(media_source: MediaSource, param=None):
        if media_source == MediaSource.WEB_CAM:
            return WebCamStreamHandler(param or 0)
        elif media_source == MediaSource.FILE_VIDEO:
            return FileVideoStreamHandler(param)
        elif media_source == MediaSource.IMAGE_FILE:
            return ImageFileStreamHandler(param)
        else:
            raise ValueError("Unsupported media type.")
"""
"""
Factory Pattern используется для создания различных обработчиков 

видеопотока без изменения клиентского кода.
"""
