from abc import ABC, abstractmethod
from datetime import datetime

class Movement:
    def __init__(self, timestamp: datetime, description: str):
        self.timestamp = timestamp
        self.description = description

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

# Создание глобального репозитория
global_repository = InMemoryMovementRepository()