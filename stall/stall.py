import serial
import time
import json
import uart
import select
from queue import Queue

jdy_send_queue = Queue()
current_nik = "gggg"
number_pda = 0
HP = 0
RD = 0
arm_psy = 0
arm_rad = 0
arm_anom = 0
regen = 0
rd_up = 0
hp_up = 0
radic_up = 0
anomaly_up = 0
oasis_up = 0
regen_up = 0
antirad = 0
vodka = 0
bint = 0
apteka20 = 0
apteka30 = 0
apteka50 = 0
Drink = 0
B190 = 0
Psy_block = 0
Ip2 = 0
Anabiotic = 0
Jacket = 0
Merc = 0
Exoskeleton = 0
Seva = 0
Stalker = 0
Ecologist = 0

block_time = 0

art1 = 120
art2 = 32
art3 = 40
art4 = 150
art5 = 80
art_up = 0
flag_art = True

oasis = False
norma = True
flag_radic = False
flag_anomaly = False
block_psy = False
block_rad = False
block_anom = False

params = {}

uart.HP = HP
uart.RD = RD
uart.arm_psy = arm_psy
uart.arm_rad = arm_rad
uart.arm_anom = arm_anom
uart.regen = regen

uart.antirad = antirad
uart.vodka = vodka
uart.Anabiotic = Anabiotic

uart.bint = bint
uart.apteka20 = apteka20
uart.apteka30 = apteka30
uart.apteka50 = apteka50

uart.Drink = Drink
uart.B190 = B190
uart.Psy_block = Psy_block
uart.Ip2 = Ip2

uart.Jacket = Jacket
uart.Merc = Merc
uart.Exoskeleton = Exoskeleton
uart.Seva = Seva
uart.Stalker = Stalker
uart.Ecologist = Ecologist

uart.block_time = block_time
uart.block_psy = block_psy
uart.block_rad = block_rad
uart.block_anom = block_anom

uart.current_nik = current_nik
uart.params = params


jdy_port = "/dev/ttyUSB0"
jdy_baud = 9600
jdy_ser = serial.Serial(jdy_port, baudrate=jdy_baud, timeout=0.3)
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

#def ART():


def update_hp_rd(HP, RD):
    global rd_up, hp_up, oasis, norma, flag_radic, flag_anomaly, radic_up, oasis_up, anomaly_up, arm_psy, arm_anom, arm_rad, regen, regen_up, block_time, block_psy, block_rad, block_anom, art1, art2, art3, art4, art5, art_up, flag_art
    rd_up += 1
    hp_up += 1
    if flag_art:
        art_up += 1
    orig_HP, orig_RD = HP, RD
    send_packets = []  # Список байтовых команд, которые нужно отправить
    #if HP <= 0:
    #    norma = False
    #   HP = 0
        #send_packets.append(bytes([0x5A, 0xA5, 0x07, 0x82, 0x00, 0x84, 0x5A, 0x01, 0x00, 0x10]))
    if flag_art and art_up >= 60:
        art_values = [art1, art2, art3, art4, art5]
        art_addresses = [0x7000, 0x7001, 0x7002, 0x7003, 0x7004]

        for i in range(5):
            if art_values[i] > 0:
                art_values[i] -= 1
                if art_values[i] == 0:
                    int_write(art_addresses[i], 27)  # сменить иконку на "пусто"

        art1, art2, art3, art4, art5 = art_values
        art_up = 0
         # Проверка: остались ли артефакты
        if all(val == 0 for val in art_values):
            flag_art = False   

    if block_time > 0:
        block_time -= 1
        int_write(0x5324, block_time)
        if block_time == 0:
            block_anom = False
            block_psy = False
            block_rad = False
            int_write(0x6100, 0) ## Номер иконки
            uart.block_time = block_time    
    if not flag_anomaly and not flag_radic:
        if regen > 0:
            regen_up += 1
            HP += 3
            if HP > 10000:
                HP = 10000
            if regen_up >= 30:
                regen = max(0, round(regen - 0.1, 1))
                uart.regen = regen
                regen_up = 0           
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
        #elif arm_rad == 0 and arm_anom == 0 and arm_psy == 0:
        #    int_write(0x6010, 6)
    changed = (HP != orig_HP) or (RD != orig_RD)
    print(f"[DEBUG] update_hp_rd: orig_HP={orig_HP}, orig_RD={orig_RD}, new_HP={HP}, new_RD={RD}, changed={changed}")
    return HP, RD, changed, send_packets

