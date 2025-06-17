import serial
import time

serial_port = "/dev/ttyS5"
baud_rate = 115200

def process_packet(packet):
    global HP, RD, antirad, params, vodka, bint, apteka20, apteka30, apteka50, current_nik
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
                        print("Нет водки в запасе!")
                elif value == 0:
                    print("СОСТОЯНИЕ: ВЫКЛЮЧЕНО (OFF)")
            elif vp == 0x5600:
                if value == 1:
                    if bint > 0:
                        print("используем бинт")  
                        bint -= 1   
                        for med in params.get("Medicina", []):
                            if med["name"] == "Bint":  
                                med["count"] = bint
                                break 
                        HP += 1000 
                        if HP > 10000: HP = 10000
                    else:
                         print("Нет бинтов в запасе!")  
            elif vp == 0x5601:
                if value == 1:
                    if apteka20 > 0:
                        print("используем Аптека20")  
                        apteka20 -= 1   
                        for med in params.get("Medicina", []):
                            if med["name"] == "Apteka20":  
                                med["count"] = apteka20
                                break 
                        HP += 2000 
                        if HP > 10000: HP = 10000
                    else:
                         print("Нет Аптека20 в запасе!") 
            elif vp == 0x5602:
                if value == 1:
                    if apteka30 > 0:
                        print("используем Аптека30")  
                        apteka30 -= 1   
                        for med in params.get("Medicina", []):
                            if med["name"] == "Apteka30":  
                                med["count"] = apteka30
                                break 
                        HP += 3000 
                        if HP > 10000: HP = 10000
                    else:
                         print("Нет Аптека30 в запасе!")
            elif vp == 0x5603:
                if value == 1:
                    if apteka50 > 0:
                        print("используем Аптека50")  
                        apteka50 -= 1   
                        for med in params.get("Medicina", []):
                            if med["name"] == "Apteka50":  
                                med["count"] = apteka50
                                break 
                        HP += 5000
                        RD -= 3000
                        if HP > 10000: HP = 10000
                        if RD < 0: RD = 0
                    else:
                         print("Нет Аптека50 в запасе!")
            elif vp == 0x5950:
                if 'send_text' in globals():
                    try:
                        send_text(0x5970, current_nik)
                        print(f"📤 Ник '{current_nik}' отправлен в 0x5970")
                    except Exception as e:
                        print(f"❌ Ошибка при отправке ника: {e}")
                else:
                    print("⚠️ send_text не задан")                            
            else:
                print(f"VP 0x{vp:04X}: значение {value}")
        else:
            print("Пакет нераспознан или слишком короткий:", packet.hex())
    else:
        print("Пакет не DWIN или нераспознан")

def main():
    with serial.Serial(serial_port, baudrate=baud_rate, timeout=0.01) as ser:
        buffer = bytearray()
        while True:
            data = ser.read(64)  # Сразу читаем побольше, если есть
            if data:
                buffer += data
            # Парсим все возможные пакеты в буфере
            while len(buffer) >= 3:
                # Ищем начало пакета
                if buffer[0] != 0x5A or buffer[1] != 0xA5:
                    buffer = buffer[1:]  # Убираем мусор до заголовка
                    continue
                plen = buffer[2]
                packet_len = plen + 3
                if len(buffer) < packet_len:
                    break  # Ждём, пока весь пакет придёт
                packet = buffer[:packet_len]
                process_packet(packet)
                buffer = buffer[packet_len:]  # Удаляем обработанное

            time.sleep(0.001)