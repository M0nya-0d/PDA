import serial
import time
import os

# Путь к tft файлу
tft_path = "/home/orangepi/PDA/stall/displey_pda.tft"

# Последовательный порт и скорость
serial_port = "/dev/ttyS1"  # это PH2/PH3 (UART1) на Orange Pi Zero 3
baud_rate = 115200

# Подключение
ser = serial.Serial(serial_port, baudrate=baud_rate, timeout=2)

# Ожидаем включения дисплея
print("Ожидаем включения дисплея (2 секунды)...")
time.sleep(2)

# Отправляем команду прошивки
file_size = os.path.getsize(tft_path)
cmd = f'whmi-wri {file_size},115200,0\r'.encode('ascii') + b'\xFF\xFF\xFF'
ser.write(cmd)
time.sleep(1)

# Передаём сам файл
with open(tft_path, 'rb') as f:
    chunk = f.read(4096)
    while chunk:
        ser.write(chunk)
        chunk = f.read(4096)

print("✅ Прошивка завершена.")
ser.close()