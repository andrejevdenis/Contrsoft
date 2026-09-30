import socket
import threading
from PyQt6.QtCore import QObject, pyqtSignal

class NetworkWorker(QObject):
    """Класс отвечает исключительно за сетевое взаимодействие через TCP-сокет."""
    data_received = pyqtSignal(str)
    status_changed = pyqtSignal(str)

    def __init__(self, host='127.0.0.1', port=2001):
        super().__init__()
        self.host = host
        self.port = port
        self.running = False
        self.client_socket = None

    def connect_and_listen(self):
        """Устанавливает соединение и слушает сокет в бесконечном цикле."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(2.0)  # Таймаут, чтобы поток не зависал при закрытии
            self.client_socket.connect((self.host, self.port))
            self.status_changed.emit("Подключено")
            self.running = True
            
            while self.running:
                try:
                    data = self.client_socket.recv(1024).decode('utf-8')
                    if not data:  # Сервер разорвал соединение
                        break
                    self.data_received.emit(data)
                except socket.timeout:
                    continue
        except Exception as e:
            self.status_changed.emit(f"Ошибка: {str(e)}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Безопасное закрытие ресурсов сокета."""
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except IOError:
                pass
        self.status_changed.emit("Отключено")