#_*_ coding:utf-8 _*_
import time
import sys
import os
import hashlib
import csv
import random
import logging.config
from functools import reduce
import threading
import requests

logging.config.fileConfig("../log/trlog.conf")
logging = logging.getLogger()

class TRSerial():
    def __init__(self,ser,lock,args,status="write"):
        os.system("sudo bash ../__init__.sh &> /dev/null")
        self.status = status
        self.ser = ser
        self.args = args
        self.lock = lock
        self.startcontent = ""
        self.endcontent = ""
        #文件md5验证
        self.md5_success = 0
        #单个ascii字符
        self.sc_fail = 0
        self.sc_success = 0
        #多个ascii字符
        self.mc_fail = 0
        self.mc_success = 0
        #全部ascii字符
        self.ac_fail = 0
        self.ac_success = 0
        #发送数据速率
        self.transmit_speed = 0
        #测试次数
        self.times = args.times
        #文件对象
        self.srcfile = None
        self.dstfile = None
        #是否测试文件
        self.fileenable = True
        #文件前缀prefix
        self.fileprefix = "".join(self.ser.name.split("/"))
        #ascii码
        self.ascii = reduce(lambda x,y:x+y,map(lambda x:chr(x),range(256)))
        #下载jpg的url路径
        self.url = args.p.strip()
        self.dstpath = "../resources/"+self.fileprefix + "dst." + self.url.split(".")[-1][0:3]
        if self.url.startswith("http"):
            try:
                self.srcpath = "../resources/"+self.fileprefix + "src." + self.url.split(".")[-1][0:3]
                self.getFile()
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
            self.srcpath = self.url.strip()
            if os.path.exists(self.srcpath):
                self.srcfile = open(r"%s"%self.srcpath, "rb")
                self.dstfile = open(self.dstpath, "wb")
            else:
                logging.info("文件不存在...")
                raise FileNotFoundError

        logging.info("main...")
    def read(self):
        times = 1
        while True:
            if times>3*self.times:
                break
            if self.status == "read":
                self.lock.acquire()
                if self.ser.in_waiting:
                        if self.fileenable:
                            logging.info("开始接收data...")
                            recstr = self.ser.read(self.ser.in_waiting) #self.bytes_number
                            self.dstfile.write(recstr)
                            self.status = "write"
                        else:
                            logging.info("read...")
                            logging.info(("读取字节数:",self.bytes_number))
                            logging.info(self.startcontent)
                            try:

                                text = self.ser.read(self.bytes_number).decode("utf-8")
                                self.endcontent = text
                                logging.info(("接收字节数：",self.bytes_number))
                                logging.info(text)
                            except:
                                self.endcontent = None

                            yield self.endcontent == self.startcontent
                            if not self.srcfile.closed and times<3*self.times:
                                self.fileenable = True
                                self.dstfile = open(self.dstpath, "wb")
                            else:
                                self.srcfile.close()
                            self.status = "write"
                            times += 1
                self.lock.release()

    def write(self):
        times = 1
        count = 1
        while True:
            if times > self.times:
                break
            if self.status == "write":
                logging.info("第" + str(times) + "次测试")
                self.lock.acquire()
                if self.fileenable:
                    logging.info("测试文件...")
                    data = self.srcfile.read(2048)
                    if data:
                        self.bytes_number = self.ser.write(data)
                        logging.info("发送data成功...")
                        self.status = "read"
                    else:
                        if not self.ser.in_waiting:
                            self.fileenable = False
                            self.srcfile.close()
                            self.status = "write"
                        else:
                            self.status = "read"
                    logging.info(("输入缓冲区:",self.ser.in_waiting))

                else:
                    self.dstfile.close()
                    logging.info("write...")
                    if count==1:
                        logging.info("测试单个ascii码")
                        sendstr = random.choice(self.ascii)
                        logging.info(("总的字节数", len(sendstr.encode("utf-8"))))
                        self.bytes_number = self.ser.write(sendstr.encode("utf-8"))
                        logging.info(("写入的字节数：",self.bytes_number))
                        logging.info(sendstr)
                        self.ser.flush()
                        logging.info(("输入缓冲区：", self.ser.in_waiting))
                        times -= 1
                        count += 1
                    elif count==2:
                        logging.info("测试多个ascii码")
                        sendstr = "".join(random.sample(self.ascii, random.randint(2, 255)))
                        logging.info(("总的字节数", len(sendstr.encode("utf-8"))))
                        self.bytes_number = self.ser.write(sendstr.encode("utf-8"))
                        logging.info(("写入的字节数：", self.bytes_number))
                        logging.info(sendstr)
                        self.ser.flush()
                        logging.info(("输入缓冲区：",self.ser.in_waiting))
                        times -= 1
                        count += 1
                    elif count==3:
                        logging.info("测试全部ascii码")
                        sendstr = self.ascii
                        logging.info(("总的字节数",len(sendstr.encode("utf-8"))))
                        start = time.time()
                        self.bytes_number = self.ser.write(sendstr.encode("utf-8"))
                        end = time.time()
                        print("传输速率",self.bytes_number/(end-start)/1024)
                        self.transmit_speed += self.bytes_number / (end - start) / 1024
                        logging.info(("写入的字节数：", self.bytes_number))
                        logging.info(sendstr)
                        self.ser.flush()
                        logging.info(("输入缓冲区：",self.ser.in_waiting))
                        count = 1
                        #验证md5
                        if self.getFileMd5(self.srcpath) == self.getFileMd5(self.dstpath):
                            self.md5_success += 1
                        self.srcfile = open(r"%s"%self.srcpath, "rb")
                    self.startcontent = sendstr
                    self.status = "read"
                    times += 1
                self.lock.release()

    def getFile(self):
        res = requests.get(self.url).content
        with open(self.srcpath,"wb") as f:
            f.write(res)
        logging.info("下载成功...")

    def getFileMd5(self,filename):
        if not os.path.isfile(filename):
            logging.info("file not found")
            return
        myHash = hashlib.md5()
        f = open(r"%s"%filename, 'rb')
        while True:
            b = f.read(8096)
            if not b:
                break
            myHash.update(b)
        f.close()
        return myHash.hexdigest()

    def run(self):
        t1 = threading.Thread(target=self.read)
        t2 = threading.Thread(target=self.write)
        t1.start()
        t2.start()
        results = self.read()
        for result in results:
            if result == False:

                if(len(self.startcontent))==1:
                    self.sc_fail += 1
                elif 1<len(self.startcontent)<256:
                    self.mc_fail += 1
                elif len(self.startcontent)==256:
                    self.ac_fail += 1
                logging.info("测试失败!")
            elif result == True:
                if (len(self.startcontent)) == 1:
                    self.sc_success += 1
                elif 1 < len(self.startcontent) < 256:
                    self.mc_success+= 1
                elif len(self.startcontent) == 256:
                    self.ac_success += 1
                logging.info("测试通过!")
        self.writecsv()

    def writecsv(self):
        device_baudrate = ["设备名",self.ser.name,"波特率",self.ser.baudrate,"传输速率","%.2fKB/s"%(self.transmit_speed/self.times)]

        headers = ["测试项","次数","成功","失败","成功率"]
        sc_percent = self.sc_success/self.times*100
        mc_percent = self.mc_success/self.times*100
        ac_percent = self.ac_success/self.times*100
        md5_percent = self.md5_success/self.times* 100
        sum_percent = (self.sc_success + self.mc_success + self.ac_success)/(3*self.times)*100
        rows = [
            {"测试项":"单个ascii码", "次数":self.times, "成功":self.sc_success,"失败":self.sc_fail,"成功率":"%.2f%%"%(sc_percent)},
            {"测试项":"多个ascii码", "次数":self.times, "成功":self.mc_success,"失败":self.mc_fail,"成功率":"%.2f%%"%(mc_percent)},
            {"测试项":"全部ascii码", "次数":self.times, "成功":self.ac_success,"失败":self.ac_fail,"成功率":"%.2f%%"%(ac_percent)},
            {"测试项":"总计", "次数":3*self.times, "成功":self.ac_success+self.mc_success+self.sc_success,"失败":self.ac_fail+self.mc_fail+self.sc_fail,"成功率":"%.2f%%"%(sum_percent)},
            {"测试项": "文件md5", "次数": self.times, "成功": self.md5_success, "失败": self.times-self.md5_success,"成功率": "%.2f%%" % md5_percent},
        ]
        with open("../report/"+"".join(self.ser.name.split("/"))+'tr.csv', 'w', newline='',encoding="utf-8")as f:
            l_csv = csv.writer(f)
            l_csv.writerow(device_baudrate)

            f_csv = csv.DictWriter(f, headers)
            f_csv.writeheader()
            f_csv.writerows(rows)
            l_csv.writerow([])


