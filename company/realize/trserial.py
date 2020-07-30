import os
import time
import random
from threading import Thread
import serial
from basic.trbasic import TRBasic,logging


class TRSerial(TRBasic):

    def __init__(self,ser,lock,args):
        super().__init__(ser,lock,args)
        #Ascii码测试下标
        self.count = 1
        #队列传输文件,准备状态
        self.nextfile = True

    def writeFiles(self):
        #发送文件
        logging.info("测试发送文件...")
        logging.info("发送文件大小(字节):%s"%os.path.getsize(self.srcpath))
        self.start_sendfile_time = time.time()
        while True:
            if self.status == "write":
                self.lock.acquire()
                if self.fileenable:
                    data = self.srcfile.read(2048)
                    if data:
                        try:
                            self.bytes_number = self.ser.write(data)
                        except serial.serialutil.SerialTimeoutException as e:
                            self.fileenable = False
                            self.srcfile.close()
                            self.status = "read"
                            logging.info("发生超时错误...")
                            self.lock.release()
                            break
                        else:
                            self.status = "read"
                    else:
                        self.srcfile.close()
                        self.fileenable = False
                        self.status = "read"
                        self.lock.release()
                        logging.info("文件传输完成")
                        break

                self.lock.release()
        logging.info("测试发送文件完成")

    def writeAscii(self):
        #发送Ascii码
        logging.info("测试发送Ascii码...")
        while True:
            if self.status == "write":
                self.lock.acquire()
                if self.count==1:
                    logging.info("测试单个ascii码")
                    sendstr = random.choice(self.ascii)
                    self.bytes_number = self.ser.write(sendstr.encode("utf-8"))
                    self.count += 1
                elif self.count==2:
                    logging.info("测试多个ascii码")
                    sendstr = "".join(random.sample(self.ascii, random.randint(2, 255)))
                    self.bytes_number = self.ser.write(sendstr.encode("utf-8"))
                    self.count += 1
                elif self.count==3:
                    logging.info("测试全部ascii码")
                    sendstr = self.ascii
                    self.bytes_number = self.ser.write(sendstr.encode("utf-8"))
                    self.count = 1

                    self.startcontent = sendstr
                    self.status = "read"
                    self.lock.release()
                    break
                self.startcontent = sendstr
                self.status = "read"
                self.lock.release()
        logging.info("单次Ascii码传输完成")

    def readFiles(self):
        #接收文件
        logging.info("测试接收文件...")
        while True:
            if self.status == "read":
                self.nextfile = False
                self.lock.acquire()
                if self.fileenable:
                    if self.ser.in_waiting:
                        recstr = self.ser.read(self.bytes_number)  # self.bytes_number
                        self.dstfile.write(recstr)
                        self.status = "write"
                    # else:
                    #     logging.info("等待缓冲区出现数据...")
                    #     time.sleep(0.1)
                else:
                    logging.info("接收文件完成")
                    self.dstfile.close()
                    self.end_receive_time = time.time()
                    logging.info("接收文件大小(字节):%s"%os.path.getsize(self.dstpath))
                    # 清理缓冲区内容
                    self.ser.reset_input_buffer()
                    self.status = "write"
                    self.lock.release()
                    break
                self.lock.release()
        logging.info("测试接收文件完成")

    def readAscii(self):
        #接收Ascii码
        logging.info("测试读取Ascii码...")
        while True:
            if self.status == "read":
                self.lock.acquire()
                if self.ser.in_waiting:
                    logging.info("read...")
                    try:
                        text = self.ser.read(self.bytes_number).decode("utf-8")
                        self.endcontent = text
                    except:
                        self.endcontent = None
                    yield self.startcontent == self.endcontent
                    if len(self.startcontent) == 256:
                        self.lock.release()
                        #清理缓冲区内容
                        self.ser.reset_input_buffer()
                        self.status = "write"
                        break
                    self.status = "write"
                self.lock.release()
        logging.info("单次Ascii码测试完成")

    def getWriteSpeed(self):
        #测试发送速率
        times = 10
        logging.info("测试"+str(self.times)+"次发送速率...")
        while times:
            if self.status == "write":
                self.lock.acquire()
                sendstr = self.ascii.encode("utf-8")
                start = time.time()
                self.bytes_number = self.ser.write(sendstr)
                end = time.time()
                self.transmit_speeds+= self.bytes_number/(end-start)/1024
                self.status = "read"
                times -= 1
                self.lock.release()
        logging.info("测试发送速率完成")

    def getReadSpeed(self):
        #测试接收速率
        times = 10
        logging.info("测试" + str(self.times) + "次接收速率...")
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
                    self.status = "write"
                    times -= 1
                    self.lock.release()
        # 清理缓冲区内容
        self.ser.reset_input_buffer()
        logging.info("测试接收速率完成")

    def write(self):
        # 发送数据
        times = 1
        logging.info("start test send ...")
        while True:
            if times > self.times:
                break
            logging.info("write测试第"+str(times)+"次")
            if self.args.f or self.args.A:
                logging.info("write测试文件md5...")
                for url in self.urls:
                    while True:
                        #判断文件是否接收完成
                        if self.nextfile == True:
                            self.getInitUrl(url)
                            break
                    self.writeFiles()
                logging.info("write测试文件md5完成")
            if self.args.a or self.args.A:
                logging.info("write测试Ascii码...")
                self.writeAscii()
                logging.info("write测试Ascii码完成")
            logging.info("write测试第"+str(times)+"次完成")
            times += 1

        #测试发送速率
        if self.args.s or self.args.A:
            logging.info("write测试发送速率...")
            self.getWriteSpeed()
            logging.info("write测试发送速率完成")
        logging.info("send over")

    def read(self):
        # 接收数据
        times = 1
        logging.info("start test receive ...")
        while True:
            if times > self.times:
                break
            logging.info("read测试第"+str(times)+"次")
            if self.args.f or self.args.A:
                logging.info("read测试文件md5...")
                for url in self.urls:
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

                    self.fileenable = True
                    # 执行初始化下次测试
                    self.nextfile = True

                logging.info("read测试文件md5完成")
            if self.args.a or self.args.A:
                logging.info("read测试Ascii码...")
                for result in self.readAscii():
                    yield result
                logging.info("read测试Ascii码完成")
            logging.info("read测试第"+str(times)+"次完成")
            times += 1
        #测试接收速率
        if self.args.s or self.args.A:
            logging.info("read测试接收速率...")
            self.getReadSpeed()
            logging.info("read测试接收速率完成")
        logging.info("receive over")

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
        print("生成测试报告...")
        self.report()

if __name__ == '__main__':
    pass

