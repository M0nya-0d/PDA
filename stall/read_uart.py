import serial
import time

serial_port = "/dev/ttyS5"
baud_rate = 115200  # или 115200

try:
    ser = serial.Serial(serial_port, baudrate=baud_rate, timeout=0.1)
    print(f"📡 Чтение {serial_port} @ {baud_rate} бод... (нажмите Ctrl+C для выхода)")
    
    while True:
        data = ser.read(128)  # Читаем до 128 байт за раз (или сколько пришло)
        if data:
            print(f"Получено: {data.hex()} | {data}")
        time.sleep(0.05)  # Не грузим процессор

except serial.SerialException as e:
    print(f"❌ Ошибка открытия порта {serial_port}: {e}")

except KeyboardInterrupt:
    print("\n🛑 Завершено пользователем.")
finally:
    try:
        ser.close()
    except:
        pass