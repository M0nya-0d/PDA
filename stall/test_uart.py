import serial
import time

ser = serial.Serial("/dev/ttyS1", 9600)

while True:
    ser.write(b"Hello from TX2\n")
    time.sleep(10)