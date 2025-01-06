from repository.movement_repository import MovementRepository, Movement
from datetime import datetime
from observer.observer import Subject
import cv2
import numpy as np
import pytz
import time

# Получаем время в Московском часовом поясе
moscow_tz = pytz.timezone('Europe/Moscow')

class CircleDetector(Subject):
    def __init__(
            self, repository: MovementRepository, 
            dp=0.5, min_dist=200, 
            param1=100, param2=150, 
            min_radius=70, max_radius=10000,
            min_delay=10.0
        ):
        super().__init__()
        self.dp = dp  # Разрешение активации в пространстве параметров
        # Минимальное расстояние между центрами обнаруженных кругов
        self.min_dist = min_dist  
        # Первый параметр для Canny-обработчика (порог)
        self.param1 = param1  
        # Второй параметр для метода HoughCircles (порог)
        self.param2 = param2  
        self.min_radius = min_radius  # Минимальный радиус кругов
        self.max_radius = max_radius  # Максимальный радиус кругов
        self.repository = repository
        self.last_detection_time = 0  # Время последнего обнаружения
        self.min_delay = min_delay  

    def process_frame(self, frame):
        current_time = time.time()  # Получаем текущее время
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Применение медианного фильтра для уменьшения шума
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
        # Если круги найдены, обрабатываем их
        if circles is not None:
            # Проверяем время последнего обнаружения
            if (current_time - self.last_detection_time) >= self.min_delay:
                for (x, y, radius) in np.uint16(np.around(circles[0, :])):
                    cv2.circle(frame, (x, y), radius, (0, 255, 0), 3)  
                    cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)       
                message = "Circle detected in frame"
                self.notify(message)
                movement = Movement(
                    timestamp=datetime.now(moscow_tz), 
                    description=message
                )
                self.repository.add_movement(movement)
                # Обновляем время последнего обнаружения
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
   - min_delay: минимальная задержка между детектированиями в секундах

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