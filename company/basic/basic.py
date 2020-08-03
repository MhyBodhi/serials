import os
import hashlib
import csv
from functools import reduce
import redis
import requests


class Basic():
    def __init__(self,ser,args):
        self.ser = ser
        self.fileprefix = "".join(self.ser.name.split("/"))
        self.url = args.p.strip()

        self.args = args
        # redis实例
        pool = redis.ConnectionPool(host=args.redis.strip(), port=6379, decode_responses=True)
        self.redis = redis.Redis(connection_pool=pool,db=0)
        # Rserver status
        self.rserverstatus = False
        # Tserver status
        self.tserverstatus = False
        # 测试次数
        self.times = args.times
        if self.times == 0:
            raise ValueError("times不能为0")
        #hkey
        self.tname = self.ser.name + "status"
        #成功与失败次数统计
        self.success = 0
        self.fail = 0
        #发送方设备名
        self.device_name = None
        #二次建立确认tstatus
        self.tstatus = None
        #写入的bytes_number
        self.bytes_number = None
        #改变写或读状态
        self.trstatus = None
        #ascii码
        self.ascii = reduce(lambda x,y:x+y,map(lambda x:chr(x),range(256)))
        #文件读取是否启动
        self.fileenable = None
        #md5验证
        self.md5_success = 0
        #传入的起始字符
        self.startcontent = None
        # 单个ascii字符
        self.sc_fail = 0
        self.sc_success = 0
        # 多个ascii字符
        self.mc_fail = 0
        self.mc_success = 0
        # 全部ascii字符
        self.ac_fail = 0
        self.ac_success = 0
        # 发送数据速率
        self.transmit_speeds = 0
        # 接受数据速率
        self.receive_speeds = 0
        # 接受数据起始、结束时间
        self.receive_start = 0
        self.receive_end = 0
        # 接收不耗时
        self.receive_speed_zero = False
        # 传入url路径集合
        self.urls = args.p.split(',')
        # Ascii码测试下标
        self.count = 1
        # 队列传输文件,准备状态
        self.nextfile = 1
        #传输文件
        self.files = None
        #接收时间
        self.receive_time = 0
        #文件测试记录
        self.files_nature = {}

    def getFile(self,url):
        res = requests.get(url).content
        with open("../resources/"+self.fileprefix+"src."+self.url.split(".")[-1][0:3],"wb") as f:
            f.write(res)

    @staticmethod
    def getFileMd5(filename):
        if not os.path.isfile(filename):
            print("文件不存在...")
            return
        myHash = hashlib.md5()
        f = open(filename, 'rb')
        while True:
            b = f.read(8096)
            if not b:
                break
            myHash.update(b)
        f.close()
        return myHash.hexdigest()

    def report(self):

        device_baudrate = ["设备名", self.ser.name, "波特率", self.ser.baudrate]

        headers = ["测试项", "次数", "传输文件名", "大小(单位:字节B)", "成功次数", "失败次数", "成功率", "速率（KB/s）", "单次平均传输所花时间（单位:秒s）"]
        report_dicts = []
        # 统计Ascii码
        if self.args.a or self.args.A:
            sc_percent = self.sc_success / self.times * 100
            mc_percent = self.mc_success / self.times * 100
            ac_percent = self.ac_success / self.times * 100
            ascii_rows = [
                {"测试项": "单个ascii码", "次数": self.times, "传输文件名": "/",
                 "大小(单位:字节B)": "/", "成功次数": self.sc_success, "失败次数": self.sc_fail,
                 "成功率": "%.2f%%" % (sc_percent), "速率（KB/s）": "/", "单次平均传输所花时间（单位:秒s）": "/",
                 },
                {"测试项": "多个ascii码", "次数": self.times, "传输文件名": "/",
                 "大小(单位:字节B)": "/", "成功次数": self.mc_success, "失败次数": self.mc_fail,
                 "成功率": "%.2f%%" % (mc_percent), "速率（KB/s）": "/", "单次平均传输所花时间（单位:秒s）": "/",
                 },
                {"测试项": "全部ascii码", "次数": self.times, "传输文件名": "/",
                 "大小(单位:字节B)": "/", "成功次数": self.ac_success, "失败次数": self.ac_fail,
                 "成功率": "%.2f%%" % (ac_percent), "速率（KB/s）": "/", "单次平均传输所花时间（单位:秒s）": "/",
                 },
            ]
            report_dicts.extend(ascii_rows)

        # 统计传输文件成功率
        if self.args.f or self.args.A:
            for file in self.files_nature:
                success = self.files_nature[file]["success"]
                files_rows = [
                    {"测试项": "md5", "次数": self.times, "传输文件名": file,
                     "大小(单位:字节B)": self.files_nature[file]["size"], "成功次数": success, "失败次数": self.times - success,
                     "成功率": "%.2f%%" % (success / self.times * 100), "速率（KB/s）": "%.2f"%(self.files_nature[file]["size"]/self.files_nature[file]["time"]/self.times/1024),
                     "单次平均传输所花时间（单位:秒s）": "%.2f" % (self.files_nature[file]["time"]/self.times),
                     },
                ]
                report_dicts.extend(files_rows)
        # 统计传输速率（发送、接收速率）
        if self.args.s or self.args.A:
            # 发送速率
            send_speed = float(self.redis.hget(self.tstatus, "transmitspeed"))
            # 接收速率(为零表示超出统计范围,有时接收速率太快让统计时间为零，致使无法统计)
            if self.receive_speed_zero:
                receive_speed = "0(速率太快，无法统计)"
            else:
                receive_speed = "%.2f" % (self.receive_speeds / 10)
            speed_rows = [
                {"测试项": "发送速率", "次数": "/", "传输文件名": "/",
                 "大小(单位:字节B)": "/", "成功次数": "/", "失败次数": "/",
                 "成功率": "/", "速率（KB/s）": "%.2f" % send_speed, "单次平均传输所花时间（单位:秒s）": "/",
                 },
                {"测试项": "接收速率", "次数": "/", "传输文件名": "/",
                 "大小(单位:字节B)": "/", "成功次数": "/", "失败次数": "/",
                 "成功率": "/", "速率（KB/s）": receive_speed, "单次平均传输所花时间（单位:秒s）": "/",
                 },
            ]
            report_dicts.extend(speed_rows)

        with open("../report/" + "".join(self.ser.name.split("/")) + 'tr.csv', 'a', newline='', encoding="utf-8") as f:
            l_csv = csv.writer(f)
            l_csv.writerow(device_baudrate)

            f_csv = csv.DictWriter(f, headers)
            f_csv.writeheader()
            f_csv.writerows(report_dicts)
            l_csv.writerow([])