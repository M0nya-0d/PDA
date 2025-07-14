from doctest import COMPARISON_FLAGS
from email.iterators import typed_subpart_iterator
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

art1 = art2 = art3 = art4 = art5 = 0
art1_name = art2_name = art3_name = art4_name = art5_name = ""
last_device_type = None
last_device_number = None
active_arts = [None, None]
device_jpg = 0
art_up = 0
flag_art = True
rad_stat = 0
regen_stat = 0
anom_stat = 0
psy_stat = 0
RD_stat = 0

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

uart.last_device_type = last_device_type
uart.current_nik = current_nik
uart.params = params


jdy_port = "/dev/ttyUSB0"
jdy_baud = 9600
jdy_ser = serial.Serial(jdy_port, baudrate=jdy_baud, timeout=0.1)
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
    global rd_up, hp_up, oasis, norma, flag_radic, flag_anomaly, radic_up, oasis_up, anomaly_up, arm_psy, arm_anom, arm_rad, regen, regen_up, block_time, block_psy, block_rad, block_anom, art1, art2, art3, art4, art5, art_up, flag_art, art1_name, art2_name, art3_name, art4_name, art5_name, rad_stat, anom_stat, regen_stat, psy_stat, RD_stat
    rd_up += 1
    hp_up += 1
    if flag_art:
        art_up += 1
    orig_HP, orig_RD = HP, RD
    if RD_stat > 0:
        RD = RD + RD_stat
    send_packets = []  # Список байтовых команд, которые нужно отправить
    #if HP <= 0:
    #    norma = False
    #   HP = 0
        #send_packets.append(bytes([0x5A, 0xA5, 0x07, 0x82, 0x00, 0x84, 0x5A, 0x01, 0x00, 0x10]))
    if flag_art and art_up >= 60:
        art_values = [art1, art2, art3, art4, art5]
        art_names  = [art1_name, art2_name, art3_name, art4_name, art5_name]
        art_addresses = [0x7000, 0x7001, 0x7002, 0x7003, 0x7004]

        for i in range(5):
            if art_values[i] > 0:
                art_values[i] -= 1
                if art_values[i] == 0:
                    globals()[f"art{i+1}_name"] = art_names[i]
                    art_efeckt(f"DROP {i+1}")
                    int_write(art_addresses[i], 27)

        # Возврат значений в глобальные переменные
        art1, art2, art3, art4, art5 = art_values
        art1_name, art2_name, art3_name, art4_name, art5_name = art_names
        art_up = 0

        # Проверка: все ли слоты пусты
        if all(val == 0 for val in art_values):
            flag_art = False
            int_write(0x6011, 0)

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
        if regen > 0 and regen_stat > 0:
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
            if hp_up >= 3:    
                if HP < 10000:
                    HP += 1
                    hp_up = 0
        elif RD > 1000 and RD <= 4000:
            if rd_up >= 3:
                RD -= 1
                rd_up = 0
            if hp_up >= 4:
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
    global RD, HP, flag_radic, arm_rad, block_rad, rad_stat, RD_stat
    if not block_rad:
        flag_radic = True
        arm_rad = min(100, arm_rad + RD_stat)
        if arm_rad > 0:
            rd_change = 100 * (1 - arm_rad / 100)
            hp_change = 50 * (1 - arm_rad / 100)
            RD += round(rd_change)
            HP -= round(hp_change)
            arm_rad = max(0, arm_rad - RD_stat)
            arm_rad = max(0, round(arm_rad - 0.1, 1))
            uart.arm_rad = arm_rad
        else:
            RD += 100
            HP -= 50

def art_type(device_type):
    global last_device_type
    last_device_type = device_type
    handlers = {
        "COMPAS": lambda: int_write(0x7005, 3),
        "BATARY": lambda: int_write(0x7005, 13),
        "KAPLYA": lambda: int_write(0x7005, 7),
        "BUBBLE": lambda: int_write(0x7005, 6),
        "FLAME": lambda: int_write(0x7005, 9),
        "JOKER": lambda: int_write(0x7005, 15),
        "GOLD": lambda: int_write(0x7005, 18),
        "SHADOW": lambda: int_write(0x7005, 11),
        "STORM": lambda: int_write(0x7005, 17),
        "CRYSTAL": lambda: int_write(0x7005, 5),
        
    }

    if device_type in handlers:
        #print(f"[ART TYPE] 🎯 Обработка типа устройства: {device_type}")
        handlers[device_type]()
    else:
        print(f"[ART TYPE] ❌ Неизвестный тип устройства: {device_type}")




