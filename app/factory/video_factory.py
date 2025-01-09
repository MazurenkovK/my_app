from abc import ABC, abstractmethod
from app.video import VideoStream

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
Factory Pattern используется для создания различных обработчиков 
видеопотока без изменения клиентского кода.
"""

