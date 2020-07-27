import time
import random
from company.realize.test.basic import TRSerial,logging


class Refactor(TRSerial):

    def __init__(self):
        super().__init__()
        #Ascii码测试下标
        self.count = 1

    def writeFiles(self):
        while True:
            if self.status == "write":
                self.lock.acquire()
                if self.fileenable:
                    data = self.srcfile.read(2048)
                    if data:
                        self.bytes_number = self.ser.write(data)
                        self.status = "read"
                    else:
                        if not self.ser.in_waiting:
                            self.fileenable = False
                            self.srcfile.close()
                            self.status = "write"
                            self.lock.release()
                            break
                        else:
                            self.status = "read"
                self.lock.release()

    def writeAscii(self):
        while True:
            if self.status == "write":
                self.lock.acquire()
                if self.count==1:
                    logging.info("测试单个ascii码")
                    sendstr = random.choice(self.ascii)
                    logging.info(("总的字节数", len(sendstr.encode("utf-8"))))
                    self.bytes_number = self.ser.write(sendstr.encode("utf-8"))
                    logging.info(("写入的字节数：",self.bytes_number))
                    logging.info(sendstr)
                    logging.info(("输入缓冲区：", self.ser.in_waiting))
                    self.count += 1
                elif self.count==2:
                    logging.info("测试多个ascii码")
                    sendstr = "".join(random.sample(self.ascii, random.randint(2, 255)))
                    logging.info(("总的字节数", len(sendstr.encode("utf-8"))))
                    self.bytes_number = self.ser.write(sendstr.encode("utf-8"))
                    logging.info(("写入的字节数：", self.bytes_number))
                    logging.info(sendstr)
                    logging.info(("输入缓冲区：",self.ser.in_waiting))
                    self.count += 1
                elif self.count==3:
                    logging.info("测试全部ascii码")
                    sendstr = self.ascii
                    logging.info(("总的字节数",len(sendstr.encode("utf-8"))))
                    start = time.time()
                    self.bytes_number = self.ser.write(sendstr.encode("utf-8"))
                    end = time.time()
                    self.transmit_speed += self.bytes_number / (end - start) / 1024
                    logging.info(("写入的字节数：", self.bytes_number))
                    logging.info(sendstr)
                    logging.info(("输入缓冲区：",self.ser.in_waiting))
                    self.count = 1

                    self.startcontent = sendstr
                    self.status = "read"
                    self.lock.release()
                    break
                self.startcontent = sendstr
                self.status = "read"
                self.lock.release()


    def readFiles(self):
        while True:
            if self.status == "read":
                self.lock.acquire()
                if self.ser.in_waiting:
                    if self.fileenable:
                        recstr = self.ser.read(self.ser.in_waiting)  # self.bytes_number
                        self.dstfile.write(recstr)
                        self.status = "write"
                    else:
                        self.dstfile.close()
                        # 验证md5
                        if self.getFileMd5(self.srcpath) == self.getFileMd5(self.dstpath):
                            self.md5_success += 1
                        self.lock.release()
                        break
                self.lock.release()

    def readAscii(self):
        logging.info("read...")
        logging.info(("读取字节数:", self.bytes_number))
        logging.info(self.startcontent)
        try:
            text = self.ser.read(self.bytes_number).decode("utf-8")
            self.endcontent = text
            logging.info(("接收字节数：", self.bytes_number))
            logging.info(text)
            yield self.startcontent == self.endcontent
        except:
            self.endcontent = None

    def getSpeed(self):
        speeds = {"发送速率":"%.2fKB/s" % (self.transmit_speed / self.times),"接收速率":1}
        return speeds

    def write(self):
        # 总方法
        pass

    def read(self):
        # 总方法
        times = 1
        while True:
            if times > self.times:
                break
            if self.args.f:
                self.writeFiles()
            if self.args.a:
                for result in self.writeAscii():
                    yield result

            if self.srcfile.closed and self.dstfile.closed:
                self.fileenable = True
                self.dstfile = open(self.dstpath, "wb")
                self.srcfile = open(r"%s" % self.srcpath, "rb")
            times += 1
        self.getSpeed()
    def getReadSpeed(self):
        return