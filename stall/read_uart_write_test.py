import serial
import time

serial_port = "/dev/ttyS5"  # UART1 на Orange Pi Zero 3
baud_rate = 19200  # или 115200 — смотри сам

try:
    ser = serial.Serial(serial_port, baudrate=baud_rate, timeout=1)
    print(f"✅ Открыт порт {serial_port} @ {baud_rate} baud")
except Exception as e:
    print(f"❌ Ошибка открытия порта {serial_port}: {e}")
    exit(1)

try:
    while True:
        # Отправляем тестовую строку
        test_string = "Hello UART!\n"
        ser.write(test_string.encode('utf-8'))
        print(f"➡️ Отправлено: {test_string.strip()}")

        # Читаем ответ
        time.sleep(0.1)  # небольшая пауза
        incoming[] = ser.read(ser.in_waiting or 1)
        if incoming:
            print(f"⬅️ Получено: {incoming.decode(errors='ignore').strip()}")

        time.sleep(1)  # раз в секунду посылаем

except KeyboardInterrupt:
    print("⏹️ Выход по Ctrl+C")
finally:
    ser.close()
    print("✅ Порт закрыт")