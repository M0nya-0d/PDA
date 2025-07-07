import serial
import time
import json
import uart
import select


current_nik = "vasy"
number_pda = 0
HP = 0
RD = 0
arm_psy = 0
arm_rad = 0
arm_anom = 0
rd_up = 0
hp_up = 0
radic_up = 0
anomaly_up = 0
oasis_up = 0
antirad = 0
vodka = 0
bint = 0
apteka20 = 0
apteka30 = 0
apteka50 = 0
Jacket = 0
Merc = 0
Exoskeleton = 0
Seva = 0
Stalker = 0
Ecologist = 0
params = {}

uart.HP = HP
uart.RD = RD
uart.arm_psy = arm_psy
uart.arm_rad = arm_rad
uart.arm_anom = arm_anom
uart.antirad = antirad
uart.vodka = vodka
uart.bint = bint
uart.apteka20 = apteka20
uart.apteka30 = apteka30
uart.apteka50 = apteka50
uart.Jacket = Jacket
uart.current_nik = current_nik
uart.params = params

oasis = False
norma = True
flag_radic = False
flag_anomaly = False

jdy_port = "/dev/ttyS1"
jdy_baud = 9600
jdy_ser = serial.Serial(jdy_port, baudrate=jdy_baud, timeout=0.01)
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
    global rd_up, hp_up, oasis, norma, flag_radic, flag_anomaly, radic_up, oasis_up, anomaly_up
    rd_up += 1
    hp_up += 1
    orig_HP, orig_RD = HP, RD
    send_packets = []  # Список байтовых команд, которые нужно отправить
    #if HP <= 0:
    #    norma = False
    #   HP = 0
        #send_packets.append(bytes([0x5A, 0xA5, 0x07, 0x82, 0x00, 0x84, 0x5A, 0x01, 0x00, 0x10]))
    if flag_radic and norma:
        send_packets.append(bytes([0x5A, 0xA5, 0x07, 0x82, 0x00, 0x84, 0x5A, 0x01, 0x00, 0x16]))
        radic_up += 1
        if radic_up >= 5:
            send_packets.append(bytes([0x5A, 0xA5, 0x07, 0x82, 0x00, 0x84, 0x5A, 0x01, 0x00, 0x00]))
            flag_radic = False
            radic_up = 0

    if flag_anomaly and norma:
        send_packets.append(bytes([0x5A, 0xA5, 0x07, 0x82, 0x00, 0x84, 0x5A, 0x01, 0x00, 0x02]))
        anomaly_up += 1
        if anomaly_up >= 5:
            send_packets.append(bytes([0x5A, 0xA5, 0x07, 0x82, 0x00, 0x84, 0x5A, 0x01, 0x00, 0x00]))
            flag_anomaly = False
            anomaly_up = 0    

    if oasis and norma == False:
        if HP < 8000:
            norma = False
            send_packets.append(bytes([0x5A, 0xA5, 0x07, 0x82, 0x00, 0x84, 0x5A, 0x01, 0x00, 0x01]))
            oasis_up += 1
            if oasis_up >= 1:
                if RD > 0:
                    RD = 0
                HP += 9
                if HP >= 8000:
                    HP = 8000
                    oasis = False
                    norma = True
                    send_packets.append(bytes([0x5A, 0xA5, 0x07, 0x82, 0x00, 0x84, 0x5A, 0x01, 0x00, 0x00]))
            if oasis_up >= 6:
                oasis_up = 0
                oasis = False        
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
                    RD = 0 
                    send_packets.append(bytes([0x5A, 0xA5, 0x07, 0x82, 0x00, 0x84, 0x5A, 0x01, 0x00, 0x0A]))   
        elif RD > 4000 and RD <= 7000:
            if rd_up >= 2:
                RD -= 1
                rd_up = 0
            if hp_up >= 1:    
                HP -= 2
                hp_up = 0
                if HP <= 0:
                    norma = False
                    HP = 0
                    RD = 0
                    send_packets.append(bytes([0x5A, 0xA5, 0x07, 0x82, 0x00, 0x84, 0x5A, 0x01, 0x00, 0x0A]))
        elif RD > 7000 and RD <= 8000:
            HP -= 10
            if HP <= 0:
                norma = False
                HP = 0
                RD = 0
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
    print(f"[DEBUG] update_hp_rd: orig_HP={orig_HP}, orig_RD={orig_RD}, new_HP={HP}, new_RD={RD}, changed={changed}")
    return HP, RD, changed, send_packets