def art_uron(device_type):
    global RD
    uron = {
        "COMPAS": lambda: 3,
        "BATARY": lambda: 3,
        "KAPLYA": lambda: 4,
        "BUBBLE": lambda: 3,
        "FLAME": lambda: 5,
        "JOKER": lambda: 5,
        "GOLD": lambda: 3,
        "SHADOW": lambda: 3,
        "STORM": lambda: 4,
        "CRYSTAL": lambda: 1,
    }

    if device_type in uron:
        damage = uron[device_type]()
        RD += damage
        print(f"[URON] +{damage} RD от {device_type}. Итого RD: {RD}")
    else:
        print(f"[URON] Неизвестный тип устройства: {device_type}") 

def art_efeckt(device_type):
    global last_device_number, last_device_type, flag_art 
    global art1, art2, art3, art4, art5
    global art1_name, art2_name, art3_name, art4_name, art5_name
    global rad_stat, regen_stat, psy_stat, anom_stat, RD_stat
    flag_art = True
    # Название артефакта -> номер картинки, эффект и удаление эффекта
    artifacts = {
        # (3, 1000, 0, 0), (+10 rad, +10 psy, +50 regen, +30 anom, +2 RD)
        "COMPAS": {
            "value": 3,
            "effect": lambda: apply_effect(100, 100, 50, 30, 2), # далает  +
            "remove": lambda: apply_effect(-100, -100, -50, -30, -2), # далает -
        },
        "BATARY": {
            "value": 4,
            "effect": lambda: apply_effect(800, 0, 1, 500, 4),
            "remove": lambda: apply_effect(-880, 0, -1, -500, -4),
        },
        "KAPLYA": {
            "value": 5,
            "effect": lambda: apply_effect(0, 500, 0, 1000, 3),
            "remove": lambda: apply_effect(0, -500, 0, -1000, -3),
        },
        "FLAME": {
            "value": 6,
            "effect": lambda: apply_effect(4, 1500, 0, 0, 3),
            "remove": lambda: apply_effect(-4, -1500, 0, 0, -3),
        },
        "JOKER": {
            "value": 7,
            "effect": lambda: apply_effect(0, 0, 5, 2000, 3),
            "remove": lambda: apply_effect(0, 0, -5, -2000, -3),
        },
    }

    # Слоты: (счетчик, имя переменной, имя артефакта, адрес)
    art_slots = [
        ("art1", "art1_name", 0x7000),
        ("art2", "art2_name", 0x7001),
        ("art3", "art3_name", 0x7002),
        ("art4", "art4_name", 0x7003),
        ("art5", "art5_name", 0x7004),
    ]

    # === DROP N ===
    if device_type.startswith("DROP "):
        try:
            index = int(device_type.split()[1]) - 1
            if 0 <= index < 5:
                var_name, name_var, addr = art_slots[index]
                if globals()[var_name] != 0:
                    art_name = globals()[name_var]
                    if art_name in artifacts:
                        artifacts[art_name]["remove"]()
                    globals()[var_name] = 0
                    globals()[name_var] = ""
                    int_write(addr, 27)
        except:
            pass
        return

    # === USE XXX ===
    name = device_type.replace(" USE", "")
    if name not in artifacts:
        return
    int_write(0x7005, 31)

    for var_name, name_var, addr in art_slots:
        if globals()[var_name] == 0:
            globals()[var_name] = 4   # минут эффекта
            globals()[name_var] = name
            int_write(addr, artifacts[name]["value"])
            artifacts[name]["effect"]()
            int_write(0x6011, 1)
            print(last_device_type)
            print(last_device_number)
            if last_device_type and last_device_number:
                use_command = f"{last_device_type}{last_device_number}use"
                jdy_send_queue.put(use_command)
                print(use_command)
            break

def apply_effect(rad=0, psy=0, regen=0, anom=0, rd=0):
    global rad_stat, psy_stat, regen_stat, anom_stat, RD_stat
    rad_stat += rad
    psy_stat += psy
    regen_stat += regen
    anom_stat += anom
    RD_stat += rd

         

def resp():
    global oasis, oasis_up
    oasis_up = 1
    oasis = True

def anomaly():
    global RD, HP, flag_anomaly, arm_anom, block_anom, anom_stat
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

