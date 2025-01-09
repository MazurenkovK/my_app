import pytest
from fastapi.testclient import TestClient
from app.main import app, global_repository
from app.factory.video_factory import VideoStreamHandlerFactory
from app.repository.movement_repository import Movement
from unittest.mock import patch, MagicMock
from datetime import datetime
import cv2 

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