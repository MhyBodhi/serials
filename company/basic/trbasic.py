#_*_ coding:utf-8 _*_
import time
import sys
import os
import hashlib
import csv
import logging.config
from functools import reduce
import requests

logging.config.fileConfig("../log/trlog.conf")
logging = logging.getLogger()

class TRBasic():
    def __init__(self,ser,lock,args,status="write"):
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
        #接受数据速率
        self.receive_speed = 0
        #接受数据起始、结束时间
        self.receive_start = 0
        self.receive_end = 0
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
        self.urls = args.p.split(',')
        # 接受速率是否可控
        self.receive_speed_zero = False
        # 保存对应文件传输时间
        self.files_nature = {}

    def getInitUrl(self,url):
        self.fileenable = True
        self.dstpath = "../resources/" + self.fileprefix + "dst." + url.split(".")[-1][0:3]
        if url.startswith("http"):
            try:
                self.srcpath = "../resources/"+self.fileprefix + "src." + url.split(".")[-1][0:3]
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
            self.srcpath = url
            if os.path.exists(self.srcpath):
                self.srcfile = open(r"%s"%self.srcpath, "rb")
                self.dstfile = open(self.dstpath, "wb")
            else:
                logging.info("文件不存在...")
                raise FileNotFoundError

    def getFile(self,url):
        res = requests.get(url).content
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

    def report(self):

        device_baudrate = ["设备名", self.ser.name, "波特率", self.ser.baudrate]

        headers = ["测试项", "次数", "传输文件名","大小(单位:字节B)","成功次数", "失败次数", "成功率","速率（KB/s）","单次传输所花时间（单位:秒s）"]
        report_dicts = []
        #统计Ascii码
        if self.args.a or self.args.A:
            sc_percent = self.sc_success / self.times * 100
            mc_percent = self.mc_success / self.times * 100
            ac_percent = self.ac_success / self.times * 100
            ascii_rows = [
                {"测试项": "单个ascii码", "次数": self.times, "传输文件名":"/",
                 "大小(单位:字节B)":"/","成功次数": self.sc_success,"失败次数": self.sc_fail,
                 "成功率": "%.2f%%" % (sc_percent),"速率（KB/s）":"/","单次传输所花时间（单位:秒s）":"/",
                 },
                {"测试项": "多个ascii码", "次数": self.times, "传输文件名": "/",
                 "大小(单位:字节B)": "/", "成功次数": self.mc_success, "失败次数": self.mc_fail,
                 "成功率": "%.2f%%" % (mc_percent), "速率（KB/s）": "/", "单次传输所花时间（单位:秒s）": "/",
                 },
                {"测试项": "全部ascii码", "次数": self.times, "传输文件名": "/",
                 "大小(单位:字节B)": "/", "成功次数": self.ac_success, "失败次数": self.ac_fail,
                 "成功率": "%.2f%%" % (ac_percent), "速率（KB/s）": "/", "单次传输所花时间（单位:秒s）": "/",
                 },
            ]
            report_dicts.extend(ascii_rows)

        #统计传输文件成功率
        if self.args.f or self.args.A:
            for file in self.files_nature:
                success = self.files_nature[file]["success"]
                files_rows = [
                {"测试项": "md5", "次数": self.times, "传输文件名": file,
                 "大小(单位:字节B)": self.files_nature[file]["size"], "成功次数": success, "失败次数": self.times-success,
                 "成功率": "%.2f%%" % (success/self.times*100), "速率（KB/s）": "/", "单次传输所花时间（单位:秒s）": "%.2f"%(self.files_nature[file]["time"]),
                 },
                ]
                report_dicts.extend(files_rows)
        #统计传输速率（发送、接收速率）
        if self.args.s or self.args.A:
            #发送速率
            send_speed = self.transmit_speed / self.times
            #接收速率(为零表示超出统计范围,有时接收速率太快让统计时间为零，致使无法统计)
            if self.receive_speed_zero:
                receive_speed = "0(速率太快，无法统计)"
            else:
                receive_speed = "%.2f"%(self.receive_speed / self.times)
            speed_rows = [
                {"测试项": "发送速率", "次数": self.times, "传输文件名": "/",
                 "大小(单位:字节B)":"/", "成功次数":"/", "失败次数": "/",
                 "成功率": "/", "速率（KB/s）": "%.2f"%send_speed, "单次传输所花时间（单位:秒s）":"/",
                 },
                {"测试项": "接收速率", "次数": self.times, "传输文件名": "/",
                 "大小(单位:字节B)": "/", "成功次数": "/", "失败次数": "/",
                 "成功率": "/", "速率（KB/s）": receive_speed, "单次传输所花时间（单位:秒s）": "/",
                 },
                ]
            report_dicts.extend(speed_rows)

        with open("../report/" + "".join(self.ser.name.split("/")) + 'tr.csv', 'w', newline='', encoding="utf-8") as f:
            l_csv = csv.writer(f)
            l_csv.writerow(device_baudrate)

            f_csv = csv.DictWriter(f, headers)
            f_csv.writeheader()
            f_csv.writerows(report_dicts)
            l_csv.writerow([])


