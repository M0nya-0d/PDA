import serial
import time

serial_port = "/dev/ttyS5"
baud_rate = 19200  # или твоя скорость

MAX_BUF = 32

def process_packet(packet):
    cmd = packet[4]
    # Проверка команды и VP
    if cmd == 0x83 and len(packet) >= 8:
        vp = (packet[4+1] << 8) | packet[4+2]
        value = packet[7]  # обычно младший байт (0x00 или 0x01)
        # Проверяем нужный VP
        if vp == 0x1200:
            if value == 1:
                print("ВКЛЮЧЕНО! (5A A5 06 83 12 00 01 00 01)")
            elif value == 0:
                print("ВЫКЛЮЧЕНО! (5A A5 06 83 12 00 01 00 00)")
            else:
                print(f"VP 0x1200: Неизвестное значение: {value}")
        else:
            print(f"Другой VP = 0x{vp:04X}, значение: {value}")
    else:
        print(f"Необработанная команда: 0x{cmd:02X}")

def main():
    with serial.Serial(serial_port, baudrate=baud_rate, timeout=0.01) as ser:
        buffer = bytearray()
        tcount = 0
        last_byte_time = time.time()

        while True:
            data = ser.read(1)
            if data:
                buffer += data
                if len(buffer) < MAX_BUF:
                    tcount = 5
                last_byte_time = time.time()
            else:
                # Каждые 2 мс декрементируем tcount (имитация Arduino)
                if tcount > 0 and (time.time() - last_byte_time) > 0.002:
                    tcount -= 1
                    last_byte_time = time.time()

            if tcount == 0 and len(buffer) > 0:
                if len(buffer) >= 3 and buffer[0] == 0x5A and buffer[1] == 0xA5:
                    plen = buffer[2]
                    if len(buffer) >= plen + 3:
                        packet = buffer[:plen + 3]
                        process_packet(packet)
                # После обработки сбрасываем буфер
                buffer = bytearray()
            time.sleep(0.001)

if __name__ == "__main__":
    main()