import os
import sys
import time
import random
import json
import logging.config
import logging
import requests
import serial
from basic.basic import Basic

logging.config.fileConfig("../log/tlog.conf")
logging = logging.getLogger()


class TSerial(Basic):

    def __init__(self,ser,args):
        super().__init__(ser,args)

        self.redis.hmset(self.tname,{"write": 0, "end": 1, "read": 0,
                 "times": self.times,
                 "reporttimes": self.times, "ok": 0,"transmit": 0, "srcmd5": 0,
                 "trstatus": "write", "fileenable": 1,"nextfile":1,
                 "files":json.dumps(self.urls),"f":0,"a":0,"s":0,"A":0})
        #储存测试项
        if self.args.A:self.redis.hmset(self.tname, {"f":1,"a":1,"s":1,"A":1})
        if self.args.f:self.redis.hset(self.tname,"f",1)
        if self.args.a:self.redis.hset(self.tname,"a",1)
        if self.args.s:self.redis.hset(self.tname,"s",1)

        if self.ser.name.endswith("0"):
            self.redis.hset("devices", "device0", self.ser.name)
        elif self.ser.name.endswith("1"):
            self.redis.hset("devices", "device1", self.ser.name)
        elif self.ser.name.endswith("2"):
            self.redis.hset("devices", "device2", self.ser.name)
        elif self.ser.name.endswith("3"):
            self.redis.hset("devices", "device3", self.ser.name)
        elif self.ser.name.endswith("4"):
            self.redis.hset("devices", "device4", self.ser.name)
        elif self.ser.name.endswith("5"):
            self.redis.hset("devices", "device5", self.ser.name)
        elif self.ser.name.endswith("6"):
            self.redis.hset("devices", "device6", self.ser.name)
        elif self.ser.name.endswith("7"):
            self.redis.hset("devices", "device7", self.ser.name)
        elif self.ser.name.endswith("8"):
            self.redis.hset("devices", "device8", self.ser.name)

    def getInitUrl(self, url):
        self.fileenable = True
        self.dstpath = "../resources/" + self.fileprefix + "dst." + url.split(".")[-1][0:3]
        self.redis.hset(self.tname,"filetype",url.split(".")[-1][0:3])
        if url.startswith("http"):
            try:
                self.srcpath = "../resources/" + self.fileprefix + "src." + url.split(".")[-1][0:3]
                self.getFile(url)
            except requests.exceptions.ConnectionError:
                if os.path.exists(self.srcpath):
                    logging.info("使用现有文件验证...")
                    self.srcfile = open(self.srcpath, "rb")
                    self.dstfile = open(self.dstpath, "wb")
                    time.sleep(3)
                else:
                    logging.info("请检查网络连接是否正常...")
                    sys.exit()
            else:
                self.srcfile = open(self.srcpath, "rb")
                self.dstfile = open(self.dstpath, "wb")
        else:
            self.srcpath = url.strip()
            print("文件名",self.srcpath)

            if os.path.exists(self.srcpath):
                self.srcfile = open(r"%s" % self.srcpath, "rb")
                self.dstfile = open(self.dstpath, "wb")
            else:
                logging.info("文件不存在...")
                raise FileNotFoundError

    def initConnect(self):
        # 与rserver建立连接初始化...
        while True:
            logging.info("连接rserver...")
            if self.redis.hget(self.tname, "read") == "0" and self.redis.hget(self.tname, "end") == "1":
                self.redis.hset(self.tname, "write", 1)
                logging.info("与rserver没有建立连接...")
                while True:
                    logging.info(("发送本机设备名称...", self.ser.name))
                    self.ser.write(self.ser.name.encode("utf-8"))
                    if self.redis.hget(self.tname, "read") == "1" and self.redis.hget(self.tname, "end") == "0":
                        self.redis.hset(self.tname, "ok", 1)
                        logging.info("rserver准备就绪...")
                        break
                    time.sleep(1)
                break
            time.sleep(3)

    #传输文件...
    def writeFiles(self):
        #发送文件
        logging.info("测试发送文件...")
        logging.info("发送文件大小(字节):%s"%os.path.getsize(self.srcpath))
        self.redis.hset(self.tname,"srcfilesize",os.path.getsize(self.srcpath))
        self.redis.hset(self.tname,"send_time",0)
        while True:
            self.trstatus = self.redis.hget(self.tname, "trstatus")
            if self.trstatus == "write":
                self.fileenable = int(self.redis.hget(self.tname, "fileenable"))
                if self.fileenable:
                    data = self.srcfile.read(2048)
                    if data:
                        try:
                            start_time = time.time()
                            self.bytes_number = self.ser.write(data)
                            end_time = time.time()
                            self.redis.hset(self.tname,"send_time",int(self.redis.hget(self.tname,"send_time"))+end_time-start_time)
                            self.redis.hset(self.tname, {"bytes_number":self.bytes_number,"trstatus": "read"})
                        except serial.serialutil.SerialTimeoutException as e:
                            self.srcfile.close()
                            self.redis.hmset(self.tname, {"srcmd5": self.getFileMd5(self.srcpath),"trstatus":"read","fileenable": 0})
                            break
                    else:
                        self.srcfile.close()
                        self.redis.hmset(self.tname, {"srcmd5": self.getFileMd5(self.srcpath),"trstatus": "read","fileenable": 0})
                        break
        logging.info("测试发送文件完成")

    def writeAscii(self):
        #发送Ascii码
        logging.info("测试发送Ascii码...")
        while True:
            self.trstatus = self.redis.hget(self.tname, "trstatus")
            if self.trstatus == "write":
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

                    logging.info(("写入的字节数大小:", self.bytes_number))
                    self.redis.hset(self.tname, "bytes_number", self.bytes_number)
                    self.redis.hset(self.tname, "ascii", sendstr)
                    self.redis.hset(self.tname, "trstatus", "read")
                    break

                logging.info(("写入的字节数大小:", self.bytes_number))
                self.redis.hset(self.tname, "bytes_number", self.bytes_number)
                self.redis.hset(self.tname, "ascii", sendstr)
                self.redis.hset(self.tname, "trstatus", "read")
        logging.info("测试发送Ascii码完成")

    def getWriteSpeed(self):
        # 测试发送速率
        times = 10
        logging.info("测试" + str(self.times) + "次发送速率...")
        while times:
            self.trstatus = self.redis.hget(self.tname, "trstatus")
            if self.trstatus == "write":
                sendstr = self.ascii.encode("utf-8")
                start = time.time()
                self.bytes_number = self.ser.write(sendstr)
                end = time.time()
                self.transmit_speeds += self.bytes_number / (end - start) / 1024
                self.redis.hset(self.tname,"bytes_number",self.bytes_number)
                self.redis.hset(self.tname,"trstatus","read")
                times -= 1
        logging.info("测试发送速率完成")

    def write(self):
        times = 1
        #连接rserver
        self.initConnect()
        #传输内容
        logging.info("start test send ...")
        while True:
            logging.info("判断transmit是否准备...")
            if self.redis.hget(self.tname,"transmit")=="1":
                while True:
                    if times > self.times:
                        break
                    if self.args.f or self.args.A:
                        for url in self.urls:
                            while True:
                                # 判断文件是否接收完成
                                self.nextfile = int(self.redis.hget(self.tname,"nextfile"))
                                if self.nextfile == 1:
                                    self.getInitUrl(url)
                                    break
                            self.redis.hset(self.tname,"currentfile",url)
                            self.writeFiles()
                    if self.args.a or self.args.A:
                        self.writeAscii()
                    times += 1
                break
        if self.args.s or self.args.A:
            self.getWriteSpeed()
            self.redis.hset(self.tname,"transmitspeed",self.transmit_speeds/10)
        self.redis.hmset(self.tname,{"ok":0,"transmit":0,"write":0})
        time.sleep(0.5)
        logging.info("send over")

    def run(self):
        self.write()
        if self.args.f:
            self.srcfile.close()
        self.redis.close()


