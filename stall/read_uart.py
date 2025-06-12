import serial
import time

serial_port = "/dev/ttyS5"
baud_rate = 19200  # Или твоя скорость

def parse_dwin_packets(buffer):
    i = 0
    while i < len(buffer) - 2:
        if buffer[i] == 0x5A and buffer[i+1] == 0xA5:
            plen = buffer[i+2]
            end_idx = i + 3 + plen - 1
            if end_idx < len(buffer):
                packet = buffer[i:end_idx+1]
                print(f"➡️ DWIN-пакет ({len(packet)} байт): {packet.hex()}")
                # Краткий разбор пакета:
                if len(packet) >= 7:
                    # VP (адрес переменной):
                    vp_hi = packet[4]
                    vp_lo = packet[5]
                    vp = (vp_hi << 8) | vp_lo
                    value = packet[6]
                    print(f"  VP = 0x{vp:04X}  Значение: {value}")
                i = end_idx + 1
            else:
                break
        else:
            i += 1

try:
    ser = serial.Serial(serial_port, baudrate=baud_rate, timeout=0.01)
    print(f"📡 Чтение {serial_port} @ {baud_rate} бод... (нажмите Ctrl+C для выхода)")

    buffer = b''
    last_time = time.time()

    while True:
        data = ser.read(128)
        if data:
            buffer += data
            last_time = time.time()
        # Разбираем буфер, если прошло больше 50 мс без новых данных
        if buffer and (time.time() - last_time > 0.05):
            print(f"Получено ({len(buffer)} байт): {buffer.hex()} | {buffer}")
            # Разбор DWIN-пакетов из буфера
            parse_dwin_packets(buffer)
            buffer = b''
        time.sleep(0.01)

except serial.SerialException as e:
    print(f"❌ Ошибка открытия порта {serial_port}: {e}")

except KeyboardInterrupt:
    print("\n🛑 Завершено пользователем.")
finally:
    try:
        ser.close()
    except:
        pass