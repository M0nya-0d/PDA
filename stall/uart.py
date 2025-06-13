import serial
import time


serial_port = "/dev/ttyS5"
baud_rate = 115200  # или твоя скорость

MAX_BUF = 32

def process_packet(packet):
    global HP, RD, antirad, params, vodka
    if packet[0] == 0x5A and packet[1] == 0xA5:
        if len(packet) >= 9 and packet[3] == 0x83:
            vp = (packet[4] << 8) | packet[5]
            value = packet[8]
            if vp == 0x5501:
                if value == 1:
                    if antirad > 0:
                        print("используем антирад")
                        antirad -= 1
                        for med in params.get("Medicina", []):
                            if med["name"] == "Antirad":
                                med["count"] = antirad
                                break
                        RD -= 7000
                        HP -= 2000
                        if RD < 0: RD = 0
                        if HP < 0: HP = 0
                    else:
                        print("Нет антирада в запасе!")
                elif value == 0:
                    print("СОСТОЯНИЕ: ВЫКЛЮЧЕНО (OFF)")
            elif vp == 0x5502:
                if value == 1:
                    if vodka > 0:
                        print("используем водка")
                        vodka -= 1
                        for med in params.get("Medicina", []):
                            if med["name"] == "Vodka":
                                med["count"] = vodka
                                break
                        RD -= 1000
                        HP -= 1000
                        if RD < 0: RD = 0
                        if HP < 0: HP = 0
                    else:
                        print("Нет антирада в запасе!")
                elif value == 0:
                    print("СОСТОЯНИЕ: ВЫКЛЮЧЕНО (OFF)")
            else:
                print(f"VP 0x{vp:04X}: значение {value}")
        else:
            print("Пакет нераспознан или слишком короткий:", packet.hex())
    else:
        print("Пакет не DWIN или нераспознан")

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
