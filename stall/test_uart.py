import serial

try:
    ser = serial.Serial("/dev/ttyS1", 9600, timeout=1)
    print("✅ JDY-40 слушает на /dev/ttyS1...")

    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode(errors='ignore').strip()
            if data:
                print(f"📡 Получено от JDY-40: {data}")

except KeyboardInterrupt:
    print("\n🔌 Завершено вручную.")
except Exception as e:
    print("❌ Ошибка:", e)
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("🔒 Соединение закрыто.")
