import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
import os
from datetime import datetime
import threading
import inputs

# Загрузка DLL библиотеки
try:
    dll_path = os.path.join(os.path.dirname(__file__), 'usb_relay_device.dll')
    usb_relay_dll = ctypes.CDLL(dll_path)
except Exception as e:
    messagebox.showerror("Error", f"Failed to load DLL: {e}")
    usb_relay_dll = None

# Константы
USB_RELAY_DEVICE_ONE_CHANNEL = 1
USB_RELAY_DEVICE_TWO_CHANNEL = 2
USB_RELAY_DEVICE_FOUR_CHANNEL = 4
USB_RELAY_DEVICE_EIGHT_CHANNEL = 8

# Структура для информации об устройстве
class USBRelayDeviceInfo(ctypes.Structure):
    pass

USBRelayDeviceInfo._fields_ = [
    ("serial_number", ctypes.c_char_p),
    ("device_path", ctypes.c_char_p),
    ("device_type", ctypes.c_int),
    ("next", ctypes.POINTER(USBRelayDeviceInfo))
]

# Функции из DLL
if usb_relay_dll:
    usb_relay_init = usb_relay_dll.usb_relay_init
    usb_relay_exit = usb_relay_dll.usb_relay_exit
    usb_relay_device_enumerate = usb_relay_dll.usb_relay_device_enumerate
    usb_relay_device_free_enumerate = usb_relay_dll.usb_relay_device_free_enumerate
    usb_relay_device_open_with_serial_number = usb_relay_dll.usb_relay_device_open_with_serial_number
    usb_relay_device_close = usb_relay_dll.usb_relay_device_close
    usb_relay_device_open_one_relay_channel = usb_relay_dll.usb_relay_device_open_one_relay_channel
    usb_relay_device_close_one_relay_channel = usb_relay_dll.usb_relay_device_close_one_relay_channel
    usb_relay_device_open_all_relay_channel = usb_relay_dll.usb_relay_device_open_all_relay_channel
    usb_relay_device_close_all_relay_channel = usb_relay_dll.usb_relay_device_close_all_relay_channel
    usb_relay_device_get_status = usb_relay_dll.usb_relay_device_get_status

    # Установка типов аргументов и возвращаемых значений
    usb_relay_init.argtypes = []
    usb_relay_init.restype = ctypes.c_int

    usb_relay_exit.argtypes = []
    usb_relay_exit.restype = ctypes.c_int

    usb_relay_device_enumerate.argtypes = []
    usb_relay_device_enumerate.restype = ctypes.POINTER(USBRelayDeviceInfo)

    usb_relay_device_free_enumerate.argtypes = [ctypes.POINTER(USBRelayDeviceInfo)]
    usb_relay_device_free_enumerate.restype = None

    usb_relay_device_open_with_serial_number.argtypes = [ctypes.c_char_p, ctypes.c_uint]
    usb_relay_device_open_with_serial_number.restype = ctypes.c_int

    usb_relay_device_close.argtypes = [ctypes.c_int]
    usb_relay_device_close.restype = None

    usb_relay_device_open_one_relay_channel.argtypes = [ctypes.c_int, ctypes.c_int]
    usb_relay_device_open_one_relay_channel.restype = ctypes.c_int

    usb_relay_device_close_one_relay_channel.argtypes = [ctypes.c_int, ctypes.c_int]
    usb_relay_device_close_one_relay_channel.restype = ctypes.c_int

    usb_relay_device_open_all_relay_channel.argtypes = [ctypes.c_int]
    usb_relay_device_open_all_relay_channel.restype = ctypes.c_int

    usb_relay_device_close_all_relay_channel.argtypes = [ctypes.c_int]
    usb_relay_device_close_all_relay_channel.restype = ctypes.c_int

    usb_relay_device_get_status.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_uint)]
    usb_relay_device_get_status.restype = ctypes.c_int


class USBRelayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("USB Relay Manager - Joystick Control")
        self.root.geometry("550x800")
        self.root.resizable(False, False)
        
        self.device_handle = -1
        self.device_opened = False
        self.devices = []
        self.relay_states = [False] * 8
        
        # Джойстик
        self.joystick_thread = None
        self.joystick_running = True
        self.joystick_name = "Not found"
        
        # Инициализация библиотеки
        if usb_relay_dll:
            result = usb_relay_init()
            if result != 0:
                messagebox.showerror("Error", "Failed to initialize USB Relay library")
        
        self.setup_ui()
        
        # Автоматический поиск и открытие устройства
        self.root.after(500, self.auto_find_and_open_device)
        
        # Запуск потока для джойстика
        self.joystick_thread = threading.Thread(target=self.joystick_listener, daemon=True)
        self.joystick_thread.start()
    
    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== Верхняя часть: поиск устройства =====
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(top_frame, text="Find device", command=self.find_device).pack(side=tk.LEFT, padx=5)
        
        self.device_combo = ttk.Combobox(top_frame, state="readonly", width=30)
        self.device_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # ===== Статус =====
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Status: Not connected", font=("Arial", 10, "bold"))
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # ===== Статус джойстика =====
        joystick_frame = ttk.Frame(main_frame)
        joystick_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(joystick_frame, text="Joystick:", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        self.joystick_label = ttk.Label(joystick_frame, text="Not found", font=("Arial", 9, "bold"), foreground="red")
        self.joystick_label.pack(side=tk.LEFT, padx=5)
        
        # ===== Кнопки открытия/закрытия устройства =====
        device_buttons_frame = ttk.Frame(main_frame)
        device_buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(device_buttons_frame, text="open device", command=self.open_device).pack(side=tk.LEFT, padx=5)
        
        self.device_status_btn = tk.Button(device_buttons_frame, bg="red", width=15, height=2)
        self.device_status_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(device_buttons_frame, text="close device", command=self.close_device).pack(side=tk.LEFT, padx=5)
        
        # ===== Релеи =====
        relays_frame = ttk.LabelFrame(main_frame, text="Relays", padding="10")
        relays_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.relay_status_btns = []
        
        for i in range(1, 9):
            relay_row = ttk.Frame(relays_frame)
            relay_row.pack(fill=tk.X, pady=5)
            
            ttk.Label(relay_row, text=f"Relay {i}", width=10).pack(side=tk.LEFT)
            ttk.Button(relay_row, text="open", width=8, 
                      command=lambda ch=i: self.set_relay_state(ch, True)).pack(side=tk.LEFT, padx=3)
            
            status_btn = tk.Button(relay_row, bg="red", width=8, height=2)
            status_btn.pack(side=tk.LEFT, padx=3)
            self.relay_status_btns.append(status_btn)
            
            ttk.Button(relay_row, text="close", width=8,
                      command=lambda ch=i: self.set_relay_state(ch, False)).pack(side=tk.LEFT, padx=3)
        
        # ===== Кнопки Open All / Close All =====
        all_buttons_frame = ttk.Frame(main_frame)
        all_buttons_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(all_buttons_frame, text="Open All", command=self.open_all).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(all_buttons_frame, text="Close All", command=self.close_all).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # ===== Лог =====
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(log_frame, height=6, yscrollcommand=scrollbar.set)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def auto_find_and_open_device(self):
        """Автоматически находит и открывает первое найденное устройство"""
        self.find_device()
        if self.devices:
            self.device_combo.current(0)
            self.open_device()
    
    def find_device(self):
        if not usb_relay_dll:
            messagebox.showerror("Error", "DLL not loaded")
            return
        
        self.devices = []
        self.device_combo.set("")
        self.device_combo['values'] = []
        
        p_device_info = usb_relay_device_enumerate()
        
        if not p_device_info:
            self.log("No USB Relay devices found")
            return
        
        p_current = p_device_info
        device_count = 0
        
        while p_current:
            serial = p_current.contents.serial_number.decode('utf-8')
            device_type = p_current.contents.device_type
            self.devices.append(serial)
            self.log(f"Found device: {serial} (Type: {device_type} channels)")
            device_count += 1
            p_current = p_current.contents.next
        
        usb_relay_device_free_enumerate(p_device_info)
        
        self.device_combo['values'] = self.devices
        if self.devices:
            self.device_combo.current(0)
        
        self.log(f"Total devices found: {device_count}")
    
    def open_device(self):
        if not usb_relay_dll:
            messagebox.showerror("Error", "DLL not loaded")
            return
        
        if not self.device_combo.get():
            messagebox.showwarning("Warning", "Select a device first")
            return
        
        if self.device_opened:
            usb_relay_device_close(self.device_handle)
        
        serial_number = self.device_combo.get()
        serial_bytes = serial_number.encode('utf-8')
        
        result = usb_relay_device_open_with_serial_number(serial_bytes, len(serial_bytes))
        
        if result > 0:
            self.device_handle = result
            self.device_opened = True
            self.device_status_btn.config(bg="green")
            self.status_label.config(text=f"Status: Connected - {serial_number}")
            self.log(f"Device opened successfully. Handle: {self.device_handle}")
            self.update_relay_status()
        else:
            messagebox.showerror("Error", "Failed to open device")
            self.log("ERROR: Failed to open device")
    
    def close_device(self):
        if self.device_opened:
            usb_relay_device_close(self.device_handle)
            self.device_opened = False
            self.device_status_btn.config(bg="red")
            self.status_label.config(text="Status: Not connected")
            self.log("Device closed")
            self.relay_states = [False] * 8
            self.update_relay_display()
    
    def set_relay_state(self, channel, state):
        if not self.device_opened:
            messagebox.showwarning("Warning", "Device not opened")
            return
        
        if state:
            result = usb_relay_device_open_one_relay_channel(self.device_handle, channel)
        else:
            result = usb_relay_device_close_one_relay_channel(self.device_handle, channel)
        
        if result == 0:
            self.relay_states[channel - 1] = state
            self.log(f"Channel {channel} turned {'ON' if state else 'OFF'}")
            self.update_relay_display()
        elif result == 1:
            messagebox.showerror("Error", f"Failed to control channel {channel}")
            self.log(f"ERROR: Failed to control channel {channel}")
        elif result == 2:
            messagebox.showerror("Error", f"Channel {channel} does not exist on this device")
            self.log(f"ERROR: Channel {channel} does not exist")
    
    def open_all(self):
        if not self.device_opened:
            messagebox.showwarning("Warning", "Device not opened")
            return
        
        result = usb_relay_device_open_all_relay_channel(self.device_handle)
        if result == 0:
            self.relay_states = [True] * 8
            self.log("All channels opened")
            self.update_relay_display()
        else:
            messagebox.showerror("Error", "Failed to open all channels")
            self.log("ERROR: Failed to open all channels")
    
    def close_all(self):
        if not self.device_opened:
            messagebox.showwarning("Warning", "Device not opened")
            return
        
        result = usb_relay_device_close_all_relay_channel(self.device_handle)
        if result == 0:
            self.relay_states = [False] * 8
            self.log("All channels closed")
            self.update_relay_display()
        else:
            messagebox.showerror("Error", "Failed to close all channels")
            self.log("ERROR: Failed to close all channels")
    
    def update_relay_status(self):
        if not self.device_opened:
            return
        
        status = ctypes.c_uint()
        result = usb_relay_device_get_status(self.device_handle, ctypes.byref(status))
        
        if result == 0:
            for i in range(8):
                if (status.value & (1 << i)) != 0:
                    self.relay_states[i] = True
                else:
                    self.relay_states[i] = False
            self.update_relay_display()
            self.log(f"Status updated: {hex(status.value)}")
    
    def update_relay_display(self):
        for i, btn in enumerate(self.relay_status_btns):
            btn.config(bg="green" if self.relay_states[i] else "red")
    
    def joystick_listener(self):
        """Слушает события джойстика в отдельном потоке"""
        try:
            # Получаем список устройств
            devices = inputs.get_gamepad()
            if devices:
                self.joystick_name = devices[0].name if hasattr(devices[0], 'name') else "Generic USB Joystick"
                self.root.after(0, lambda: self.update_joystick_status(True))
                self.log(f"Joystick found: {self.joystick_name}")
        except:
            pass
        
        # Слушаем события
        button_states = {}
        
        while self.joystick_running:
            try:
                events = inputs.get_gamepad()
                for event in events:
                    # Кнопки (BTN)
                    if event.ev_type == 'Key':
                        # Button mapping для Generic USB Joystick
                        # A = BTN_A, B = BTN_B, X = BTN_X, Y = BTN_Y
                        # LB = BTN_TL, RB = BTN_TR, LT = BTN_TL2, RT = BTN_TR2
                        
                        button_map = {
                            'BTN_A': 1,      # Relay 1
                            'BTN_B': 2,      # Relay 2
                            'BTN_X': 3,      # Relay 3
                            'BTN_Y': 4,      # Relay 4
                            'BTN_TL': 5,     # LB - Relay 5
                            'BTN_TR': 6,     # RB - Relay 6
                            'BTN_TL2': 7,    # LT - Relay 7
                            'BTN_TR2': 8,    # RT - Relay 8
                        }
                        
                        if event.state == 1 and event.code in button_map:  # Button pressed
                            relay_channel = button_map[event.code]
                            
                            # Переключаем состояние релея
                            new_state = not self.relay_states[relay_channel - 1]
                            self.root.after(0, lambda ch=relay_channel, st=new_state: self.set_relay_state(ch, st))
                            
                            self.log(f"Joystick Button {event.code} - Relay {relay_channel} {'ON' if new_state else 'OFF'}")
                    
                    # D-Pad (ABS)
                    elif event.ev_type == 'Absolute':
                        # D-Pad для управления
                        if event.code == 'ABS_HAT0X':
                            if event.state == 1:  # Right
                                self.log("D-Pad Right pressed")
                            elif event.state == -1:  # Left
                                self.log("D-Pad Left pressed")
                        
                        elif event.code == 'ABS_HAT0Y':
                            if event.state == 1:  # Down
                                self.log("D-Pad Down pressed")
                            elif event.state == -1:  # Up
                                self.log("D-Pad Up pressed")
            
            except Exception as e:
                self.log(f"Joystick error: {str(e)[:50]}")
                pass
    
    def update_joystick_status(self, found):
        """Обновляет статус джойстика в UI"""
        if found:
            self.joystick_label.config(text=self.joystick_name, foreground="green")
        else:
            self.joystick_label.config(text="Not found", foreground="red")


if __name__ == "__main__":
    root = tk.Tk()
    app = USBRelayApp(root)
    
    def on_closing():
        app.joystick_running = False
        if usb_relay_dll:
            usb_relay_exit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
