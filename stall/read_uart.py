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
                if len(packet) >= 8:
                    vp = (packet[4] << 8) | packet[5]
                    value = packet[6] + (packet[7] << 8)
                    print(f"  VP = 0x{vp:04X}  Значение: {value}")
                else:
                    print("  Пакет слишком короткий для 2-байтового значения!")
                i = end_idx + 1
            else:
                break
        else:
            i += 1

def hexstr_to_bytes(hexstr):
    # Удаляем пробелы и переводим в байты
    hexstr = hexstr.replace(' ', '')
    return bytes.fromhex(hexstr)

def main():
    try:
        with serial.Serial(serial_port, baudrate=baud_rate, timeout=0.2) as ser:
            print(f"✅ Открыт порт {serial_port} @ {baud_rate} бод")
            print("Введи команду в hex (например, 5aa50483000401) или 'exit':")
            while True:
                cmd = input("> ").strip()
                if cmd.lower() in ('exit', 'quit'):
                    break
                try:
                    packet = hexstr_to_bytes(cmd)
                    print(f"Отправка: {packet.hex()}")
                    ser.write(packet)
                    # Ждем и читаем ответ (до 128 байт, 0.2 сек таймаут)
                    time.sleep(0.05)
                    data = ser.read(128)
                    if data:
                        print(f"Ответ ({len(data)} байт): {data.hex()}")
                        parse_dwin_packets(data)
                    else:
                        print("Нет ответа (таймаут)!")
                except Exception as e:
                    print(f"Ошибка: {e}")
    except serial.SerialException as e:
        print(f"❌ Ошибка открытия порта {serial_port}: {e}")

if __name__ == "__main__":
    main()