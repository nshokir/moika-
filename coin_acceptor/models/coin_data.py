"""
Модели данных для работы с монетами
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class CoinEvent:
    """
    Класс для хранения события приема монеты
    """
    denomination: int      # Номинал монеты (1, 3, 5)
    timestamp: datetime    # Время события
    payout_duration: int   # Длительность срабатывания в секундах
    
    def __repr__(self) -> str:
        return f"CoinEvent(denomination={self.denomination}, time={self.timestamp.strftime('%H:%M:%S')}, duration={self.payout_duration}s)"


@dataclass
class DeviceStatus:
    """
    Класс для хранения статуса устройства
    """
    is_connected: bool     # Подключено ли устройство
    port: Optional[str]    # COM порт
    coin_1_count: int      # Количество монет номиналом 1
    coin_3_count: int      # Количество монет номиналом 3
    coin_5_count: int      # Количество монет номиналом 5
    total_coins: int       # Всего монет
    is_payout_active: bool # Активно ли срабатывание
    
    def __repr__(self) -> str:
        status_text = "🟢 Подключено" if self.is_connected else "🔴 Отключено"
        return (
            f"DeviceStatus({status_text} на {self.port})\n"
            f"Монеты: 1сом={self.coin_1_count}, 3сом={self.coin_3_count}, "
            f"5сом={self.coin_5_count} (Всего: {self.total_coins})"
        )
