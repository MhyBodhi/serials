import os
import time
import random
from threading import Thread
import serial
from basic.trbasic import TRBasic,logging


class Refactor(TRBasic):

    def __init__(self,ser,lock,args):
        super().__init__(ser,lock,args)
        #Ascii码测试下标
        self.count = 1
        #队列传输文件,准备状态
        self.nextfile = True

    def writeFiles(self):
        #发送文件
        self.start_sendfile_time = time.time()
        while True:
            if self.status == "write":
                self.lock.acquire()
                if self.fileenable:
                    print("开始写入...")
                    data = self.srcfile.read(2048)
                    if data:
                        try:
                            self.bytes_number = self.ser.write(data)
                        except serial.serialutil.SerialTimeoutException as e:
                            self.fileenable = False
                            self.srcfile.close()
                            self.ser.reset_input_buffer()
                            self.status = "read"
                            logging.info("发生超时错误...")
                            self.lock.release()
                            break
                        print("写入字节数",self.bytes_number)
                        self.status = "read"
                        print("切换read成功...")
                    else:
                        if not self.ser.in_waiting:
                            self.fileenable = False
                            self.srcfile.close()
                            self.lock.release()
                            self.status = "read"
                            logging.info("文件传输完成...")
                            break
                        else:
                            self.status = "read"
                self.lock.release()

    def writeAscii(self):
        #发送Ascii码
        while True:
            if self.status == "write":
                print("进入成功...")
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
        print("结束writeAscii码...")


    def readFiles(self):
        #接收文件
        while True:
            if self.status == "read":
                self.nextfile = False
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
                    print("关闭接收文件...")
                    self.dstfile.close()
                    self.end_receive_time = time.time()
                    self.status = "write"
                    self.nextfile = True
                    self.lock.release()
                    break
                self.lock.release()

    def readAscii(self):
        #接收Ascii码
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
                        self.lock.release()
                        self.status = "write"
                        break
                    self.status = "write"
                self.lock.release()
        print("结束readAscii码...")

    def getWriteSpeed(self):
        #测试发送速率
        times = self.times
        while times:
            if self.status == "write":
                self.lock.acquire()
                sendstr = self.ascii.encode("utf-8")
                start = time.time()
                self.bytes_numbers = self.ser.write(sendstr)
                end = time.time()
                self.transmit_speed += self.bytes_numbers/(end-start)/1024
                self.status = "read"
                times -= 1
                self.lock.release()

    def getReadSpeed(self):
        #吃接收速率
        times = self.times
        while times:
            if self.ser.in_waiting:
                if self.status == "read":
                    self.lock.acquire()
                    self.receive_start = time.time()
                    receivestr = self.ser.read(self.bytes_number).decode("utf-8")
                    self.receive_end = time.time()
                    # 接收数据速率
                    if self.receive_end - self.receive_start:
                        self.receive_speed += self.bytes_number / (self.receive_end - self.receive_start) / 1024
                    else:
                        self.receive_speed_zero = True
                    print("接收到的数据",receivestr)
                    self.status = "write"
                    times -= 1
                    self.lock.release()

    def write(self):
        # 发送数据
        times = 1
        while True:
            if times > self.times:
                break
            print("write执行第"+str(times)+"次测试")
            if self.args.f:
                for url in self.urls:
                    while True:
                        #判断文件是否接收完成
                        if self.nextfile == True:
                            self.getInitUrl(url)
                            break
                    print("发送文件...")
                    self.writeFiles()
            if self.args.a:
                print("测试Ascii码...")
                self.writeAscii()
            print("write执行第"+str(times)+"次完成...")
            print(self.status)
            times += 1
        #测试发送速率
        if self.args.s:
            print(self.getWriteSpeed())
        print("write over...")

    def read(self):
        # 接收数据
        times = 1
        while True:
            if times > self.times:
                break
            print("read执行第"+str(times)+"次测试")
            if self.args.f:
                for url in self.urls:
                    self.getInitUrl(url)
                    print("接收文件...")
                    self.readFiles()
                    if times==1:
                        if url.startswith("http"):
                            self.files_nature[self.srcpath] = {"size":os.path.getsize(self.srcpath),"time":self.end_receive_time - self.start_sendfile_time,"success":0}
                        else:
                            self.files_nature[url] = {"size":os.path.getsize(self.srcpath),"time":self.end_receive_time - self.start_sendfile_time,"success":0}
                    # 验证md5
                    if self.getFileMd5(self.srcpath) == self.getFileMd5(self.dstpath):
                        if url.startswith("http"):
                            self.files_nature[self.srcpath]["success"] += 1
                        else:
                            self.files_nature[url]["success"] += 1

            if self.args.a:
                print("读取asciii码")
                for result in self.readAscii():
                    yield result
            print("read执行第"+str(times)+"次完成...")
            times += 1
        #测试接收速率
        if self.args.s:
            print(self.getReadSpeed())
        print("read over...")

    def run(self):
        t1 = Thread(target=self.write)
        t2 = Thread(target=self.read)
        t1.start()
        t2.start()
        results = self.read()
        for result in results:
            if result == False:
                self.ser.reset_input_buffer()
                if(len(self.startcontent))==1:
                    self.sc_fail += 1
                elif 1<len(self.startcontent)<256:
                    self.mc_fail += 1
                elif len(self.startcontent)==256:
                    self.ac_fail += 1
                logging.info("测试Ascii码失败!")
            elif result == True:
                if (len(self.startcontent)) == 1:
                    self.sc_success += 1
                elif 1 < len(self.startcontent) < 256:
                    self.mc_success+= 1
                elif len(self.startcontent) == 256:
                    self.ac_success += 1
                logging.info("测试Ascii码成功!")
        self.report()

if __name__ == '__main__':
    pass

