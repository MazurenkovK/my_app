# movement_repository.py
from datetime import datetime
from loguru import logger
import os
import cv2
from abc import ABC, abstractmethod
from app.models import get_db, Image  # Импортируем необходимые функции и классы
from sqlalchemy.orm import Session

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
        logger.info(f"Movement added: {movement.timestamp}, Description: {movement.description}")

    def get_movements(self):
        logger.info("Retrieving movements.")
        return self.movements
    
    def clear_movements(self):
        self.movements = []
    
    def save_frame(self, movement: Movement, save_dir="saved_frames"):
        try:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)  # Создаем директорию, если не существует
                logger.info(f"Directory created: {save_dir}")

            # Преобразуем кадр в оттенки серого
            gray_frame = cv2.cvtColor(movement.frame, cv2.COLOR_BGR2GRAY)

            # Сохраняем цветной кадр
            color_frame_filename = os.path.join(
                save_dir, f"frame_{movement.timestamp.isoformat()}.jpg"
            )
            cv2.imwrite(color_frame_filename, movement.frame)
            logger.info(f"Saved color frame: {color_frame_filename}")

            # Сохраняем кадр в оттенках серого
            gray_frame_filename = os.path.join(
                save_dir, f"frame_gray_{movement.timestamp.isoformat()}.jpg"
            )
            cv2.imwrite(gray_frame_filename, gray_frame)
            logger.info(f"Saved gray frame: {gray_frame_filename}")
        except Exception as e:
            logger.error(f"Error saving frame: {e}")
    
    def save_image_to_db(self, movement: Movement):
        try:
            db: Session = next(get_db())
            db_image = Image(timestamp=movement.timestamp, description=movement.description, image_data=movement.frame.tobytes())
            db.add(db_image)
            db.commit()
            db.refresh(db_image)
            logger.info(f"Image saved to database with ID: {db_image.id}")
        except Exception as e:
            logger.error(f"Error saving to the db: {e}")


# Создание глобального репозитория
#global_repository = InMemoryMovementRepository()