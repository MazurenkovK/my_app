from abc import ABC, abstractmethod
from loguru import logger

class Observer(ABC):
    @abstractmethod
    def update(self, message: str):
        pass

class Subject(ABC):
    def __init__(self):
        self._observers = []

    def attach(self, observer: Observer):
        self._observers.append(observer)
        logger.info(f"Observer {observer} attached.")

    def detach(self, observer: Observer):
        self._observers.remove(observer)
        logger.info(f"Observer {observer} detached.")

    def notify(self, message: str):
        logger.info(f"Notifying observers with message: {message}")
        for observer in self._observers:
            observer.update(message)