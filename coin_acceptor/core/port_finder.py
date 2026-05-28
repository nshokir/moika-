"""
Модуль для автоматического поиска COM портов
"""
import serial
import serial.tools.list_ports
from typing import Optional, List


class PortFinder:
    """Класс для поиска доступных COM портов"""
    
    @staticmethod
    def get_available_ports() -> List[str]:
        """
        Получить список доступных COM портов
        
        Returns:
            List[str]: Список портов (например, ['COM3', 'COM5'])
        """
        ports = []
        for port, desc, hwid in serial.tools.list_ports.comports():
            ports.append(port)
        return ports
    
    @staticmethod
    def find_cctalk_port() -> Optional[str]:
        """
        Автоматический поиск порта с ccTalk устройством
        Пытается подключиться к каждому доступному порту
        
        Returns:
            Optional[str]: Найденный порт или None
        """
        available_ports = PortFinder.get_available_ports()
        
        for port in available_ports:
            try:
                ser = serial.Serial(
                    port=port,
                    baudrate=9600,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=1
                )
                
                if ser.is_open:
                    ser.close()
                    return port
                    
            except (serial.SerialException, OSError):
                continue
        
        return None
    
    @staticmethod
    def test_port(port: str, baudrate: int = 9600) -> bool:
        """
        Проверить, открывается ли порт
        
        Args:
            port: Имя порта (например, 'COM3')
            baudrate: Скорость передачи
            
        Returns:
            bool: True если порт доступен, False иначе
        """
        try:
            ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=1
            )
            ser.close()
            return True
        except (serial.SerialException, OSError):
            return False
