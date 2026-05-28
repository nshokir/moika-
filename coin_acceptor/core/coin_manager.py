"""
Модуль для управления монетами и механизмом обратного срабатывания
"""
import threading
import time
from typing import Dict
from PyQt5.QtCore import QObject, pyqtSignal


class CoinManager(QObject):
    """
    Класс для управления монетами и механизмом срабатывания
    """
    
    # Сигналы
    coin_count_updated = pyqtSignal(dict)  # Обновление количества монет
    payout_status_changed = pyqtSignal(str, bool)  # (номинал, статус срабатывания)
    
    # Настройки для каждого номинала (номинал: время срабатывания в секундах)
    PAYOUT_TIMES = {
        1: 60,      # 1 сом - 1 минута
        3: 180,     # 3 сома - 3 минуты
        5: 300      # 5 сомов - 5 минут
    }
    
    def __init__(self, cctalk_handler):
        """
        Инициализация менеджера монет
        
        Args:
            cctalk_handler: Обработчик ccTalk протокола
        """
        super().__init__()
        self.cctalk_handler = cctalk_handler
        self.coin_counts = {1: 0, 3: 0, 5: 0}
        self.payout_threads = {}
        
        # Подключаем сигнал детектирования монеты
        self.cctalk_handler.coin_detected.connect(self.on_coin_detected)
    
    def on_coin_detected(self, denomination: int):
        """
        Обработчик события детектирования монеты
        
        Args:
            denomination: Номинал монеты (1, 3 или 5)
        """
        if denomination in self.coin_counts:
            # Увеличиваем счетчик
            self.coin_counts[denomination] += 1
            
            # Отправляем сигнал об обновлении
            self.coin_count_updated.emit(self.coin_counts.copy())
            
            # Запускаем механизм срабатывания
            self.trigger_payout(denomination)
    
    def trigger_payout(self, denomination: int):
        """
        Запустить механизм обратного срабатывания
        
        Args:
            denomination: Номинал монеты
        """
        # Если уже идет срабатывание для этого номинала, ничего не делаем
        if denomination in self.payout_threads and self.payout_threads[denomination].is_alive():
            return
        
        # Создаем новый поток для срабатывания
        payout_thread = threading.Thread(
            target=self._payout_worker,
            args=(denomination,),
            daemon=True
        )
        self.payout_threads[denomination] = payout_thread
        payout_thread.start()
    
    def _payout_worker(self, denomination: int):
        """
        Рабочая функция для управления механизмом срабатывания
        
        Args:
            denomination: Номинал монеты
        """
        try:
            payout_duration = self.PAYOUT_TIMES.get(denomination, 60)
            
            # Сигнал начала срабатывания
            self.payout_status_changed.emit(f"{denomination} сом", True)
            
            # Отправляем команду на устройство
            self._send_payout_command(denomination)
            
            # Ждем необходимое время
            time.sleep(payout_duration)
            
            # Отправляем команду остановки
            self._send_stop_command(denomination)
            
            # Сигнал окончания срабатывания
            self.payout_status_changed.emit(f"{denomination} сом", False)
            
        except Exception as e:
            self.payout_status_changed.emit(f"{denomination} сом", False)
    
    def _send_payout_command(self, denomination: int):
        """
        Отправить команду на срабатывание механизма
        
        Args:
            denomination: Номинал монеты
        """
        command_map = {
            1: bytes([0x10]),
            3: bytes([0x20]),
            5: bytes([0x30])
        }
        
        if denomination in command_map:
            self.cctalk_handler.send_command(command_map[denomination])
    
    def _send_stop_command(self, denomination: int):
        """
        Отправить команду на остановку механизма
        
        Args:
            denomination: Номинал монеты
        """
        self.cctalk_handler.send_command(bytes([0x00]))
    
    def get_coin_counts(self) -> Dict[int, int]:
        """
        Получить текущий счет монет
        
        Returns:
            Dict[int, int]: Словарь с количеством монет по номиналам
        """
        return self.coin_counts.copy()
    
    def reset_coin_counts(self):
        """Сбросить счетчики монет"""
        self.coin_counts = {1: 0, 3: 0, 5: 0}
        self.coin_count_updated.emit(self.coin_counts.copy())
