import pytest
from fastapi.testclient import TestClient
from app.main import app, global_repository
from app.factory.video_factory import VideoStreamHandlerFactory
from app.repository.movement_repository import Movement, InMemoryMovementRepository
from app.detectors.circle_detector import CircleDetector
from unittest.mock import patch, MagicMock
from datetime import datetime
import cv2 
import numpy as np

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_repository():
    global_repository.clear_movements()

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Motion CircleDetection API Maz"}

def test_video_feed_invalid_stream_type():
    response = client.get("/video_feed?stream_type=InvalidType")
    assert response.status_code == 400
    assert response.json() == {"detail": "Unknown stream type"}

def test_video_feed_valid_stream_type():
    with patch.object(VideoStreamHandlerFactory, 'create_handler', 
                      return_value=MagicMock()) as mock_handler:
        mock_handler.return_value.get_stream.return_value.get_frame = MagicMock(
            return_value=cv2.imread('test_image.jpg')
            )
        response = client.get("/video_feed?stream_type=Webcam")
        assert response.status_code == 200
        assert response.headers["content-type"] == "multipart/x-mixed-replace; boundary=frame"

def test_get_movements_empty():
    response = client.get("/movements")
    assert response.status_code == 200
    assert response.json() == []

def test_get_movements_with_data():
    movement = Movement(timestamp=datetime.fromisoformat(
        "2023-10-01T12:00:00"), description="Test Movement"
        )
    global_repository.add_movement(movement)
    response = client.get("/movements")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["description"] == "Test Movement"


@pytest.fixture
def circle_detector():
    repository = InMemoryMovementRepository()
    detector = CircleDetector(repository=repository)
    return detector

def test_circle_detector_initialization(circle_detector):
    assert circle_detector.repository is not None

def test_circle_detector_process_frame(circle_detector: CircleDetector):
    # Создаем мок для кадра
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.circle(gray_frame, (320, 240), 50, (255, 255, 255), 2)
    
    with patch('cv2.HoughCircles', return_value=np.array([[[320, 240, 50]]])):
        processed_frame = circle_detector.process_frame(frame)
        assert processed_frame is not None

def test_circle_detector_no_circles_detected(circle_detector):
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    with patch('cv2.HoughCircles', return_value=None):
        processed_frame = circle_detector.process_frame(frame)
        assert processed_frame is not None
        assert not circle_detector.is_saving

"""
Описание тестов:

 client = TestClient(app):
- Эта строка создает экземпляр TestClient для приложения FastAPI, 
  которое указано в app.
- TestClient предоставляет удобный интерфейс для тестирования API, 
позволяя отправлять HTTP-запросы к различным эндпоинтам приложения 
и получать ответы, что облегчает проверку поведения API в тестах.

 @pytest.fixture(autouse=True):
- Декоратор @pytest.fixture определяет функцию, которая будет служить 
фикстурой для тестов. Фикстуры — это функции, которые позволяют 
инициализировать какие-либо ресурсы или устанавливать контекст 
для выполнения тестов.
- Параметр autouse=True указывает, что данная фикстура будет 
автоматически применяться ко всем тестам в модуле, в котором 
она определена, без необходимости явно указывать ее в каждом тесте.

 def clear_repository()::
- Это определение функции фикстуры. Функция clear_repository 
вызывается перед каждым тестом.
- Она очищает репозиторий движений, вызывая метод clear_movements() 
глобального репозитория (global_repository), что позволяет делать 
каждый тест независимым и гарантирует, что состояние репозитория 
не будет влиять на результаты тестов. 

Таким образом, в целом этот код отвечает за инициализацию тестового 
клиента и обеспечение того, чтобы перед каждым тестом 
репозиторий движений очищался.

1. test_read_root: 
- Этот тест проверяет, что корневой маршрут (/) API возвращает 
  правильный ответ.
- Он отправляет GET-запрос на корневой маршрут и проверяет, 
что код состояния ответа равен 200. Также он проверяет, 
что JSON-ответ 
совпадает с ожидаемым значением {"message": "Motion CircleDetection API Maz"}.

2. test_video_feed_invalid_stream_type:
- Этот тест проверяет обработку некорректного типа потока видео.
- Он отправляет GET-запрос на маршрут /video_feed с параметром stream_type, 
установленным в значение InvalidType. Ожидается, что ответ будет иметь 
код состояния 400 и JSON-ответ будет содержать сообщение об 
ошибке {"detail": "Unknown stream type"}.

3. test_video_feed_valid_stream_type:
- Этот тест проверяет работу с корректным типом потока видео (Webcam).
- Он использует unittest.mock.patch для подмены метода создания обработчика 
потоков. Возвращается мок-объект, который возвращает тестовое изображение 
при вызове get_frame.
- Затем он отправляет GET-запрос на /video_feed с параметром stream_type=Webcam 
и проверяет, что ответ имеет код состояния 200 и заголовок content-type 
равен "multipart/x-mixed-replace; boundary=frame".

4. test_get_movements_empty:
- Этот тест проверяет эндпоинт для получения движений (/movements) в случае, 
если движений еще нет.
- Он отправляет GET-запрос и проверяет, что ответ имеет код состояния 200 
и возвращает пустой список.

5. test_get_movements_with_data:
- Этот тест проверяет эндпоинт для получения движений, когда в репозитории 
действительно есть данные.
- Сначала создается объект Movement с временной меткой и описанием, 
который добавляется в глобальный репозиторий. Затем выполняется GET-запрос 
на /movements, и проверяется, что ответ имеет код состояния 200, 
длина списка движений равна 1, и описание первого движения совпадает 
с ожидаемым значением "Test Movement".

6. circle_detector (фикстура):
- Эта фикстура создает экземпляр CircleDetector с использованием 
InMemoryMovementRepository как репозиторий для движения.
- Она автоматически используется перед каждым тестом, 
который ее запрашивает, благодаря параметру autouse=True.

7. test_circle_detector_initialization:
- Этот тест проверяет, что инициализация CircleDetector проходит 
успешно и репозиторий не является нулевым.
- Он просто проверяет, что поле repository 
в объекте circle_detector не равно None.

8. test_circle_detector_process_frame:
- Тест проверяет, как CircleDetector обрабатывает кадры.
- Создается черный кадр и рисуется белый круг на нем. Затем используется 
мок для функции cv2.HoughCircles, который возвращает координаты круга.
- Метод process_frame вызывается для обработки кадра, и проверяется, 
что выходные данные не равны None.

9. test_circle_detector_no_circles_detected:
- Этот тест проверяет, что происходит, когда на кадре нет кругов.
- Создается черный кадр без кругов, и при вызове функции cv2.HoughCircles 
одменяется, чтобы она вернула None.
- Вызов метода process_frame также должен вернуть результат, проверяется, 
что он не равен None, и флаг is_saving в circle_detector должен быть False, 
указывая на то, что нет обнаруженных кругов.
"""