def KDA(device_type, device_number):
    global active_arts, last_device_type, last_device_number, number_pda, jdy_send_queue

    last_device_type = device_type
    last_device_number = device_number

    # Таблица соответствия типов и номеров картинок
    image_map = {
        "COMPAS": 3,
        "BATARY": 13,
        "KAPLYA": 7,
        "BUBBLE": 6,
        "FLAME": 9,
        "JOKER": 15,
        "GOLD": 18,
        "SHADOW": 11,
        "STORM": 17,
        "CRYSTAL": 5
    }

    img_code = image_map.get(device_type, 0)
    if img_code == 0:
        print(f"[ART] ❌ Неизвестный тип: {device_type}")
        return

    # Проверка и регистрация в слот
    if active_arts[0] is None:
        active_arts[0] = device_type  # сохраняем только тип
        int_write(0x7006, img_code)
        print(f"[ART] ✅ Слот 1: {device_type}{device_number}, картинка {img_code}")
    elif active_arts[1] is None:
        active_arts[1] = device_type  # сохраняем только тип
        int_write(0x7007, img_code)
        print(f"[ART] ✅ Слот 2: {device_type}{device_number}, картинка {img_code}")
    else:
        print("[ART] ⚠️ Нет свободных слотов")
        return

    # Подготовка и отправка команды сохранения
    message = f"KDA {number_pda} {device_type}{device_number}save"
    print(f"[ART] 📡 Подготовлено к отправке: {message}")

    try:
        jdy_send_queue.put(message)
        print(f"[ART] ⬅️ Добавлено в очередь: {message}")
    except Exception as e:
        print(f"[ART] ⚠️ Ошибка при добавлении в очередь: {e}")





def load_params(filename):
    with open(filename, "r") as f:
        data = json.load(f)
    return data

def save_params(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def main():
    global HP, RD, antirad, params, vodka, bint, apteka20, apteka30, apteka50, number_pda, current_nik, arm_anom, arm_psy, arm_rad, regen, Jacket, Merc, Exoskeleton, Seva, Stalker, Ecologist, B190, Drink, Psy_block, Ip2, Anabiotic, block_time, block_psy, block_rad, block_anom, number_pda, last_device_type, last_device_number
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
    uart.last_device_type = last_device_type
    

    buffer = bytearray()
    tcount = 0
    last_byte_time = time.time()
    last_update = time.monotonic()
    save_counter = 0
    need_save = False

    while True:
        jdy_buffer = ""
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
                            HP, RD, Jacket, Merc, Exoskeleton, Seva, Stalker, Ecologist, arm_rad, arm_psy, arm_anom, regen, B190, Drink, Ip2, Psy_block, Anabiotic, block_rad, block_anom, block_psy, block_time, last_device_type = uart.process_packet(packet, send_text, int_write, KDA, art_efeckt)
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
                valid_artifacts = {
                    "COMPAS", "BATARY", "KAPLYA", "BUBBLE", "FLAME",
                    "JOKER", "GOLD", "SHADOW", "STORM", "CRYSTAL"}
                while jdy_ser.in_waiting:
                    try:
                        line = jdy_ser.readline().decode(errors='ignore').strip()
                        if line:
                            print(f"[JDY-40] 📶 Получено: {line}")
                            if line == "Radic-1":
                                radic()
                            elif line == "Oasis":
                                resp()
                            elif line == "Anomaly":
                                anomaly()
                            elif line == "PSY":
                                psy()   
                            elif any(line.startswith(prefix) for prefix in valid_artifacts):
                                parts = line.split()
                                if len(parts) == 2:
                                    type_device, device_number = parts
                                    if type_device in valid_artifacts:
                                        print(f"[JDY] 🔍 Найден артефакт: {type_device} с номером {device_number}")
                                        last_device_type = type_device
                                        last_device_number = device_number
                                        uart.last_device_type = last_device_type
                                        uart.last_device_number = last_device_number
                                        art_type(type_device)
                                        art_uron(type_device)
                                        
                                        
                                    else:
                                        print(f"[JDY] ⚠️ Неизвестный тип артефакта: {type_device}") 
                            elif line.startswith("PDA"):
                                parts = line.split()
                                if len(parts) >= 3:
                                    prefix, id_str, type_device = parts[0], parts[1], parts[2]
                                    try:
                                        if int(id_str) == number_pda:
                                            print(f"[PDA] ✅ Это для нас. Тип устройства: {type_device}")
                                            art_type(type_device)
                                    except ValueError:
                                        print("[PDA] ⚠️ Неверный формат ID")
                    except Exception as e:
                        print(f"[JDY-40] ⚠️ Ошибка чтения: {e}")

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

            int_write(0x5321, int(arm_rad * 10) + rad_stat)
            int_write(0x5320, int(regen * 10) + regen_stat)
            int_write(0x5323, int(arm_psy * 10) + psy_stat)
            int_write(0x5322, int(arm_anom * 10) + anom_stat)
            
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