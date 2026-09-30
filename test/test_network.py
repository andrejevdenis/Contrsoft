import pytest
from PyQt6.QtCore import Qt
from objects.main_window import MainWindow

def test_ui_remains_responsive_on_network_drop(qtbot, mock_signal_server):
    """
    Критический сценарий: Проверка устойчивости UI при падении TCP-канала.
    Убеждаемся, что при обрыве связи интерфейс не «вешается» и реагирует на действия.
    """
    # 1. Arrange: Создаем инстанс главного окна приложения и регистрируем в qtbot
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()

    # 2. Act: Эмулируем нажатие пользователем кнопки «Подключиться»
    qtbot.mouseClick(window.btn_connect, Qt.MouseButton.LeftButton)

    # Ожидаем успешную установку соединения с фикстурным сервером
    qtbot.waitUntil(lambda: window.lbl_status.text() == "Подключено", timeout=2000)
    assert window.lbl_status.text() == "Подключено", "Приложение не смогло подключиться к серверу."

    # 3. Act: Убиваем соединение на стороне сервера (эмуляция аварии симулятора)
    mock_signal_server.stop_and_drop_client()

    # Ожидаем, пока фоновый поток приложения считает обрыв и обновит статус в UI
    qtbot.waitUntil(lambda: window.lbl_status.text() == "Отключено", timeout=3000)
    
    # 4. Assert: Проверяем отзывчивость UI после падения сети
    # Пытаемся кликнуть по кнопке заново. Если бы поток UI завис, qtbot упал бы по таймауту.
    qtbot.mouseClick(window.btn_connect, Qt.MouseButton.LeftButton)
    
    # Интерфейс должен оставаться активным, а статус уйти на попытку переподключения или ошибку сокета
    assert window.isEnabled() is True, "Критическая ошибка: Интерфейс приложения заблокирован сетевым потоком!"
    assert "Ошибка" in window.lbl_status.text() or window.lbl_status.text() == "Подключение..."