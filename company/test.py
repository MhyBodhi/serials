import time
import serial
ser = serial.Serial("com7",115200)
def write(ser):
    while True:
        ser.write("data".encode("utf-8"))
        time.sleep(1)

if __name__ == '__main__':
    write(ser)
