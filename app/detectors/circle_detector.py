from app.repository.movement_repository import MovementRepository, Movement
from datetime import datetime
from app.observer.observer import Subject
from loguru import logger
from pydantic import BaseModel, PositiveInt, PositiveFloat, NonNegativeFloat
import cv2
import numpy as np
import pytz
import time

# Получаем время в Московском часовом поясе
moscow_tz = pytz.timezone('Europe/Moscow')

# Функция/свертка для повышения четкости кадра
def sharpen_image(image):
       kernel = np.array([[0, -1, 0],
                          [-1, 5, -1],
                          [0, -1, 0]])
       sharpened = cv2.filter2D(image, -1, kernel)
       return sharpened

# Создаем Pydantic модель для валидации конфигурации
class CircleDetectorConfig(BaseModel):
    """Конфигурация детектора кругов с валидацией"""
    dp: PositiveFloat = 0.5
    min_dist: PositiveInt = 200
    param1: PositiveInt = 100
    param2: PositiveInt = 150
    min_radius: PositiveInt = 70
    max_radius: PositiveInt = 10000
    min_delay: NonNegativeFloat = 0
    save_delay: NonNegativeFloat = 2    
    
class CircleDetector(Subject):
    def __init__(self, repository: MovementRepository, config: CircleDetectorConfig):
        super().__init__()
        self.config = config

        # Инициализация параметров из валидированного конфига
        self.dp = config.dp  # Разрешение активации в пространстве параметров
        # Минимальное расстояние между центрами обнаруженных кругов
        self.min_dist = config.min_dist  
        # Первый параметр для Canny-обработчика (порог)
        self.param1 = config.param1  
        # Второй параметр для метода HoughCircles (порог)
        self.param2 = config.param2  
        self.min_radius = config.min_radius  # Минимальный радиус кругов
        self.max_radius = config.max_radius  # Максимальный радиус кругов
        self.repository = repository
        self.last_detection_time = 0  # Время последнего обнаружения
        self.min_delay = config.min_delay
        self.save_delay = config.save_delay    
        self.last_save_time = 0  # Время последнего сохранения
        self.is_saving = False  # Флаг для отслеживания процесса сохранения

    def process_frame(self, frame):
        #logging.debug("Processing frame")
        current_time = time.time()  # Получаем текущее время
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5) 
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=self.dp,
            minDist=self.min_dist,
            param1=self.param1,
            param2=self.param2,
            minRadius=self.min_radius,
            maxRadius=self.max_radius
        )

        if circles is not None and len(circles[0]) > 0:                        
            #logging.debug(f"Circles detected: {circles}")
            if (current_time - self.last_detection_time) >= self.min_delay:
                for (x, y, radius) in np.uint16(np.around(circles[0, :])):
                    cv2.circle(frame, (x, y), radius, (0, 255, 0), 2)  
                    cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)       
                message = "Circle detected in frame"                
                self.notify(message)
                movement = Movement(
                    timestamp=datetime.now(moscow_tz), 
                    description=message
                )   
                logger.info(f"Circles detected: {circles}")             

                # Начинаем процесс сохранения, если он еще не идет
                if not self.is_saving:
                    self.is_saving = True
                    self.last_save_time = current_time  
                
                # Проверяем, прошла ли задержка для сохранения
                if (current_time - self.last_save_time) >= self.save_delay:
                    # Обрезаем изображение
                    crop_size = int(2.5 * radius)
                    x_start = max(0, x - crop_size // 2)
                    y_start = max(0, y - crop_size // 2)
                    x_end = min(frame.shape[1], x + crop_size // 2)
                    y_end = min(frame.shape[0], y + crop_size // 2)

                    cropped_frame = frame[y_start:y_end, x_start:x_end]
                    logger.info(f"Object is focused. The frame size to save: {crop_size}x{crop_size}")

                    # Сохраняем данные о движении
                    movement.frame = sharpen_image(cropped_frame.copy())
                    self.repository.add_movement(movement)
                    self.repository.save_frame(movement)
                    self.repository.save_image_to_db(movement)
                    self.is_saving = False  # Завершаем процесс сохранения
                    self.last_detection_time = current_time
            
        return frame

'''
Класс CircleDetector:

1. Параметры для HoughCircles:
   - dp: Доля разрешения активации в пространстве параметров. 
   Значение 1 означает, что используется то же разрешение, 
   что и входное изображение.
   - min_dist: Минимальное расстояние между центрами 
   обнаруженных кругов.
   - param1: Первый параметр для Canny-обработчика, 
   используемый для выявления границ.
   - param2: Второй параметр для HoughCircles, который определяет 
   порог для обнаруженных кругов.
   - min_radius и max_radius: Минимальный и максимальный радиусы 
   кругов для обнаружения (min_radius=70 - детектирует круг 0,15м на расстоянии 1,3м).
   - min_delay: минимальная задержка между детектированиями в секундах.
   - save_delay: задержка перед сохранением кадра для стабилизации изображения


2. Медианный фильтр:
   - Обработанный кадр сначала преобразуется в оттенки серого 
   и проходит через медианный фильтр для уменьшения шумов, 
   что улучшает точность выделения кругов.

3. Использование HoughCircles:
   - Метод cv2.HoughCircles ищет окружности в изображении. 
   Если круги найдены, они рисуются на кадре, 
   рисуя как саму окружность, так и центр круга.

4. Уведомление:
   - Если хотя бы один круг был обнаружен, вызывается метод 
   notify, чтобы уведомить наблюдателей о данном событии.

Класс CircleDetector обнаруживает круги 
в кадрах видео с использованием методов 
обработки изображений OpenCV для решения конкретной задачи.
'''