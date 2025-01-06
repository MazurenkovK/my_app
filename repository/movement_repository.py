from abc import ABC, abstractmethod
from datetime import datetime
import os
import cv2

class Movement:
    def __init__(self, timestamp: datetime, description: str, frame=None):
        self.timestamp = timestamp
        self.description = description
        self.frame = frame  # Сохраняем необработанный кадр

class MovementRepository(ABC):
    @abstractmethod
    def add_movement(self, movement: Movement):
        pass

    @abstractmethod
    def get_movements(self):
        pass

class InMemoryMovementRepository(MovementRepository):
    def __init__(self):
        self.movements = []

    def add_movement(self, movement: Movement):
        self.movements.append(movement)

    def get_movements(self):
        return self.movements
    
    def save_frame(self, movement: Movement, save_dir="saved_frames"):
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)  # Создаем директорию, если не существует
        frame_filename = os.path.join(
            save_dir, f"frame_{movement.timestamp.isoformat()}.jpg"
            )
        cv2.imwrite(frame_filename, movement.frame)  # Сохраняем кадр в файл

# Создание глобального репозитория
global_repository = InMemoryMovementRepository()