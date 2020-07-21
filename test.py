import time
import os
from threading import Thread
# from multiprocessing import Process
import serial
ser = serial.Serial("com3",baudrate=115200)
def write(ser):
    while True:
        ser.write("data".encode("utf-8"))
        time.sleep(1)

def read(ser):
    while True:
        print(ser.read(4).decode("utf-8"))
        time.sleep(1)

if __name__ == '__main__':
    # Thread(target=write,args=(ser,)).start()
    # Thread(target=read,args=(ser,)).start()
    # print(ser)
    # import time
    # start = time.time()
    # time.sleep(1)
    # end = time.time()
    # print(end-start)
    print(ser)