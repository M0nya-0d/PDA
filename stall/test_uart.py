import serial
import time

ser = serial.Serial("/dev/ttyS2", 9600)

while True:
    ser.write(b"Hello from TX2\n")
    time.sleep(1)