def radic():
    global RD, HP, flag_radic
    flag_radic = True
    RD += 100
    HP -= 50

def resp():
    global oasis, oasis_up
    oasis_up = 1
    oasis = True

def anomaly():
    global RD, HP, flag_anomaly
    flag_anomaly = True
    RD += 100
    HP -= 50

def load_params(filename):
    with open(filename, "r") as f:
        data = json.load(f)
    return data

def save_params(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def main():
    global HP, RD, antirad, params, vodka, bint, apteka20, apteka30, apteka50, number_pda, current_nik, arm_anom, arm_psy, arm_rad, Jacket
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
    arm_psy = params["PSY"]
    arm_rad = params["Radic"]
    arm_anom = params["Anomaly"]
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
    for med in params.get("Medicina", []):
        if med["name"] == "Jacket":
            Jacket = med["count"]
                                   

    uart.HP = HP
    uart.RD = RD
    uart.arm_psy = arm_psy
    uart.arm_rad = arm_rad
    uart.arm_anom = arm_anom
    uart.antirad = antirad
    uart.vodka = vodka
    uart.bint = bint
    uart.apteka20 = apteka20
    uart.apteka30 = apteka30
    uart.apteka50 = apteka50
    uart.Jacket = Jacket
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
        rlist, _, _ = select.select([ser, jdy_ser], [], [], 0.01)
        for s in rlist:
            if s == ser:
                data = ser.read(1)
                if data:
                    buffer += data
                    if len(buffer) >= 3 and buffer[0] == 0x5A and buffer[1] == 0xA5:
                        plen = buffer[2]
                        if len(buffer) >= plen + 3:
                            packet = buffer[:plen + 3]
                            uart.process_packet(packet, send_text, int_write)
                            HP, RD = uart.HP, uart.RD
                            antirad, vodka = uart.antirad, uart.vodka
                            bint = uart.bint
                            apteka20, apteka30, apteka50 = uart.apteka20, uart.apteka30, uart.apteka50
                            params = uart.params
                            buffer = bytearray()
            elif s == jdy_ser:
                jdy_data = jdy_ser.read(jdy_ser.in_waiting or 1)
                if jdy_data:
                    decoded = jdy_data.decode(errors='ignore').strip()
                    print(f"[JDY-40] 📶 Получено: {decoded}")
                    if decoded == "Radic-1":
                        radic()  
                    if decoded == "Oasis":
                        resp()
                    if decoded == "Anomaly":
                        anomaly()          

        now = time.monotonic()
        if now - last_update >= 1.0:
            last_update = now
            HP, RD, changed, packets = update_hp_rd(HP, RD)  
            uart.HP = HP
            uart.RD = RD
            params["HP"] = HP
            params["RD"] = RD
            params["PSY"] = arm_psy
            params["Radic"] = arm_rad
            params["Anomaly"] = arm_anom
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
                elif med["name"] == "Jacket":
                    med["count"] = Jacket
      
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
            int_write(0x5312, Jacket)
            int_write(0x5321, arm_rad)
            int_write(0x5999, int_version)

            now_time = time.strftime("%H%M", time.localtime())
            int_time = int(now_time)
            int_write(0x5990, int_time) # время
            print(int_time)            
            print(f'HP = {HP}, RD = {RD}')

            if changed:
                #save_counter += 1
                #if save_counter >= 5:
                    #save_counter = 0
                number_key = str(number_pda)
                if number_key not in all_params:
                    all_params[number_key] = {}
                all_params[number_key]["HP"] = HP 
                all_params[number_key]["RD"] = RD
                all_params[number_key]["PSY"] = arm_psy
                all_params[number_key]["Anomaly"] = arm_anom
                all_params[number_key]["Radic"] = arm_rad 
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

        time.sleep(0.01)
if __name__ == "__main__":
    main()        