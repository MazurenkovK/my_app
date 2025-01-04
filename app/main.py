from fastapi import FastAPI
from factory.video_factory import VideoStreamHandlerFactory
from starlette.responses import StreamingResponse  # Импортируем StreamingResponse
from app.detectors_circle import CircleDetector
from observer.notifier import ConsoleNotifier
from repository.movement_repository import global_repository
import cv2

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Motion Detection API Maz"}

@app.get("/video_feed")
def video_feed(stream_type: str = "Webcam", url: str = None):
    # Создание обработчика видеопотока через фабрику
    handler = VideoStreamHandlerFactory.create_handler(stream_type=stream_type, url=url)
    video = handler.get_stream()

    # Инициализация репозитория движений
    #repository = InMemoryMovementRepository()

    # Инициализация детектора движения
    detector = CircleDetector(repository=global_repository)
    notifier = ConsoleNotifier()
    detector.attach(notifier)

    def frame_generator():
        try:
            while True:
                frame = video.get_frame()
                if frame is None:
                    break
                # Отображение кадра зеркально
                flipped_frame = cv2.flip(frame, 1)  # 1 — зеркальное отображение по вертикали                
                # Обработка кадра детектором кругов
                processed_frame = detector.process_frame(flipped_frame)
                ret, buffer = cv2.imencode('.jpg', processed_frame)
                if not ret:
                    continue
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"Error during video processing: {e}")
            #raise HTTPException(status_code=500, detail="Internal Server Error")
        finally:
            video.release()

    return StreamingResponse(
        frame_generator(), 
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/movements")
def get_movements():
    #repository = InMemoryMovementRepository()
    movements = global_repository.get_movements()
    return [{"timestamp": m.timestamp.isoformat(), "description": m.description} for m in movements] 
        
"""
- VideoStream класс отвечает за подключение к видеопотоку.
- Маршрут /video_feed возвращает поток изображений, закодированных
 в JPEG, которые можно отображать на frontend        
- Теперь маршрут /video_feed принимает параметры stream_type и url, 
позволяя выбрать тип потока динамически.
- Observer Pattern используется для уведомления наблюдателей 
о событиях, таких как обнаружение движения.
- MotionDetector — субъект, который анализирует кадры и уведомляет 
наблюдателей при обнаружении движения.
- ConsoleNotifier — наблюдатель, который выводит уведомления в консоль.
- Паттерн Repository используется для хранения и управления 
данными о детектированных движениях. Это позволяет легко менять способ 
хранения данных (например, из памяти на базу данных) без изменения 
бизнес-логики.
- MovementRepository — абстрактный класс, 
InMemoryMovementRepository — конкретная реализация, хранящая 
данные в памяти. 
- В CircleDetector добавляется ссылка на репозиторий для сохранения 
информации о движениях.
- Добавлен маршрут /movements для получения списка всех 
детектированных движений.






"""