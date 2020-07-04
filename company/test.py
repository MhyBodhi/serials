import time
import serial
ser = serial.Serial("/dev/ttyXRUSB0")
while True:
    ser.write("data".encode("utf-8"))
    print("缓冲区大小",ser.in_waiting)
    time.sleep(1)