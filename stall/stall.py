import serial
import time

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
    print(f'Send to {hex(addr)}:', packet.hex())
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
        ser.write(packet)
        response = ser.read(32)
        print('Ответ:', response.hex())

HP = 0
RD = 1000

while True:
    # Увеличиваем HP
    if HP < 10000:
        HP += 1

    # Уменьшаем RD
    if 0 < RD < 4000:
        RD -= 1

    # Отправляем значения
    int_write(0x5000, HP)   # VP = 0x5000
    int_write(0x5001, RD)   # VP = 0x5001 (создай такую переменную в редакторе!)

    print(f'HP = {HP}, RD = {RD}')
    time.sleep(1)
