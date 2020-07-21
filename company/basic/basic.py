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

        # redis实例
        pool = redis.ConnectionPool(host='192.168.1.113', port=6379, decode_responses=True)
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
        self.transmit_speed = 0
        # 接受数据速率
        self.receive_speed = 0
        # 接受数据起始、结束时间
        self.receive_start = 0
        self.receive_end = 0


    def getFile(self):
        res = requests.get(self.url).content
        print("url",self.url)
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

        device_baudrate = ["设备名", self.ser.name, "波特率", self.ser.baudrate,"发送速率","%.2fKB/s" % (self.transmit_speed / self.times),"接收速率","%.2fKB/s" % (self.receive_speed / self.ac_success)]

        headers = ["测试项", "次数", "成功", "失败", "成功率"]
        sc_percent = self.sc_success / self.times * 100
        mc_percent = self.mc_success / self.times * 100
        ac_percent = self.ac_success / self.times * 100
        md5_percent = self.md5_success / self.times * 100
        sum_percent = (self.sc_success + self.mc_success + self.ac_success) / (3 * self.times) * 100
        rows = [
            {"测试项": "单个ascii码", "次数": self.times, "成功": self.sc_success, "失败": self.sc_fail,
             "成功率": "%.2f%%" % (sc_percent)},
            {"测试项": "多个ascii码", "次数": self.times, "成功": self.mc_success, "失败": self.mc_fail,
             "成功率": "%.2f%%" % (mc_percent)},
            {"测试项": "全部ascii码", "次数": self.times, "成功": self.ac_success, "失败": self.ac_fail,
             "成功率": "%.2f%%" % (ac_percent)},
            {"测试项": "总计", "次数": 3 * self.times, "成功": self.ac_success + self.mc_success + self.sc_success,
             "失败": self.ac_fail + self.mc_fail + self.sc_fail, "成功率": "%.2f%%" % (sum_percent)},
            {"测试项": "文件md5", "次数": self.times, "成功": self.md5_success, "失败": self.times - self.md5_success,
             "成功率": "%.2f%%" % md5_percent},
        ]
        with open("../report/"+"".join(self.ser.name.split("/")) + 'r.csv', 'w', newline='', encoding="utf-8")as f:
            l_csv = csv.writer(f)
            l_csv.writerow(device_baudrate)

            f_csv = csv.DictWriter(f, headers)
            f_csv.writeheader()
            f_csv.writerows(rows)
            l_csv.writerow([])