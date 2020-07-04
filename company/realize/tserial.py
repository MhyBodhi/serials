import os
import sys
import time
import random
import logging.config
import requests
from basic.basic import Basic

logging.config.fileConfig("../log/tlog.conf")
logging = logging.getLogger()


class TSerial(Basic):

    def __init__(self,ser,args):
        super().__init__(ser,args)
        if self.url.startswith("http"):
            try:
                self.srcpath = "../report/"+self.fileprefix + "src." + self.url.split(".")[-1][0:3]
                self.getFile()
            except requests.exceptions.ConnectionError:
                if os.path.exists(self.srcpath):
                    logging.info("使用现有文件验证...")
                    self.srcfile = open(self.srcpath, "rb")
                    time.sleep(3)
                else:
                    logging.info("请检查网络连接是否正常...")
                    sys.exit()
            else:
                self.srcfile = open(self.srcpath, "rb")
        else:
            self.srcpath = self.url.strip()
            if os.path.exists(r"%s"%self.srcpath):
                self.srcfile = open(r"%s"%self.srcpath, "rb")
            else:
                logging.info("文件不存在...")
                raise FileNotFoundError
        self.redis.hmset(self.tname, {"write": 0, "end":1,"read":0, "times": self.times,"reporttimes":self.times,"ok": 0, "transmit": 0, "srcmd5": 0,"trstatus":"write","fileenable":1})
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

    def write(self):
        times = 1
        count = 1
        while True:
            logging.info("连接rserver...")
            if self.redis.hget(self.tname,"read") == "0" and self.redis.hget(self.tname,"end") == "1":
                self.redis.hset(self.tname, "write", 1)
                logging.info("与rserver没有建立连接...")
                logging.info(("self.tname",self.tname))
                while True:
                    self.ser.write(self.ser.name.encode("utf-8"))
                    logging.info(("设备名称",self.ser.name))
                    if self.redis.hget(self.tname,"read") == "1" and self.redis.hget(self.tname,"end") == "0":
                        self.redis.hset(self.tname,"ok",1)
                        logging.info("rserver准备就绪...")
                        break
                    logging.info("发送本机设备名称...")
                    time.sleep(1)
                break
            time.sleep(3)

        while True:
            logging.info("判断transmit是否准备...")
            if self.redis.hget(self.tname,"transmit")=="1":
                logging.info(("传输源文件srcfile大小", os.path.getsize(self.srcpath)))
                while True:
                    if times > self.times:
                        break
                    self.trstatus = self.redis.hget(self.tname,"trstatus")
                    if self.trstatus=="write":
                        self.fileenable = int(self.redis.hget(self.tname,"fileenable"))
                        if self.fileenable:
                            data = self.srcfile.read(1024)
                            if data:
                                self.bytes_number = self.ser.write(data)
                                self.redis.hset(self.tname,"bytes_number",self.bytes_number)
                                self.redis.hset(self.tname, "trstatus", "read")
                            else:
                                self.bytes_number = 0
                                self.redis.hset(self.tname, "bytes_number", self.bytes_number)
                                self.redis.hset(self.tname, "fileenable", 0)
                                self.redis.hset(self.tname, "trstatus", "write")
                                self.srcfile.close()
                                self.redis.hmset(self.tname,{"srcmd5":self.getFileMd5(self.srcpath),"srcfile":0})
                        else:
                            logging.info("验证ascii码")
                            if count == 1:
                                logging.info("测试单个ascii码")
                                sendstr = random.choice(self.ascii)
                                self.bytes_number = self.ser.write(sendstr.encode("utf-8"))
                                self.ser.flush()
                                times -= 1
                                count += 1
                            elif count == 2:
                                logging.info("测试多个ascii码")
                                sendstr = "".join(random.sample(self.ascii, random.randint(2, 255)))
                                self.bytes_number = self.ser.write(sendstr.encode("utf-8"))
                                self.ser.flush()
                                times -= 1
                                count += 1
                            elif count == 3:
                                logging.info("测试全部ascii码")
                                sendstr = self.ascii
                                self.bytes_number = self.ser.write(sendstr.encode("utf-8"))
                                self.ser.flush()
                                count = 1
                                logging.info(("传输源文件srcfile大小", os.path.getsize(self.srcpath)))
                                self.srcfile = open(r"%s"%self.srcpath, "rb")
                                self.redis.hset(self.tname, "srcfile", 1)
                            logging.info(("写入的字节数大小:",self.bytes_number))
                            self.redis.hset(self.tname, "bytes_number", self.bytes_number)
                            self.redis.hset(self.tname, "ascii", sendstr)
                            self.redis.hset(self.tname, "trstatus", "read")
                            times += 1
                break
            time.sleep(3)
        self.redis.hmset(self.tname,{"ok":0,"transmit":0,"write":0,"times":int(self.redis.hget(self.tname,"times"))-1,"trstatus":"read"})
        time.sleep(0.5)


    def run(self):
        self.write()
        self.srcfile.close()
        self.redis.close()