def radic():
    global RD, HP, flag_radic, arm_rad, block_rad
    if not block_rad:
        flag_radic = True
        if arm_rad > 0:
            rd_change = 100 * (1 - arm_rad / 100)
            hp_change = 50 * (1 - arm_rad / 100)
            RD += round(rd_change)
            HP -= round(hp_change)
            arm_rad = max(0, round(arm_rad - 0.1, 1))
            uart.arm_rad = arm_rad
        else:
            RD += 100
            HP -= 50


def resp():
    global oasis, oasis_up
    oasis_up = 1
    oasis = True

def anomaly():
    global RD, HP, flag_anomaly, arm_anom, block_anom
    if not block_anom:
        flag_anomaly = True
        if arm_anom > 0:
            rd_change = 100 * (1 - arm_anom / 100)
            hp_change = 80 * (1 - arm_anom / 100)
            RD += round(rd_change)
            HP -= round(hp_change)
            arm_anom = max(0, round(arm_anom - 0.1, 1))
            uart.arm_anom = arm_anom
        else:
            RD += 150
            HP -= 80

def psy():
    print("PSY")

def KDA():
    global number_pda, jdy_ser
    message = f"KDA {number_pda} POISK"
    print(f"[KDA] 📡 {message}")
    try:
        jdy_ser.write((message + "\n").encode("utf-8"))
        print(f"[KDA] ⬅️ отправка: {message}")
    except Exception as e:
        print(f"[KDA] ⚠️ Ошибка отправки: {e}")

def load_params(filename):
    with open(filename, "r") as f:
        data = json.load(f)
    return data

