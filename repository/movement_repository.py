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
        # Преобразуем кадр в оттенки серого
        gray_frame = cv2.cvtColor(movement.frame, cv2.COLOR_BGR2GRAY)
        # Сохраняем цветной кадр
        color_frame_filename = os.path.join(
            save_dir, f"frame_{movement.timestamp.isoformat()}.jpg"
        )
        # Сохраняем цветной кадр в файл
        cv2.imwrite(color_frame_filename, movement.frame)  
        # Сохраняем кадр в оттенках серого
        gray_frame_filename = os.path.join(
            save_dir, f"frame_gray_{movement.timestamp.isoformat()}.jpg"
        )
        # Сохраняем серый кадр в файл
        cv2.imwrite(gray_frame_filename, gray_frame)  

# Создание глобального репозитория
global_repository = InMemoryMovementRepository()