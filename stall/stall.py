import serial
import time
import json
import uart


HP = 0
RD = 0
rd_up = 0
hp_up = 0
antirad = 0
vodka = 0
params = {}

uart.HP = HP
uart.RD = RD
uart.antirad = antirad
uart.vodka = vodka
uart.params = params

oasis = False
norma = True

serial_port = "/dev/ttyS5"
baud_rate = 115200
VERS_PATH = "/home/orangepi/PDA/vers.txt"

def int_write(addr, num):
    packet = bytearray([
        0x5A, 0xA5,
        0x05,
        0x82,
        (addr >> 8) & 0xFF, addr & 0xFF,
        (num >> 8) & 0xFF, num & 0xFF
    ])
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
        ser.write(packet)

TEXT_LENGTH = 7  # или сколько в настройках DWIN

def send_text(addr, text):
    text = text.ljust(TEXT_LENGTH)
    text_bytes = text.encode("ascii")
    length = 3 + len(text_bytes)
    packet = bytearray([
        0x5A, 0xA5,
        length,
        0x82,
        (addr >> 8) & 0xFF, addr & 0xFF
    ]) + text_bytes
    print("Отправляется пакет:", packet.hex())
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
        ser.write(packet)

def update_hp_rd(HP, RD):
    global rd_up, hp_up, oasis, norma
    rd_up += 1
    hp_up += 1
    orig_HP, orig_RD = HP, RD
    send_packets = []  # Список байтовых команд, которые нужно отправить
    #if HP <= 0:
    #    norma = False
    #   HP = 0
        #send_packets.append(bytes([0x5A, 0xA5, 0x07, 0x82, 0x00, 0x84, 0x5A, 0x01, 0x00, 0x10]))
    if oasis:
        norma = False
        send_packets.append(bytes([0x5A, 0xA5, 0x07, 0x82, 0x00, 0x84, 0x5A, 0x01, 0x00, 0x01]))
        if RD > 0:
            RD = 0
        HP += 11
        if HP > 8000:
            HP = 8000
            oasis = False
            norma = True
            send_packets.append(bytes([0x5A, 0xA5, 0x07, 0x82, 0x00, 0x84, 0x5A, 0x01, 0x00, 0x00]))
    if norma:
        if RD > 0 and RD <= 1000:
            if rd_up >= 3:
                RD -= 1
                rd_up = 0
            if hp_up >= 3:    
                if HP < 10000:
                    HP += 1
                    hp_up = 0
        elif RD > 1000 and RD <= 4000:
            if rd_up >= 3:
                RD -= 1
                rd_up = 0
            if hp_up >= 2:
                HP -= 1
                hp_up = 0
                if HP <= 0:
                    norma = False
                    HP = 0 
                    send_packets.append(bytes([0x5A, 0xA5, 0x07, 0x82, 0x00, 0x84, 0x5A, 0x01, 0x00, 0x0A]))   
        elif RD > 4000 and RD <= 7000:
            if rd_up >= 2:
                RD -= 1
                rd_up = 0
            if hp_up >= 2:    
                HP -= 2
                hp_up = 0
                if HP <= 0:
                    norma = False
                    HP = 0
                    send_packets.append(bytes([0x5A, 0xA5, 0x07, 0x82, 0x00, 0x84, 0x5A, 0x01, 0x00, 0x0A]))
        elif RD > 7000 and RD <= 8000:
            HP -= 10
            if HP <= 0:
                norma = False
                HP = 0
                send_packets.append(bytes([0x5A, 0xA5, 0x07, 0x82, 0x00, 0x84, 0x5A, 0x01, 0x00, 0x0A]))
        elif RD > 8000 and RD <= 15000:
            HP -= 50
            if HP <= 0:
                norma = False
                HP = 0
                RD = 0 
                send_packets.append(bytes([0x5A, 0xA5, 0x07, 0x82, 0x00, 0x84, 0x5A, 0x01, 0x00, 0x0A]))
        elif RD == 0 and HP < 10000:
            HP += 1
            if HP > 10000:
                HP = 10000
    changed = (HP != orig_HP) or (RD != orig_RD)
    return HP, RD, changed, send_packets



def load_params(filename):
    with open(filename, "r") as f:
        data = json.load(f)
    return data

def save_params(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def main():
    global HP, RD, antirad, params, vodka

    with open(VERS_PATH, "r") as f:
        version = f.read().strip()
    print(f"Версия программы: {version}")

    ser = serial.Serial(serial_port, baudrate=baud_rate, timeout=0.01)

    def int_write(addr, num):
        packet = bytearray([
            0x5A, 0xA5,
            0x05,
            0x82,
            (addr >> 8) & 0xFF, addr & 0xFF,
            (num >> 8) & 0xFF, num & 0xFF
        ])
        ser.write(packet)

    def send_text(addr, text):
        text = text.ljust(TEXT_LENGTH)
        text_bytes = text.encode("ascii")
        length = 3 + len(text_bytes)
        packet = bytearray([
            0x5A, 0xA5,
            length,
            0x82,
            (addr >> 8) & 0xFF, addr & 0xFF
        ]) + text_bytes
        print("Отправляется пакет:", packet.hex())
        ser.write(packet)

    send_text(0x5999, version)

    params = load_params("param.json")
    HP = params["HP"]
    RD = params["RD"]
    for med in params.get("Medicina", []):
        if med["name"] == "Antirad":
            antirad = med["count"]
    for med in params.get("Medicina", []):
        if med["name"] == "Vodka":
            vodka = med["count"]

    uart.HP = HP
    uart.RD = RD
    uart.antirad = antirad
    uart.vodka = vodka
    uart.params = params

    buffer = bytearray()
    tcount = 0
    last_byte_time = time.time()
    last_update = time.monotonic()
    save_counter = 0
    need_save = False

    while True:
        data = ser.read(1)
        if data:
            buffer += data
            if len(buffer) < 32:
                tcount = 5
            last_byte_time = time.time()
        else:
            if tcount > 0 and (time.time() - last_byte_time) > 0.002:
                tcount -= 1
                last_byte_time = time.time()
        if tcount == 0 and len(buffer) > 0:
            if len(buffer) >= 3 and buffer[0] == 0x5A and buffer[1] == 0xA5:
                plen = buffer[2]
                if len(buffer) >= plen + 3:
                    packet = buffer[:plen + 3]
                    uart.process_packet(packet)
                    HP = uart.HP
                    RD = uart.RD
                    antirad = uart.antirad
                    vodka = uart.vodka
                    params = uart.params
            buffer = bytearray()

        now = time.monotonic()
        if now - last_update >= 1.0:
            last_update = now
            HP, RD, changed, packets = update_hp_rd(HP, RD)  
            uart.HP = HP
            uart.RD = RD
            params["HP"] = HP
            params["RD"] = RD
            for med in params.get("Medicina", []):
                if med["name"] == "Antirad":
                    med["count"] = antirad
                elif med["name"] == "Vodka":
                    med["count"] = vodka
            for packet in packets:
                ser.write(packet)
            int_write(0x5000, HP)
            int_write(0x5001, RD)
            int_write(0x5301, antirad)
            int_write(0x5302, vodka)
            print(f'HP = {HP}, RD = {RD}')

            if changed:
                need_save = True
                save_counter += 1
                if save_counter >= 60:
                    save_counter = 0
                    save_params("param.json", params)
                    print("Сохранено в param.json после изменений")
            else:
                save_counter = 0
                need_save = False

        time.sleep(0.01)
if __name__ == "__main__":
    main()        