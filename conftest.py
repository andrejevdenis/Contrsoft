import socket
import threading
import time
import pytest

class MockTcpServer:
    """Управляемый Mock-сервер для эмуляции внешнего симулятора сигналов."""
    def __init__(self, host='127.0.0.1', port=2001):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client_conn = None
        self.is_running = False
        self.thread = None

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.is_running = True
        
        def accept_loop():
            try:
                self.server_socket.settimeout(1.0)
                while self.is_running:
                    try:
                        self.client_conn, _ = self.server_socket.accept()
                        break
                    except socket.timeout:
                        continue
            except Exception:
                pass

        self.thread = threading.Thread(target=accept_loop, daemon=True)
        self.thread.start()

    def stop_and_drop_client(self):
        """Принудительный разрыв связи с клиентом (эмуляция падения процесса)."""
        self.is_running = False
        if self.client_conn:
            try:
                self.client_conn.shutdown(socket.SHUT_RDWR)
                self.client_conn.close()
            except IOError:
                pass
        try:
            self.server_socket.close()
        except IOError:
            pass


@pytest.fixture
def mock_signal_server():
    """Фикстура pytest, которая автоматически поднимает и тушит сервер для теста."""
    server = MockTcpServer()
    server.start()
    time.sleep(0.1)  # Даем микропаузу для старта сокета
    
    yield server     # Здесь выполняется сам тест
    
    server.stop_and_drop_client()  # Teardown: гарантированное очищение портов после теста