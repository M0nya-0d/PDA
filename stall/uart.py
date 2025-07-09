import serial
import time
import subprocess
import uart

serial_port = "/dev/ttyS5"
baud_rate = 115200

def process_packet(packet, send_text, int_write):
    global HP, RD, antirad, params, vodka, bint, apteka20, apteka30, apteka50, current_nik, number_pda, arm_rad, arm_psy, arm_anom, regen, Jacket, Merc, Exoskeleton, Seva, Stalker, Ecologist, B190, Drink, Ip2, Psy_block, Anabiotic, block_rad, block_anom, block_psy, block_time
    default_return = (HP, RD, Jacket, Merc, Exoskeleton, Seva, Stalker, Ecologist, arm_rad, arm_psy, arm_anom, regen)
    if not (packet[0] == 0x5A and packet[1] == 0xA5):
        print("Пакет не DWIN или нераспознан")
        return HP, RD, Jacket, Merc, Exoskeleton, Seva, Stalker, Ecologist, arm_rad, arm_psy, arm_anom, regen, B190, Drink, Ip2, Psy_block, Anabiotic, block_rad, block_anom, block_psy, block_time

    if len(packet) < 9 or packet[3] != 0x83:
        print("Пакет нераспознан или слишком короткий:", packet.hex())
        return HP, RD, Jacket, Merc, Exoskeleton, Seva, Stalker, Ecologist, arm_rad, arm_psy, arm_anom, regen, B190, Drink, Ip2, Psy_block, Anabiotic, block_rad, block_anom, block_psy, block_time

    vp = (packet[4] << 8) | packet[5]
    value = packet[8]

    # === Jacket (arm_rad += 10) ===
    #if vp == 0x5651 and value == 1:
    #    print("🛡️ Используем Jacket — добавляем защиту от радиации")
    #    arm_rad += 10
    #    return

    # === Медикаменты ===
    med_actions = {
        0x5501: ("Antirad", 7000, 2000),
        0x5502: ("Vodka", 1000, 1000),
        0x5661: ("Anabiotic", 0, 0),

        0x5658: ("B190", 0, 0),
        0x5657: ("Drink", 0, 0),
        0x5660: ("Ip2", 0, 0),
        0x5659: ("Psy_block", 0, 0),

        0x5600: ("Bint", 0, -1000),
        0x5601: ("Apteka20", 0, -2000),
        0x5602: ("Apteka30", 0, -3000),
        0x5603: ("Apteka50", 3000, -5000),

        0x5651: ("Jacket", 0, 0),
        0x5652: ("Merc", 0, 0),
        0x5653: ("Exoskeleton", 0, 0),
        0x5654: ("Seva", 0, 0),
        0x5655: ("Stalker", 0, 0),
        0x5656: ("Ecologist", 0, 0),

    }

    if vp in med_actions and value == 1:
        name, rd_change, hp_change = med_actions[vp]
        count = {
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

        }.get(name, 0)

        if count > 0:
            print(f"используем {name}")
            count -= 1
            RD = max(0, RD - rd_change)
            HP = max(0, HP - hp_change) if hp_change > 0 else min(HP - hp_change, 10000)

            for med in params.get("Medicina", []):
                if med["name"] == name:
                    med["count"] = count
                    break

            # Обновляем переменные
            if name == "Antirad":
                antirad = count
            elif name == "Vodka":
                vodka = count
            elif name == "Anabiotic":
                Anabiotic = count
                uart.Anabiotic = Anabiotic
                HP -= 3000
                RD = 0

            elif name == "B190":
                block_time = 61
                block_rad = True
                int_write(0x6100, 2) ## Номер иконки
                B190 = count
                uart.block_time = block_time
                uart.block_rad = block_rad
                
            elif name == "Drink":
                regen = 62
                params["Regen"] = regen
                Drink = count
                uart.regen = regen

            elif name == "Ip2":
                Ip2 = count
                block_time = 61
                block_anom = True
                int_write(0x6100, 3) ## Номер иконки
                uart.block_time = block_time
                uart.block_anom = block_anom

            elif name == "Psy_block":
                Psy_block = count
                block_time = 61
                block_psy = True
                int_write(0x6100, 1) ## Номер иконки
                uart.block_time = block_time
                uart.block_psy = block_psy

            elif name == "Bint":
                bint = count
            elif name == "Apteka20":
                apteka20 = count
            elif name == "Apteka30":
                apteka30 = count
            elif name == "Apteka50":
                apteka50 = count

                ##### ARMOR ############
            elif name == "Jacket":
                arm_rad = 10
                arm_anom = 0
                arm_psy = 0
                regen = 0
                int_write(0x6010, 3) ## Номер иконки
                params["Radic"] = arm_rad
                params["Anomaly"] = arm_anom
                params["PSY"] = arm_psy
                params["Regen"] = regen
                Jacket = count
                uart.Jacket = Jacket  # <-- ЭТО ОЧЕНЬ ВАЖНО
                uart.arm_rad = arm_rad
                uart.arm_anom = arm_anom
                uart.arm_psy = arm_psy
                uart.regen = regen

            elif name == "Merc":
                arm_rad = 20
                arm_anom = 10
                arm_psy = 0
                regen = 0
                int_write(0x6010, 4) ## Номер иконки
                params["Radic"] = arm_rad
                params["Anomaly"] = arm_anom
                params["PSY"] = arm_psy
                params["Regen"] = regen
                Merc = count
                uart.Merc = Merc  # <-- ЭТО ОЧЕНЬ ВАЖНО
                uart.arm_rad = arm_rad
                uart.arm_anom = arm_anom
                uart.arm_psy = arm_psy
                uart.regen = regen
            elif name == "Exoskeleton":
                arm_rad = 30
                arm_anom = 40
                arm_psy = 10
                regen = 100
                int_write(0x6010, 0) ## Номер иконки
                params["Radic"] = arm_rad
                params["Anomaly"] = arm_anom
                params["PSY"] = arm_psy
                params["Regen"] = regen
                Exoskeleton = count
                uart.Exoskeleton = Exoskeleton  # <-- ЭТО ОЧЕНЬ ВАЖНО
                uart.arm_rad = arm_rad
                uart.arm_anom = arm_anom
                uart.arm_psy = arm_psy
                uart.regen = regen
            elif name == "Seva":
                arm_rad = 50
                arm_anom = 40
                arm_psy = 30
                regen = 0
                int_write(0x6010, 2) ## Номер иконки
                params["Radic"] = arm_rad
                params["Anomaly"] = arm_anom
                params["PSY"] = arm_psy
                params["Regen"] = regen
                Seva = count
                uart.Seva = Seva  # <-- ЭТО ОЧЕНЬ ВАЖНО
                uart.arm_rad = arm_rad
                uart.arm_anom = arm_anom
                uart.arm_psy = arm_psy
                uart.regen = regen
            elif name == "Stalker":
                arm_rad = 30
                arm_anom = 20
                arm_psy = 10
                regen = 0
                int_write(0x6010, 5) ## Номер иконки
                params["Radic"] = arm_rad
                params["Anomaly"] = arm_anom
                params["PSY"] = arm_psy
                params["Regen"] = regen
                Stalker = count
                uart.Stalker = Stalker  # <-- ЭТО ОЧЕНЬ ВАЖНО
                uart.arm_rad = arm_rad
                uart.arm_anom = arm_anom
                uart.arm_psy = arm_psy
                uart.regen = regen
            elif name == "Ecologist":
                arm_rad = 80
                arm_anom = 60
                arm_psy = 40
                regen = 0 
                int_write(0x6010, 1) ## Номер иконки
                params["Radic"] = arm_rad
                params["Anomaly"] = arm_anom
                params["PSY"] = arm_psy
                params["Regen"] = regen
                Ecologist = count
                uart.Ecologist = Ecologist  # <-- ЭТО ОЧЕНЬ ВАЖНО
                uart.arm_rad = arm_rad
                uart.arm_anom = arm_anom
                uart.arm_psy = arm_psy
                uart.regen = regen

        else:
            print(f"Нет {name} в запасе!")

    elif vp == 0x5950:
        try:
            send_text(0x5970, current_nik)
            print(f"📤 Ник '{current_nik}' отправлен в 0x5970")

            int_write(0x5960, number_pda)
            print(f"📤 number_pda = {number_pda} отправлен в 0x5960")

            result = subprocess.run(['ping', '-c', '1', '-W', '1', '8.8.8.8'], stdout=subprocess.DEVNULL)
            if result.returncode == 0:
                print("🌐 Интернет доступен")
                int_write(0x5950, 1)
                int_write(0x5965, 1)
            else:
                print("❌ Нет интернета")
                int_write(0x5950, 0)
                int_write(0x5965, 0)
        except Exception as e:
            print(f"❌ Ошибка при отправке: {e}")

    elif vp == 0x5940 and value == 1:
        result = subprocess.run(['ping', '-c', '1', '-W', '1', '8.8.8.8'], stdout=subprocess.DEVNULL)
        if result.returncode == 0:
            try:
                subprocess.run(['/bin/bash', '/home/orangepi/PDA/update_pda.sh'], check=True)
                print("🔄 Обновление выполнено")
            except subprocess.CalledProcessError as e:
                print(f"❌ Ошибка при запуске update_pda.sh: {e}")
        else:
            print("❌ Интернет недоступен, обновление отменено")

    else:
        print(f"VP 0x{vp:04X}: значение {value}")
    return HP, RD, Jacket, Merc, Exoskeleton, Seva, Stalker, Ecologist, arm_rad, arm_psy, arm_anom, regen, B190, Drink, Ip2, Psy_block, Anabiotic, block_rad, block_anom, block_psy, block_time    
