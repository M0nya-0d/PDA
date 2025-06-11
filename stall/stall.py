import serial
import time
import json

serial_port = "/dev/ttyS5"
baud_rate = 115200

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

def update_hp_rd(HP, RD):
    if 0 < RD < 4000:
        RD -= 1
        if HP < 10000:
            HP += 1
    elif 4000 < RD < 7000:
        RD -= 1
    elif 7000 < RD < 8000:
        HP -= 10
        if HP < 0:
            HP = 0
    elif 8000 < RD < 9000:
        HP -= 20
        if HP < 0:
            HP = 0
    return HP, RD

def load_params(filename):
    with open(filename, "r") as f:
        data = json.load(f)
    return data["HP"], data["RD"]

def main():
    # Загружаем стартовые параметры из файла
    HP, RD = load_params("param.json")
    print(f"Стартовые значения: HP = {HP}, RD = {RD}")

    last_update = time.monotonic()
    while True:
        now = time.monotonic()
        if now - last_update >= 1.0:
            last_update = now
            HP, RD = update_hp_rd(HP, RD)
            int_write(0x5000, HP)
            int_write(0x5001, RD)
            print(f'HP = {HP}, RD = {RD}')
        # Здесь могут быть другие задачи
        time.sleep(0.01)

if __name__ == "__main__":
    main()
