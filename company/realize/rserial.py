import json
import time
import os
import logging.config
import logging
from basic.basic import Basic

logging.config.fileConfig("../log/rlog.conf")
logging = logging.getLogger()

class RSerial(Basic):
    def __init__(self,ser,args):
        super().__init__(ser,args)
        self.dstpath = None

    def ininConnect(self):
        logging.info("连接tserver...")
        #建立连接...
        while True:
            self.devices = self.redis.hvals("devices")
            if self.ser.in_waiting:
                device_data = ""
                try:
                    device_data = self.ser.read(20).decode("utf-8")
                    logging.info(("包含设备名称数据：", device_data))
                except Exception as e:
                    print("错误1:", e)
                try:
                    self.device_name = [device for device in self.devices if device in device_data][0]
                    logging.info(("设备名称:", self.device_name))
                except Exception as e:
                    print("错误2:", e)
                if self.device_name:
                    self.tstatus = self.device_name + "status"
                    self.redis.hmset(self.tstatus, {"read": 1,"end": 0})
                    logging.info("正在建立连接...")
                    break
                else:
                    logging.info("缓冲区收到数据...不支持该波特率...")
                    time.sleep(1)
            else:
                time.sleep(3)

        # 清理input缓冲区
        while True:
            if self.redis.hget(self.tstatus, "ok") == "1":
                self.ser.reset_input_buffer()
                break

    def readFiles(self):
        #接收文件
        logging.info("测试接收文件...")
        self.dstpath = "../resources/"+self.fileprefix+"dst." + self.redis.hget(self.tstatus,"filetype")
        self.dstfile = open(self.dstpath, "wb")
        self.receive_time = 0
        while True:
            self.trstatus = self.redis.hget(self.tstatus, "trstatus")
            self.bytes_number = int(self.redis.hget(self.tstatus,"bytes_number"))
            if self.trstatus == "read":
                #改变nextfile状态
                self.redis.hset(self.tstatus,"nextfile",0)
                self.fileenable = int(self.redis.hget(self.tstatus, "fileenable"))
                if self.fileenable:
                    if self.ser.in_waiting:
                        start_time = time.time()
                        recstr = self.ser.read(self.bytes_number)  # self.bytes_number
                        end_time = time.time()
                        self.receive_time += end_time - start_time
                        self.dstfile.write(recstr)
                        self.redis.hset(self.tstatus,"trstatus","write")
                    # else:
                    #     logging.info("等待缓冲区出现数据...")
                    #     time.sleep(0.1)
                else:
                    logging.info("接收文件完成")
                    self.dstfile.close()
                    logging.info("接收文件大小(字节):%s"%os.path.getsize(self.dstpath))
                    # 清理缓冲区内容
                    self.ser.reset_input_buffer()
                    self.redis.hset(self.tstatus, "trstatus", "write")
                    break
        logging.info("测试接收文件完成")

    def readAscii(self):
        #接收Ascii码
        logging.info("测试读取Ascii码...")
        while True:
            self.trstatus = self.redis.hget(self.tstatus, "trstatus")
            if self.trstatus == "read":
                self.bytes_number = int(self.redis.hget(self.tstatus, "bytes_number"))
                self.startcontent = self.redis.hget(self.tstatus, "ascii")
                if self.ser.in_waiting:
                    logging.info("read...")
                    try:
                        print("接收字节数",self.bytes_number)
                        text = self.ser.read(self.bytes_number).decode("utf-8")

                        print("接收ascii码",text)
                        self.endcontent = text
                    except Exception as e:
                        logging.info(e)
                        self.endcontent = None
                    yield self.startcontent == self.endcontent
                    if len(self.startcontent) == 256:
                        #清理缓冲区内容
                        self.ser.reset_input_buffer()
                        self.redis.hset(self.tstatus, "trstatus","write")
                        break
                    #清理缓冲区
                    self.ser.reset_input_buffer()
                    self.redis.hset(self.tstatus, "trstatus", "write")
        logging.info("测试读取Ascii码完成")

    def getReadSpeed(self):
        #测试接收速率
        times = 10
        logging.info("测试" + str(self.times) + "次接收速率...")
        while times:
            self.trstatus = self.redis.hget(self.tstatus, "trstatus")
            self.bytes_number = int(self.redis.hget(self.tstatus, "bytes_number"))
            if self.trstatus == "read":
                if self.ser.in_waiting:
                    self.receive_start = time.time()
                    receivestr = self.ser.read(self.bytes_number).decode("utf-8")
                    self.receive_end = time.time()
                    # 接收数据速率
                    if self.receive_end - self.receive_start:
                        self.receive_speeds += self.bytes_number / (self.receive_end - self.receive_start) / 1024
                    else:
                        self.receive_speed_zero = True
                    self.redis.hset(self.tstatus,"trstatus","write")
                    times -= 1
        # 清理缓冲区内容
        self.ser.reset_input_buffer()
        logging.info("测试接收速率完成")

    def read(self):
        times = 1
        #与tserver建立连接初始化...
        self.ininConnect()
        self.files = self.redis.hget(self.tstatus,"files")
        self.times = int(self.redis.hget(self.tstatus, "reporttimes"))
        self.redis.hset(self.tstatus, "transmit", 1)
        args_f = int(self.redis.hget(self.tstatus, "f"))
        if args_f:
            self.args.f = True
        else:
            self.args.f = False
        args_a = int(self.redis.hget(self.tstatus, "a"))
        if args_a:
            self.args.a = True
        else:
            self.args.A =False
        args_s = int(self.redis.hget(self.tstatus, "s"))
        if args_s:
            self.args.s = True
        else:
            self.args.s = False
        args_A = int(self.redis.hget(self.tstatus, "A"))
        if args_A:
            self.args.A = True
        else:
            self.args.A =False
        logging.info("start test receive ...")
        while True:
            if times>self.times:
                break
            if self.args.f or self.args.A:
                self.files = json.loads(self.redis.hget(self.tstatus,"files"))
                for url in self.files:

                    self.readFiles()
                    if times == 1:
                        self.files_nature[url] = {"size": self.redis.hget(self.tstatus,"srcfilesize"),"time": 0,"success": 0}
                    # 验证md5
                    if self.redis.hget(self.tstatus,"srcmd5") == self.getFileMd5(self.dstpath):
                        self.files_nature[url]["success"] += 1
                    else:
                        logging.error(("文件%s"%url,"第"+str(times)+"次时md5失败"))
                    #累计当前文件传输时间
                    self.files_nature[url]["time"] += float(self.redis.hget(self.tstatus,"send_time"))+self.receive_time
                    #启动接收文件功能
                    self.redis.hset(self.tstatus, "fileenable", 1)
                    # 执行初始化下次测试
                    self.redis.hset(self.tstatus,"nextfile",1)
            if self.args.a or self.args.A:
                logging.info("read测试Ascii码...")
                for result in self.readAscii():
                    yield result
                    if not result:
                        if len(self.startcontent) == 1:
                            logging.error("单个ascii码第"+str(times)+"次时测试失败")
                        elif 1 < len(self.startcontent) < 256:
                            logging.error("多个ascii码第"+str(times)+"次时测试失败")
                        elif len(self.startcontent) == 256:
                            logging.error("全部ascii码第" + str(times) + "次时测试失败")
                logging.info("read测试Ascii码完成")
            logging.info("read测试第"+str(times)+"次完成")
            times += 1
        # 测试接收速率
        if self.args.s or self.args.A:
            logging.info("read测试接收速率...")
            self.getReadSpeed()
            logging.info("read测试接收速率完成")

        if self.redis.hget(self.tstatus, "write") == "0":
            print("完成...")
            self.redis.hmset(self.tstatus, {"end": 1, "read": 0,"trstatus":"write"})
        logging.info("receive over")
        self.redis.hset("main","times",int(self.redis.hget("main","times"))+1)

    def run(self):
        logging.info("main receive...")
        results = self.read()
        for result in results:
            if result == False:
                self.ser.reset_input_buffer()
                if (len(self.startcontent)) == 1:
                    self.sc_fail += 1
                elif 1 < len(self.startcontent) < 256:
                    self.mc_fail += 1
                elif len(self.startcontent) == 256:
                    self.ac_fail += 1
            elif result == True:
                if (len(self.startcontent)) == 1:
                    self.sc_success += 1
                elif 1 < len(self.startcontent) < 256:
                    self.mc_success += 1
                elif len(self.startcontent) == 256:
                    self.ac_success += 1
        print("开始生成报告")
        self.report()