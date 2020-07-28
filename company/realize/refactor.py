import time
import random
from threading import Thread
from realize.basic import TRSerial,logging


class Refactor(TRSerial):

    def __init__(self,ser,lock,args):
        super().__init__(ser,lock,args)
        #Ascii码测试下标
        self.count = 1

    def writeFiles(self):

        while True:
            if self.status == "write":
                self.lock.acquire()
                if self.fileenable:
                    print("开始写入...")
                    data = self.srcfile.read(2048)
                    if data:
                        self.bytes_number = self.ser.write(data)
                        print("写入字节数",self.bytes_number)
                        self.status = "read"
                        print("切换read成功...")
                    else:
                        if not self.ser.in_waiting:
                            self.fileenable = False
                            self.srcfile.close()
                            self.lock.release()
                            self.status = "read"
                            print("文件传输完成...")
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
                    print("缓冲区有数据...")
                    if self.fileenable:
                        print("这里...")
                        recstr = self.ser.read(self.ser.in_waiting)  # self.bytes_number
                        print("读取内容为",recstr)
                        self.dstfile.write(recstr)
                        self.status = "write"
                else:
                    self.dstfile.close()
                    # 验证md5
                    if self.getFileMd5(self.srcpath) == self.getFileMd5(self.dstpath):
                        self.md5_success += 1
                        print("success...")
                    self.status = "write"
                    self.lock.release()
                    break
                self.lock.release()

    def readAscii(self):
        while True:
            if self.status == "read":
                self.lock.acquire()
                if self.ser.in_waiting:
                    logging.info("read...")
                    logging.info(("读取字节数:", self.bytes_number))
                    try:
                        text = self.ser.read(self.bytes_number).decode("utf-8")
                        self.endcontent = text
                        logging.info(text)
                    except:
                        self.endcontent = None
                    yield self.startcontent == self.endcontent
                    if len(self.startcontent) == 256:
                        print("ok...")
                        self.status = "write"
                        break
                    self.status = "write"
                self.lock.release()

    def getSpeed(self):
        start = time.time()
        self.bytes_number = self.ser.write(self.ascii.encode("utf-8"))
        end = time.time()
        self.transmit_speed = self.bytes_number / (end - start) / 1024
        self.ser.reset_input_buffer()
        speeds = {"发送速率":"%.2fKB/s" % self.transmit_speed,"接收速率":1}
        return speeds

    def write(self):
        # 总方法
        times = 1
        while True:
            if times > self.times:
                break
            print("write执行第"+str(times)+"次测试")
            if self.args.f:
                self.writeFiles()
            if self.args.a:
                print("测试Ascii码...")
                self.writeAscii()
            print("write执行第"+str(times)+"次完成...")
            print(self.status)
            times += 1

    def read(self):
        # 总方法
        times = 1
        while True:
            if times > self.times:
                break
            print("read执行第"+str(times)+"次测试")
            if self.srcfile.closed and self.dstfile.closed:
                print("再次传输文件...")
                self.dstfile = open(self.dstpath, "wb")
                self.srcfile = open(r"%s" % self.srcpath, "rb")
                print("打开文件成功..")
                self.fileenable = True
            if self.args.f:
                self.readFiles()
            if self.args.a:
                for result in self.readAscii():
                    yield result
            print("read执行第"+str(times)+"次完成...")

            times += 1
        # print(self.getSpeed())

    def run(self):
        # #传输文件测试
        # t1 = Thread(target=self.writeFiles)
        # t2 = Thread(target=self.readFiles)
        # t1.start()
        # t2.start()
        #传输Ascii码测试
        # t1 = Thread(target=self.writeAscii)
        # t2 = Thread(target=self.readAscii)
        # t1.start()
        # t2.start()
        # for result in self.readAscii():
        #     print(result)
        t1 = Thread(target=self.write)
        t2 = Thread(target=self.read)
        t1.start()
        t2.start()
        for result in self.read():
            print("start...")
            print(result)

    def getReadSpeed(self):
        return

if __name__ == '__main__':
    pass

