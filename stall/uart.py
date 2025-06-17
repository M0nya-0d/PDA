import serial
import time
import subprocess

serial_port = "/dev/ttyS5"
baud_rate = 115200

def process_packet(packet, send_text, int_write):
    global HP, RD, antirad, params, vodka, bint, apteka20, apteka30, apteka50, current_nik, number_pda
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
                        RD = max(0, RD - 7000)
                        HP = max(0, HP - 2000)
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
                        RD = max(0, RD - 1000)
                        HP = max(0, HP - 1000)
                    else:
                        print("Нет водки в запасе!")
                elif value == 0:
                    print("СОСТОЯНИЕ: ВЫКЛЮЧЕНО (OFF)")
            elif vp == 0x5600 and value == 1 and bint > 0:
                print("используем бинт")  
                bint -= 1
                for med in params.get("Medicina", []):
                    if med["name"] == "Bint":
                        med["count"] = bint
                        break
                HP = min(HP + 1000, 10000)
            elif vp == 0x5601 and value == 1 and apteka20 > 0:
                print("используем Аптека20")  
                apteka20 -= 1
                for med in params.get("Medicina", []):
                    if med["name"] == "Apteka20":
                        med["count"] = apteka20
                        break
                HP = min(HP + 2000, 10000)
            elif vp == 0x5602 and value == 1 and apteka30 > 0:
                print("используем Аптека30")  
                apteka30 -= 1
                for med in params.get("Medicina", []):
                    if med["name"] == "Apteka30":
                        med["count"] = apteka30
                        break
                HP = min(HP + 3000, 10000)
            elif vp == 0x5603 and value == 1 and apteka50 > 0:
                print("используем Аптека50")  
                apteka50 -= 1
                for med in params.get("Medicina", []):
                    if med["name"] == "Apteka50":
                        med["count"] = apteka50
                        break
                HP = min(HP + 5000, 10000)
                RD = max(0, RD - 3000)
            elif vp == 0x5950:
                try:
                    send_text(0x5970, current_nik)
                    print(f"📤 Ник '{current_nik}' отправлен в 0x5970")

                    int_write(0x5960, number_pda)
                    print(f"📤 number_pda = {number_pda} отправлен в 0x5960")

        # Проверка наличия интернета (пинг до 8.8.8.8)
                    import subprocess
                    result = subprocess.run(['ping', '-c', '1', '-W', '1', '8.8.8.8'],
                                            stdout=subprocess.DEVNULL)

                    if result.returncode == 0:
                        print("🌐 Интернет доступен")
                        int_write(0x5950, 1)
                        int_write(0x5980, 1)                            
                    else:
                        int_write(0x5950, 0)
                        int_write(0x5980, 0)
                        print("❌ Нет интернета")

                except Exception as e:
                    print(f"❌ Ошибка при отправке: {e}")
            elif vp == 0x5940 and value == 1:
                import subprocess
                result = subprocess.run(['ping', '-c', '1', '-W', '1', '8.8.8.8'],
                                        stdout=subprocess.DEVNULL)
                if result.returncode == 0:
                    try:
                        subprocess.run(['/bin/bash', '/home/orangepi/PDA/update_pda.sh'], check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"❌ Ошибка при запуске update_pda.sh: {e}")
                else:
                    print("❌ Интернет недоступен, обновление отменено")
            else:
                print(f"VP 0x{vp:04X}: значение {value}")
        else:
            print("Пакет нераспознан или слишком короткий:", packet.hex())
    else:
        print("Пакет не DWIN или нераспознан")