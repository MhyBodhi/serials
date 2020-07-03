#_*_ coding:utf-8 _*_
import time
import sys
sys.path.append("..")
import os
import hashlib
import csv
import argparse
import random
from functools import reduce
import threading
from threading import Lock
import serial
import requests
from basic.basic import logging

class Serial():
    def __init__(self,ser,lock,status="write"):
        self.status = status
        self.ser = ser
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
        self.url = args.p
        self.dstpath = self.fileprefix + "dst." + self.url.split(".")[-1][0:3]
        if self.url.startswith("http"):
            try:
                self.srcpath = self.fileprefix + "src." + self.url.split(".")[-1][0:3]
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

        logging.info("start...")
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
                        self.bytes_number = self.ser.write(sendstr.encode("utf-8"))

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
        print("args.p",args.p)
        print("url",self.url)
        res = requests.get(self.url).content
        try:
                os.remove(self.fileprefix+"src."+self.url.split(".")[-1][0:3])
        except:
            pass
        try:
            with open(self.fileprefix+"src."+self.url.split(".")[-1][0:3],"wb") as f:
                f.write(res)
            logging.info("下载成功...")
        except:
            os.remove(self.fileprefix + "src." + self.url.split(".")[-1][0:3])

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
        threading.Thread(target=self.read).start()
        threading.Thread(target=self.write).start()
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
        device_baudrate = ["设备名",self.ser.name,"波特率",self.ser.baudrate]

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
        with open("".join(self.ser.name.split("/"))+'report.csv', 'w', newline='',encoding="utf-8")as f:
            l_csv = csv.writer(f)
            l_csv.writerow(device_baudrate)

            f_csv = csv.DictWriter(f, headers)
            f_csv.writeheader()
            f_csv.writerows(rows)
            l_csv.writerow([])


def run(ser):
    lock = Lock()
    r = Serial(ser, lock)
    r.run()

def main(baudrate):
    devices = []
    devices.extend(args.devices.strip().split(","))
    sers = []
    for device in devices:
        try:
            sers.append(serial.Serial(device, baudrate,timeout=None,write_timeout=None))
        except:
            pass

    plist = []
    if not sers:
        logging.info("设备读取失败")
        return
    for ser in sers:
        plist.append(threading.Thread(target=run, args=(ser,)))
    for i in plist:
        i.start()
    for i in plist:
        i.join()
    report()

def report():
    csvfiles = [file for file in os.listdir(".") if file.endswith("csv")]
    try:
        with open("total.csv", "a", newline="", encoding="utf-8") as f:
            fw_csv = csv.writer(f)
            for csvfile in csvfiles:
                with open(csvfile, "r", encoding="utf-8") as fl:
                    fr_csv = csv.reader(fl)
                    for row in fr_csv:
                        fw_csv.writerow(row)
    except Exception as e:
        return
if __name__ == '__main__':
    try:
        os.remove("total.csv")
    except:
        pass
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--times", type=int, default=10, help="test_times:number")
    parser.add_argument("-n", "--devices", default=None, help="devices_name:eg./dev/ttyXRUSB0,/dev/ttyXRUSB1>...")
    parser.add_argument("-b", default="115200", help="baudrates:eg.115200,9600...")
    parser.add_argument("-p",default="https://ss1.bdstatic.com/70cFvXSh_Q1YnxGkpoWK1HF6hhy/it/u=3455238864,153902017&fm=26&gp=0.jpg",help="url:download image eg.https://www.baidu.com/.../xxx.jpg")
    parser.add_argument("-t", action='store_true', default=False, help="txserver:threading transmit data")
    parser.add_argument("-r", action='store_true', default=False, help="rxserver:listening receive data")
    args = parser.parse_args()
    baudrates = []
    baudrates.extend(args.b.strip().split(","))
    if args.devices==None:
        logging.info("请输入设备名称,-n")
        parser.print_help()
    for baudrate in baudrates:
        main(baudrate)
