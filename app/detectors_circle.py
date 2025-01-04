import cv2
import numpy as np
from observer.observer import Observer, Subject

class CircleDetector(Subject):
    def __init__(
            self, dp=0.5, min_dist=200, 
            param1=100, param2=150, 
            min_radius=70, max_radius=10000
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

    def process_frame(self, frame):
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
            for (x, y, radius) in np.uint16(np.around(circles[0, :])):
                # Рисуем окружность и центр
                cv2.circle(frame, (x, y), radius, (0, 255, 0), 3)  
                cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)       
            self.notify("Circle detected in frame")
        
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