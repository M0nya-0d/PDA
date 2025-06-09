import serial
import time
import os
import sys

# === НАСТРОЙКИ ===

tft_path = "/home/orangepi/PDA/stall/displey_pda.tft"
serial_port = "/dev/ttyS5"
baud_rate = 9600  # или 115200

# === ПРОВЕРКИ ===

if not os.path.exists(tft_path):
    print(f"❌ Файл не найден: {tft_path}")
    sys.exit(1)

file_size = os.path.getsize(tft_path)
print(f"📄 Размер файла: {file_size} байт")

# === ОТКРЫВАЕМ ПОРТ ===

try:
    ser = serial.Serial(serial_port, baudrate=baud_rate, timeout=2)
    print(f"✅ Открыт порт {serial_port} @ {baud_rate} baud")
except Exception as e:
    print(f"❌ Ошибка открытия порта {serial_port}: {e}")
    sys.exit(1)

# === ОЖИДАНИЕ ГОТОВНОСТИ ДИСПЛЕЯ ===

print("⚠️ ОТКЛЮЧИТЕ питание дисплея! Потом нажмите Enter.")
input("➡️ Теперь ВКЛЮЧИ питание дисплея и нажми Enter...")

# Цикл — пока дисплей не скажет что ГОТОВ
while True:
    # Отправляем команду прошивки
    cmd = f'whmi-wri {file_size},{baud_rate},0\r'.encode('ascii') + b'\xFF\xFF\xFF'
    print(f"➡️ Отправляю команду: {cmd}")
    ser.write(cmd)

    # Ждём ответ
    time.sleep(0.5)
    response = ser.read(6)

    print(f"⬅️ Ответ дисплея: {response.hex()}")

    # Проверяем ответ
    if response.startswith(b'\x05\x00\x00'):
        print("✅ Дисплей ГОТОВ к прошивке!")
        break  # выходим из цикла — будем слать прошивку
    else:
        print("🔄 Дисплей НЕ ГОТОВ → повтор через 1 сек...")
        time.sleep(1)

# === ОТПРАВКА ПРОШИВКИ ===

print("📤 Передача прошивки...")
with open(tft_path, 'rb') as f:
    sent = 0
    chunk = f.read(4096)
    while chunk:
        ser.write(chunk)
        sent += len(chunk)
        percent = (sent / file_size) * 100
        print(f"\r🟢 Прогресс: {percent:.1f}% ({sent}/{file_size} байт)", end="")
        chunk = f.read(4096)

print("\n✅ ПРОШИВКА УСПЕШНО ЗАВЕРШЕНА!")

# === ЗАКРЫВАЕМ ПОРТ ===

ser.close()
print("✅ Порт закрыт")
