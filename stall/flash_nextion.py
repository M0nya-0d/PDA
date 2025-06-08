import serial
import time
import os
import sys

# === НАСТРОЙКИ ===

# Путь к файлу прошивки
tft_path = "/home/monya/PDA/stall/displey_pda.tft"

# UART порт (PH2/PH3 → UART1 → /dev/ttyS1)
serial_port = "/dev/ttyS1"

# Список скоростей для попытки (можно добавить другие)
baud_rates = [115200, 9600, 57600]

# === ПРОВЕРКИ ===

if not os.path.exists(tft_path):
    print(f"❌ Файл не найден: {tft_path}")
    sys.exit(1)

file_size = os.path.getsize(tft_path)
print(f"📄 Размер файла: {file_size} байт")

# === ПРОШИВКА ===

for baud_rate in baud_rates:
    try:
        print(f"\n🔌 Подключение к {serial_port} @ {baud_rate} бод...")
        ser = serial.Serial(serial_port, baudrate=baud_rate, timeout=2)

        print("⏳ Ждите! Включите питание дисплея, подождите 2 секунды...")
        time.sleep(2)

        # Отправляем команду прошивки
        cmd = f'whmi-wri {file_size},{baud_rate},0\r'.encode('ascii') + b'\xFF\xFF\xFF'
        ser.write(cmd)
        time.sleep(1)

        # Отправка файла с прогрессом
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

        print("\n✅ Прошивка завершена на скорости", baud_rate)
        ser.close()
        break  # успешная прошивка → выходим из цикла

    except serial.SerialException as e:
        print(f"⚠️ Не удалось открыть порт {serial_port} на {baud_rate} бод: {e}")
    except Exception as e:
        print(f"⚠️ Ошибка на скорости {baud_rate}: {e}")

else:
    print("❌ Не удалось прошить дисплей на доступных скоростях.")