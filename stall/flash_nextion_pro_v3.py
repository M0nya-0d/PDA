import serial
import time
import os
import sys

# === НАСТРОЙКИ ===

tft_path = "/home/orangepi/PDA/stall/displey_pda.tft"
serial_port = "/dev/ttyS5"
baud_rates = [115200, 57600, 38400, 19200, 9600]  # Попробуем все скорости

# === ПРОВЕРКИ ===

if not os.path.exists(tft_path):
    print(f"❌ Файл не найден: {tft_path}")
    sys.exit(1)

file_size = os.path.getsize(tft_path)
print(f"📄 Размер файла: {file_size} байт")

# === ОТКЛЮЧЕНИЕ / ВКЛЮЧЕНИЕ ДИСПЛЕЯ ===

print("⚠️ ОТКЛЮЧИТЕ питание дисплея! Потом нажмите Enter.")
input("➡️ Теперь ВКЛЮЧИ питание дисплея и нажми Enter...")

# === ПОИСК РАБОЧЕЙ СКОРОСТИ ===

found_baud = None

for baud_rate in baud_rates:
    print(f"\n🔄 Пробуем скорость {baud_rate} baud...")

    try:
        ser = serial.Serial(serial_port, baudrate=baud_rate, timeout=2)
        print(f"✅ Открыт порт {serial_port} @ {baud_rate} baud")
    except Exception as e:
        print(f"❌ Ошибка открытия порта {serial_port}: {e}")
        continue

    # ПРЕДВАРИТЕЛЬНЫЙ СБРОС
    ser.write(b'\xFF\xFF\xFF')
    time.sleep(0.1)
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    # ЦИКЛ ОЖИДАНИЯ ГОТОВНОСТИ

    for attempt in range(3):
        print(f"🔁 Попытка {attempt + 1} на скорости {baud_rate}:")

        # Магическая строка
        ser.write(b'DRAKJHSUYDGBNCJHGJKSHBDN' + b'\xFF\xFF\xFF')
        print("➡️ Отправил 'магическую строку' для сброса режима.")

        # ВАЖНО! Ждём 2.0 сек (по Habr)
        time.sleep(2.0)

        # Сбросим input buffer
        ser.reset_input_buffer()

        # Отправляем connect
        ser.write(b'connect' + b'\xFF\xFF\xFF')
        print("➡️ Отправил 'connect'.")

        # Ждём ответ
        time.sleep(1.5)
        response = ser.read(64)
        print(f"⬅️ Ответ дисплея: {response}")

        # Проверяем есть ли 'comok' в ответе
        if b'comok' in response:
            print(f"✅ Дисплей ГОТОВ к прошивке на {baud_rate} baud!")
            found_baud = baud_rate
            break
        else:
            print("🔄 Дисплей НЕ ответил на 'connect' — повтор...")

    ser.close()

    if found_baud:
        break

# === ЕСЛИ НЕ НАШЛИ — ВЫХОД ===

if not found_baud:
    print("❌ Не удалось установить связь с дисплеем на доступных скоростях!")
    sys.exit(1)

# === ПОВТОРНО ОТКРЫВАЕМ ПОРТ НА РАБОЧЕЙ СКОРОСТИ ===

ser = serial.Serial(serial_port, baudrate=found_baud, timeout=2)
print(f"\n✅ Открыт порт {serial_port} @ {found_baud} baud для прошивки")

# === ОТКЛЮЧАЕМ СОН / ДИММЕР ===

print("➡️ Отключаю режим сна и диммера...")
ser.write(b'sleep=0' + b'\xFF\xFF\xFF')
time.sleep(0.1)
ser.write(b'dims=100' + b'\xFF\xFF\xFF')
time.sleep(0.1)

# === СБРАСЫВАЕМ БУФЕРЫ ПЕРЕД ПРОШИВКОЙ ===

ser.reset_input_buffer()
ser.reset_output_buffer()

# === ПОСЫЛАЕМ КОМАНДУ ПРОШИВКИ ===

cmd = f'whmi-wri {file_size},{found_baud},0'.encode('ascii') + b'\x79\x79\x79' + b'\xFF\xFF\xFF'
print(f"➡️ Отправляю команду прошивки: {cmd}")
ser.write(cmd)

# === ОЖИДАЕМ БАЙТ 0x05 ===

start_time = time.time()
got_ready = False

print("⏳ Ожидаем ответ 0x05 от дисплея (готовность к прошивке)...")

while time.time() - start_time < 0.5:
    b = ser.read(1)
    if b == b'\x05':
        got_ready = True
        print("✅ Получено 0x05 — дисплей ГОТОВ принимать прошивку!")
        break

if not got_ready:
    print("⚠️ Не получили 0x05 — дисплей НЕ ГОТОВ — ошибка!")
    ser.close()
    sys.exit(1)

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
