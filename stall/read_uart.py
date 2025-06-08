import serial

# UART порт и скорость (Проверь свою скорость!)
serial_port = "/dev/ttyS5"
baud_rate = 9600  # или 115200 — какая стоит в твоем Nextion!

try:
    ser = serial.Serial(serial_port, baudrate=baud_rate, timeout=1)
    print(f"📡 Чтение {serial_port} @ {baud_rate} бод... (нажмите Ctrl+C для выхода)")
    
    while True:
        data = ser.readline()
        if data:
            print(f"Получено: {data.hex()} | {data}")

except serial.SerialException as e:
    print(f"❌ Ошибка открытия порта {serial_port}: {e}")

except KeyboardInterrupt:
    print("\n🛑 Завершено пользователем.")
finally:
    try:
        ser.close()
    except:
        pass