from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from factory.video_factory import VideoStreamHandlerFactory
from starlette.responses import StreamingResponse  
from app.detectors_circle import CircleDetector
from observer.notifier import ConsoleNotifier
from repository.movement_repository import global_repository
from utils.decorators import LoggingDetectorDecorator, FilterDetectorDecorator
from loguru import logger
import cv2
import asyncio


app = FastAPI()

# Настройка логирования
logger.add("movement_repository.log", rotation="1 MB", level="INFO", backtrace=True, diagnose=True)
logger.add("app_errors.log", rotation="1 MB", level="ERROR")  # Файл для ошибок

# Обработчик ошибок для HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error occurred: {exc.detail}, Status code: {exc.status_code}, Path: {request.url.path}")
    return await request.app.default_exception_handler(request, exc)

# Обработчик ошибок для других исключений
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"An unexpected error occurred: {exc}, Path: {request.url.path}")
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

@app.get("/")
async def read_root():
    return {"message": "Motion CircleDetection API Maz"}

@app.get("/video_feed")
async def video_feed(stream_type: str = "Webcam", url: str = None):
    # Создание обработчика видеопотока через фабрику
    try:
        handler = VideoStreamHandlerFactory.create_handler(
            stream_type=stream_type, url=url
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    
    try:
        video = handler.get_stream()
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    # Инициализация детектора движения с глобальным репозиторием
    detector = CircleDetector(repository=global_repository)

    # Применение декораторов
    # detector = LoggingDetectorDecorator(detector)
    # detector = FilterDetectorDecorator(detector, keyword="Motion")
    
    # Инициализация наблюдателей
    console_notifier = ConsoleNotifier()
    detector.attach(console_notifier)

    async def frame_generator():
        try:
            while True:
                frame = await asyncio.to_thread(video.get_frame)  # Используем asyncio.to_thread для асинхронного вызова
                if frame is None:
                    break
                # Отображение кадра зеркально
                flipped_frame = cv2.flip(frame, 1)
                # Обработка кадра детектором
                processed_frame = await asyncio.to_thread(detector.process_frame, flipped_frame)
                ret, buffer = cv2.imencode('.jpg', processed_frame)
                if not ret:
                    continue
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' 
                       + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"Error during video processing: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        finally:
            await asyncio.to_thread(video.release)

    return StreamingResponse(
        frame_generator(), 
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/movements")
async def get_movements():
    movements = await asyncio.to_thread(global_repository.get_movements)
    print(f"Total movements found: {len(movements)}")  # Отладочный вывод
    return [
        {"timestamp": m.timestamp.isoformat(), 
         "description": m.description} for m in movements
    ]
        
"""
- VideoStream класс отвечает за подключение к видеопотоку.
- Маршрут /video_feed возвращает поток изображений, закодированных
 в JPEG, которые можно отображать на frontend        
- Теперь маршрут /video_feed принимает параметры stream_type и url, 
позволяя выбрать тип потока динамически.
- Observer Pattern используется для уведомления наблюдателей 
о событиях, таких как обнаружение движения.
- CircleDetector — субъект, который анализирует кадры и уведомляет 
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
- Паттерн Decorator позволяет динамически добавлять новые обязанности 
объектам. В нашем случае, мы можем использовать его для добавления 
дополнительных функций к детектору движения, например, логирование 
или фильтрацию событ.
- LoggingDetectorDecorator добавляет логирование при обработке 
каждого кадра.
- FilterDetectorDecorator добавляет фильтрацию событий по 
ключевому слову.







"""