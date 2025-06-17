import serial
import time
import json
import uart


current_nik = "vasy"
number_pda = 0
HP = 0
RD = 0
rd_up = 0
hp_up = 0
antirad = 0
vodka = 0
bint = 0
apteka20 = 0
apteka30 = 0
apteka50 = 0
params = {}

uart.HP = HP
uart.RD = RD
uart.antirad = antirad
uart.vodka = vodka
uart.bint = bint
uart.apteka20 = apteka20
uart.apteka30 = apteka30
uart.apteka50 = apteka50
uart.current_nik = current_nik
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
        HP += 9
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
            #if hp_up >= 3:    
                #if HP < 10000:
                    #HP += 1
                    #hp_up = 0
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
                HP -= 5
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
    global HP, RD, antirad, params, vodka, bint, apteka20, apteka30, apteka50, number_pda, current_nik
    all_params = load_params("/home/orangepi/PDA/stall/param.json")
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

    with open("/home/orangepi/PDA/number.txt", "r") as f:
        number_pda = int(f.read().strip())
        number_key = str(number_pda)
        all_params = load_params("/home/orangepi/PDA/stall/param.json")
        if number_key in all_params:
            params = all_params[number_key]
            current_nik = params.get("Nik-name", "noname")
            print(f"Nik-name найден: {current_nik}")
            uart.send_text = send_text
            uart.number_pda = number_pda
        else:
            print(f"Ошибка: номер {number_pda} не найден в param.json")
            return
        
    with open(VERS_PATH, "r") as f:
        version = f.read().strip()
    int_version = int(version)  
    int_write(0x5999, int_version)



    HP = params["HP"]
    RD = params["RD"]
    for med in params.get("Medicina", []):
        if med["name"] == "Antirad":
            antirad = med["count"]
    for med in params.get("Medicina", []):
        if med["name"] == "Vodka":
            vodka = med["count"]
    for med in params.get("Medicina", []):
        if med["name"] == "Bint":
            bint = med["count"]
    for med in params.get("Medicina", []):
        if med["name"] == "Apteka20":
            apteka20 = med["count"] 
    for med in params.get("Medicina", []):
        if med["name"] == "Apteka30":
            apteka30 = med["count"]
    for med in params.get("Medicina", []):
        if med["name"] == "Apteka50":
            apteka50 = med["count"]                                   

    uart.HP = HP
    uart.RD = RD
    uart.antirad = antirad
    uart.vodka = vodka
    uart.bint = bint
    uart.apteka20 = apteka20
    uart.apteka30 = apteka30
    uart.apteka50 = apteka50
    uart.current_nik = current_nik
    uart.send_text = send_text
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
                    uart.process_packet(packet, send_text, int_write) # забрал после юарта
                    HP = uart.HP
                    RD = uart.RD
                    antirad = uart.antirad
                    vodka = uart.vodka
                    bint = uart.bint
                    apteka20 = uart.apteka20
                    apteka30 = uart.apteka30
                    apteka50 = uart.apteka50
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
            for med in params.get("Medicina", []): # записал в файл
                if med["name"] == "Antirad":
                    med["count"] = antirad
                elif med["name"] == "Vodka":
                    med["count"] = vodka
                elif med["name"] == "Bint":
                    med["count"] = bint
                elif med["name"] == "Apteka20":
                    med["count"] = apteka20
                elif med["name"] == "Apteka30":
                    med["count"] = apteka30
                elif med["name"] == "Apteka50":
                    med["count"] = apteka50  
            for packet in packets:   # обновляю на экран
                ser.write(packet)
            int_write(0x5000, HP)
            int_write(0x5001, RD)
            int_write(0x5301, antirad)
            int_write(0x5302, vodka)
            int_write(0x5308, bint)
            int_write(0x5309, apteka20)
            int_write(0x5310, apteka30)
            int_write(0x5311, apteka50)
            int_write(0x5999, int_version)

            now_time = time.strftime("%H%M", time.localtime())
            int_time = int(now_time)
            int_write(0x5990, int_time) # время
            print(int_time)            
            print(f'HP = {HP}, RD = {RD}')

            if changed:
                need_save = True
                save_counter += 1
                if save_counter >= 10:
                    save_counter = 0
                    number_key = str(number_pda)
                    if number_key not in all_params:
                        all_params[number_key] = {}
                    all_params[number_key]["HP"] = HP 
                    all_params[number_key]["RD"] = RD 
                    known_meds = {  
                        "Antirad": antirad,
                        "Vodka": vodka,
                        "Bint": bint,
                        "Apteka20": apteka20,
                        "Apteka30": apteka30,
                        "Apteka50": apteka50
                    } 
                    new_meds = []  
                    for med in params.get("Medicina", []): 
                        name = med["name"]
                        count = known_meds.get(name, med["count"])
                        new_meds.append({"name": name, "count": count})
                    all_params[number_key]["Medicina"] = new_meds    
                    save_params("/home/orangepi/PDA/stall/param.json", all_params)    
                    #all_params[number_key] = params
                    #save_params("param.json", all_params)
                    print("Сохранено в param.json после изменений")
            else:
                save_counter = 0
                need_save = False

        time.sleep(0.01)
if __name__ == "__main__":
    main()        