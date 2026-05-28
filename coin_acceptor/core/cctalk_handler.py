"""
Модуль для работы с ccTalk протоколом
"""
import serial
import threading
import time
from typing import Callable, Optional
from PyQt5.QtCore import QThread, pyqtSignal


class CCTalkHandler(QThread):
    """
    Класс для обработки ccTalk протокола в отдельном потоке
    """
    
    # Сигналы
    coin_detected = pyqtSignal(int)  # Номинал монеты
    connection_status_changed = pyqtSignal(bool)  # Статус подключения
    error_occurred = pyqtSignal(str)  # Ошибка
    
    def __init__(self, port: str, baudrate: int = 9600):
        """
        Инициализация обработчика ccTalk
        
        Args:
            port: COM порт (например, 'COM3')
            baudrate: Скорость передачи (по умолчанию 9600)
        """
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.serial_port = None
        self.is_running = False
        self.is_connected = False
    
    def connect(self) -> bool:
        """
        Подключиться к устройству
        
        Returns:
            bool: True если успешно подключено, False иначе
        """
        try:
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            self.is_connected = True
            self.connection_status_changed.emit(True)
            return True
        except serial.SerialException as e:
            self.error_occurred.emit(f"Ошибка подключения: {str(e)}")
            self.is_connected = False
            self.connection_status_changed.emit(False)
            return False
    
    def disconnect(self):
        """Отключиться от устройства"""
        self.is_running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.is_connected = False
        self.connection_status_changed.emit(False)
    
    def run(self):
        """Основной цикл чтения данных из устройства"""
        if not self.connect():
            return
        
        self.is_running = True
        
        while self.is_running:
            try:
                if self.serial_port and self.serial_port.in_waiting > 0:
                    data = self.serial_port.read()
                    self.process_data(data)
                time.sleep(0.1)
            except Exception as e:
                self.error_occurred.emit(f"Ошибка чтения: {str(e)}")
                break
        
        self.disconnect()
    
    def process_data(self, data: bytes):
        """
        Обработать полученные данные из ccTalk устройства
        
        Args:
            data: Полученные байты
        """
        if len(data) > 0:
            byte_value = data[0]
            
            if byte_value == 0x01:
                self.coin_detected.emit(1)
            elif byte_value == 0x03:
                self.coin_detected.emit(3)
            elif byte_value == 0x05:
                self.coin_detected.emit(5)
    
    def send_command(self, command: bytes) -> bool:
        """
        Отправить команду на устройство
        
        Args:
            command: Команда в виде байтов
            
        Returns:
            bool: True если успешно отправлено
        """
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.write(command)
                return True
            return False
        except serial.SerialException as e:
            self.error_occurred.emit(f"Ошибка отправки: {str(e)}")
            return False
