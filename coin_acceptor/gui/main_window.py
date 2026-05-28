"""
Главное окно приложения для приема монет
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QStatusBar, QGroupBox, QLCDNumber, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer
from PyQt5.QtGui import QFont, QColor, QPixmap
from core.port_finder import PortFinder
from core.cctalk_handler import CCTalkHandler
from core.coin_manager import CoinManager


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Приемник монет - ccTalk (1, 3, 5 сомов)")
        self.setGeometry(100, 100, 600, 500)
        
        # Переменные состояния
        self.cctalk_handler = None
        self.coin_manager = None
        self.port = None
        
        # Инициализация UI
        self.init_ui()
        
        # Попытка подключиться при запуске
        QTimer.singleShot(500, self.auto_connect)
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # === Секция статуса подключения ===
        connection_group = QGroupBox("Статус подключения")
        connection_layout = QHBoxLayout()
        
        self.status_label = QLabel("🔴 Отключено")
        self.status_label.setFont(QFont("Arial", 12, QFont.Bold))
        connection_layout.addWidget(self.status_label)
        
        self.port_label = QLabel("Порт: -")
        self.port_label.setFont(QFont("Arial", 10))
        connection_layout.addWidget(self.port_label)
        
        connection_layout.addStretch()
        connection_group.setLayout(connection_layout)
        main_layout.addWidget(connection_group)
        
        # === Секция счетчиков монет ===
        coins_group = QGroupBox("Количество принятых монет")
        coins_layout = QHBoxLayout()
        
        # 1 сом
        coin1_layout = QVBoxLayout()
        label1 = QLabel("1 сом")
        label1.setFont(QFont("Arial", 10, QFont.Bold))
        self.lcd1 = QLCDNumber(3)
        self.lcd1.setSegmentStyle(QLCDNumber.Flat)
        self.lcd1.display(0)
        coin1_layout.addWidget(label1)
        coin1_layout.addWidget(self.lcd1)
        coins_layout.addLayout(coin1_layout)
        
        # 3 сома
        coin3_layout = QVBoxLayout()
        label3 = QLabel("3 сома")
        label3.setFont(QFont("Arial", 10, QFont.Bold))
        self.lcd3 = QLCDNumber(3)
        self.lcd3.setSegmentStyle(QLCDNumber.Flat)
        self.lcd3.display(0)
        coin3_layout.addWidget(label3)
        coin3_layout.addWidget(self.lcd3)
        coins_layout.addLayout(coin3_layout)
        
        # 5 сомов
        coin5_layout = QVBoxLayout()
        label5 = QLabel("5 сомов")
        label5.setFont(QFont("Arial", 10, QFont.Bold))
        self.lcd5 = QLCDNumber(3)
        self.lcd5.setSegmentStyle(QLCDNumber.Flat)
        self.lcd5.display(0)
        coin5_layout.addWidget(label5)
        coin5_layout.addWidget(self.lcd5)
        coins_layout.addLayout(coin5_layout)
        
        coins_group.setLayout(coins_layout)
        main_layout.addWidget(coins_group)
        
        # === Секция статуса срабатывания ===
        payout_group = QGroupBox("Статус срабатывания механизма")
        payout_layout = QVBoxLayout()
        
        self.payout_status_label = QLabel("Ожидание монет...")
        self.payout_status_label.setFont(QFont("Arial", 11))
        self.payout_status_label.setStyleSheet("color: gray;")
        payout_layout.addWidget(self.payout_status_label)
        
        payout_group.setLayout(payout_layout)
        main_layout.addWidget(payout_group)
        
        # === Кнопки управления ===
        buttons_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton("Подключиться")
        self.connect_btn.clicked.connect(self.on_connect_clicked)
        buttons_layout.addWidget(self.connect_btn)
        
        self.disconnect_btn = QPushButton("Отключиться")
        self.disconnect_btn.clicked.connect(self.on_disconnect_clicked)
        self.disconnect_btn.setEnabled(False)
        buttons_layout.addWidget(self.disconnect_btn)
        
        self.reset_btn = QPushButton("Сбросить счетчики")
        self.reset_btn.clicked.connect(self.on_reset_clicked)
        self.reset_btn.setEnabled(False)
        buttons_layout.addWidget(self.reset_btn)
        
        main_layout.addLayout(buttons_layout)
        
        main_layout.addStretch()
        
        central_widget.setLayout(main_layout)
        
        # Строка статуса
        self.statusBar().showMessage("Готово")
    
    def auto_connect(self):
        """Автоматическое подключение при запуске"""
        self.statusBar().showMessage("Поиск устройства...")
        
        # Ищем порт
        port = PortFinder.find_cctalk_port()
        
        if port:
            self.port = port
            self.init_handlers()
            self.cctalk_handler.start()
        else:
            available_ports = PortFinder.get_available_ports()
            if available_ports:
                self.statusBar().showMessage(f"Устройство не найдено. Доступные порты: {', '.join(available_ports)}")
                QMessageBox.information(
                    self,
                    "Предупреждение",
                    f"Устройство не найдено.\n\nДоступные порты: {', '.join(available_ports)}\n\nПроверьте подключение и попробуйте вручную выбрать порт."
                )
            else:
                self.statusBar().showMessage("Нет доступных портов")
                QMessageBox.warning(self, "Ошибка", "Нет доступных COM портов")
    
    def init_handlers(self):
        """Инициализация обработчиков"""
        self.cctalk_handler = CCTalkHandler(self.port)
        self.coin_manager = CoinManager(self.cctalk_handler)
        
        # Подключаем сигналы
        self.cctalk_handler.connection_status_changed.connect(self.on_connection_status_changed)
        self.cctalk_handler.error_occurred.connect(self.on_error_occurred)
        self.coin_manager.coin_count_updated.connect(self.on_coin_count_updated)
        self.coin_manager.payout_status_changed.connect(self.on_payout_status_changed)
    
    @pyqtSlot()
    def on_connect_clicked(self):
        """Обработчик нажатия кнопки подключения"""
        if not self.port:
            port = PortFinder.find_cctalk_port()
            if not port:
                QMessageBox.warning(self, "Ошибка", "Устройство не найдено")
                return
            self.port = port
        
        self.init_handlers()
        self.cctalk_handler.start()
    
    @pyqtSlot()
    def on_disconnect_clicked(self):
        """Обработчик нажатия кнопки отключения"""
        if self.cctalk_handler:
            self.cctalk_handler.disconnect()
    
    @pyqtSlot()
    def on_reset_clicked(self):
        """Обработчик нажатия кнопки сброса счетчиков"""
        if self.coin_manager:
            self.coin_manager.reset_coin_counts()
            self.statusBar().showMessage("Счетчики сброшены")
    
    @pyqtSlot(bool)
    def on_connection_status_changed(self, connected: bool):
        """Обработчик изменения статуса подключения"""
        if connected:
            self.status_label.setText(f"🟢 Подключено ({self.port})")
            self.port_label.setText(f"Порт: {self.port}")
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.reset_btn.setEnabled(True)
            self.statusBar().showMessage(f"Подключено на порту {self.port}")
        else:
            self.status_label.setText("🔴 Отключено")
            self.port_label.setText("Порт: -")
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            self.reset_btn.setEnabled(False)
            self.statusBar().showMessage("Отключено")
    
    @pyqtSlot(str)
    def on_error_occurred(self, error_msg: str):
        """Обработчик ошибок"""
        QMessageBox.critical(self, "Ошибка", error_msg)
        self.statusBar().showMessage(f"Ошибка: {error_msg}")
    
    @pyqtSlot(dict)
    def on_coin_count_updated(self, counts: dict):
        """Обработчик обновления счетчиков монет"""
        self.lcd1.display(counts.get(1, 0))
        self.lcd3.display(counts.get(3, 0))
        self.lcd5.display(counts.get(5, 0))
    
    @pyqtSlot(str, bool)
    def on_payout_status_changed(self, denomination: str, is_active: bool):
        """Обработчик изменения статуса срабатывания"""
        if is_active:
            self.payout_status_label.setText(f"⏱️ Срабатывание: {denomination}")
            self.payout_status_label.setStyleSheet("color: red; font-weight: bold;")
            self.statusBar().showMessage(f"Срабатывание механизма: {denomination}")
        else:
            self.payout_status_label.setText("✓ Ожидание монет...")
            self.payout_status_label.setStyleSheet("color: green;")
            self.statusBar().showMessage("Готово")
    
    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        if self.cctalk_handler:
            self.cctalk_handler.disconnect()
        event.accept()
