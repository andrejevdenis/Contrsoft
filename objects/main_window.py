import threading
from PyQt6.QtWidgets import QMainWindow, QPushButton, QTableWidget, QVBoxLayout, QWidget, QLabel
from objects.network_worker import NetworkWorker

class MainWindow(QMainWindow):
    """Класс отвечает исключительно за отображение UI и координацию потоков."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Signal Monitor")
        self._init_ui()
        self.worker = None
        self.network_thread = None

    def _init_ui(self):
        """Инициализация компонентов интерфейса (Инкапсуляция UI)."""
        self.btn_connect = QPushButton("Подключиться")
        self.lbl_status = QLabel("Отключено")
        self.table = QTableWidget(10, 5)
        
        layout = QVBoxLayout()
        layout.addWidget(self.btn_connect)
        layout.addWidget(self.lbl_status)
        layout.addWidget(self.table)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        self.btn_connect.clicked.connect(self.start_connection)

    def start_connection(self):
        """Инициализирует и запускает фоновый поток сетевого рабочего."""
        self.lbl_status.setText("Подключение...")
        self.worker = NetworkWorker()
        self.worker.status_changed.connect(self.lbl_status.setText)
        
        # Разделение потоков: UI остается отзывчивым
        self.network_thread = threading.Thread(target=self.worker.connect_and_listen, daemon=True)
        self.network_thread.start()

    def closeEvent(self, event):
        """Переопределение закрытия окна для корректного выхода из потоков."""
        if self.worker:
            self.worker.cleanup()
        super().closeEvent(event)