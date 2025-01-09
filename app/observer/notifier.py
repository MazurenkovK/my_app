from app.observer.observer import Observer

class ConsoleNotifier(Observer):
    def update(self, message: str):
        #print(f"Notifier: {message}")
        pass