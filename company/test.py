import time
from functools import reduce
import serial
from threading import Thread,Lock
ascii = reduce(lambda x, y: x + y, map(lambda x: chr(x), range(256)))
class Test():
    def __init__(self):
        self.ser = serial.Serial("com3", 115200,timeout=10,write_timeout=10)
        self.status = "write"
    def write(self,lock):
        while True:
            if self.status == "write":
                lock.acquire()
                sendstr = ascii.encode("utf-8")
                start = time.time()
                bytes_numbers = self.ser.write(sendstr)
                print(bytes_numbers)
                end = time.time()
                print("发送速率%.2fKB/s"%(bytes_numbers/(end-start)/1024))
                self.status = "read"
                lock.release()

    def read(self,lock):
        while True:
            if self.ser.in_waiting:
                if self.status == "read":
                    lock.acquire()
                    start = time.time()
                    self.ser.read(384).decode("utf-8")
                    end = time.time()
                    print("接收速率%.2fKB/s"%(384 / (end - start) / 1024))
                    self.status = "write"
                    lock.release()
    def run(self):
        lock = Lock()
        t1 = Thread(target=self.write, args=(lock,))
        t2 = Thread(target=self.read, args=(lock,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
if __name__ == '__main__':
    print("/home/kylin".split(","))