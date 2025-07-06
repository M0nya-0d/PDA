import serial

try:
    ser = serial.Serial("/dev/ttyS3", 9600, timeout=2)
    print("✅ Устройство открылось успешно.")
    ser.close()
except Exception as e:
    print("❌ Ошибка:", e)