def save_params(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def main():
    global HP, RD, antirad, params, vodka, bint, apteka20, apteka30, apteka50, number_pda, current_nik, arm_anom, arm_psy, arm_rad, regen, Jacket, Merc, Exoskeleton, Seva, Stalker, Ecologist, B190, Drink, Psy_block, Ip2, Anabiotic, block_time, block_psy, block_rad, block_anom
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
    regen = params["Regen"]

    for med in params.get("Medicina", []):
        if med["name"] == "B190":
            B190 = med["count"]
    for med in params.get("Medicina", []):
        if med["name"] == "Drink":
            Drink = med["count"]
    for med in params.get("Medicina", []):
        if med["name"] == "Psy_block":
            Psy_block = med["count"]
    for med in params.get("Medicina", []):
        if med["name"] == "Ip2":
            Ip2 = med["count"]

    for med in params.get("Medicina", []):
        if med["name"] == "Antirad":
            antirad = med["count"]
    for med in params.get("Medicina", []):
        if med["name"] == "Vodka":
            vodka = med["count"]
    for med in params.get("Medicina", []):
        if med["name"] == "Anabiotic":
            Anabiotic = med["count"]

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
    for med in params.get("Medicina", []):
        if med["name"] == "Merc":
            Merc = med["count"]
    for med in params.get("Medicina", []):
        if med["name"] == "Exoskeleton":
            Exoskeleton = med["count"] 
    for med in params.get("Medicina", []):
        if med["name"] == "Seva":
            Seva = med["count"]
    for med in params.get("Medicina", []):
        if med["name"] == "Stalker":
            Stalker = med["count"]
    for med in params.get("Medicina", []):
        if med["name"] == "Ecologist":
            Ecologist = med["count"]                              

    uart.HP = HP
    uart.RD = RD
    uart.arm_psy = arm_psy
    uart.arm_rad = arm_rad
    uart.arm_anom = arm_anom
    uart.regen = regen

    uart.B190 = B190
    uart.Drink = Drink
    uart.Ip2 = Ip2
    uart.Psy_block = Psy_block

    uart.antirad = antirad
    uart.vodka = vodka
    uart.Anabiotic = Anabiotic

    uart.bint = bint
    uart.apteka20 = apteka20
    uart.apteka30 = apteka30
    uart.apteka50 = apteka50

    uart.Jacket = Jacket
    uart.Merc = Merc
    uart.Seva = Seva
    uart.Stalker = Stalker
    uart.Ecologist = Ecologist
    uart.Exoskeleton = Exoskeleton
    uart.current_nik = current_nik
    uart.send_text = send_text
    uart.params = params
    uart.KDA = KDA
    uart.jdy_ser = jdy_ser

    buffer = bytearray()
    tcount = 0
    last_byte_time = time.time()
    last_update = time.monotonic()
    save_counter = 0
    need_save = False

    while True:
        if not jdy_send_queue.empty():
            msg = jdy_send_queue.get()
            try:
                if jdy_ser.is_open:
                    print(f"[KDA] ⬅️ отправка: {msg}")
                    jdy_ser.write((msg + "\n").encode("utf-8"))
                    jdy_ser.flush()
                else:
                    print("[KDA] ❌ Порт закрыт")
            except Exception as e:
                print("[KDA] ⚠️ Ошибка отправки:", e)
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
                            #uart.process_packet(packet, send_text, int_write, KDA)
                            HP, RD, Jacket, Merc, Exoskeleton, Seva, Stalker, Ecologist, arm_rad, arm_psy, arm_anom, regen, B190, Drink, Ip2, Psy_block, Anabiotic, block_rad, block_anom, block_psy, block_time = uart.process_packet(packet, send_text, int_write, KDA)
                            antirad, vodka = uart.antirad, uart.vodka
                            bint = uart.bint
                            apteka20, apteka30, apteka50 = uart.apteka20, uart.apteka30, uart.apteka50
                            Exoskeleton = uart.Exoskeleton
                            Seva = uart.Seva
                            Stalker = uart.Stalker
                            Ecologist = uart.Ecologist
                            Anabiotic = uart.Anabiotic
                            B190 = uart.B190
                            Drink = uart.Drink
                            Ip2 = uart.Ip2
                            Psy_block = uart.Psy_block
                            block_time = uart.block_time
                            block_psy = uart.block_psy
                            block_rad = uart.block_rad
                            block_anom = uart.block_anom
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
                    if decoded == "PSY":
                        psy()
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
            params["Regen"] = regen
            for med in params.get("Medicina", []): # записал в файл
                
                if med["name"] == "Antirad":
                    med["count"] = antirad
                elif med["name"] == "Vodka":
                    med["count"] = vodka
                elif med["name"] == "Anabiotic":
                    med["count"] = Anabiotic

                elif med["name"] == "B190":
                    med["count"] = B190
                elif med["name"] == "Drink":
                    med["count"] = Drink
                elif med["name"] == "Ip2":
                    med["count"] = Ip2
                elif med["name"] == "Psy_block":
                    med["count"] = Psy_block    

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
                elif med ["name"] == "Merc":
                    med["count"] = Merc
                elif med ["name"] == "Exoskeleton":
                    med ["count"] = Exoskeleton
                elif med ["name"] == "Seva":
                    med ["count"] = Seva
                elif med ["name"] == "Stalker":
                    med ["count"] = Stalker
                elif med ["name"] == "Ecologist":
                    med ["count"] = Ecologist    
      
            for packet in packets:   # обновляю на экран
                ser.write(packet)
            int_write(0x5000, HP)
            int_write(0x5001, RD)
            int_write(0x5301, antirad)
            int_write(0x5302, vodka)
            int_write(0x5303, Anabiotic)

            int_write(0x5304, B190)
            int_write(0x5307, Drink)
            int_write(0x5306, Ip2)
            int_write(0x5305, Psy_block)

            int_write(0x5308, bint)
            int_write(0x5309, apteka20)
            int_write(0x5310, apteka30)
            int_write(0x5311, apteka50)

            int_write(0x5312, Jacket)
            int_write(0x5313, Merc)
            int_write(0x5316, Exoskeleton)
            int_write(0x5315, Seva)
            int_write(0x5314, Stalker)
            int_write(0x5317, Ecologist)

            int_write(0x7010, art1)
            int_write(0x7011, art2)
            int_write(0x7012, art3)
            int_write(0x7013, art4)
            int_write(0x7014, art5)

            int_write(0x5321, int(arm_rad * 10))
            int_write(0x5320, int(regen * 10))
            int_write(0x5323, int(arm_psy * 10))
            int_write(0x5322, int(arm_anom * 10))
            
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
                all_params[number_key]["Regen"] = regen 
                known_meds = {  
                    "Antirad": antirad,
                    "Vodka": vodka,
                    "Anabiotic": Anabiotic,

                    "B190": B190,
                    "Drink": Drink,
                    "Ip2": Ip2,
                    "Psy_block": Psy_block,
                    
                    "Bint": bint,
                    "Apteka20": apteka20,
                    "Apteka30": apteka30,
                    "Apteka50": apteka50,

                    "Jacket": Jacket,
                    "Merc": Merc,
                    "Exoskeleton": Exoskeleton,
                    "Seva": Seva,
                    "Stalker": Stalker,
                    "Ecologist": Ecologist
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