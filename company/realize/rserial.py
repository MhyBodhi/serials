import time
import os
import logging.config
from basic.basic import Basic

logging.config.fileConfig("../log/rlog.conf")
logging = logging.getLogger()


class RSerial(Basic):
    def __init__(self,ser,args):
        super().__init__(ser,args)
        self.dstpath = "../resources/"+self.fileprefix+"dst."

    def ininConnect(self):
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
                    pass
                try:
                    self.device_name = [device for device in self.devices if device in device_data][0]
                    logging.info(("设备名称:", self.device_name))
                except Exception as e:
                    print("错误2:", e)
                if self.device_name:
                    self.tstatus = self.device_name + "status"
                    self.redis.hmset(self.tstatus, {"read": 1})
                    self.redis.hmset(self.tstatus, {"end": 0})
                    logging.info("正在建立连接...")
                    break
                else:
                    logging.info("缓冲区收到数据...")
                    logging.info("与tserver未建立连接...")
                    time.sleep(1)
            else:
                logging.info("与tserver未建立连接...")
                time.sleep(3)

        # 清理input缓冲区
        while True:
            if self.redis.hget(self.tstatus, "ok") == "1":
                self.ser.reset_input_buffer()
                break

    def readFiles(self):
        #接收文件
        logging.info("测试接收文件...")
        while True:
            self.trstatus = self.redis.hget(self.tstatus, "trstatus")
            self.bytes_number = int(self.redis.hget(self.tstatus,"bytes_number"))
            if self.trstatus == "read":
                #改变nextfile状态
                self.redis.hset(self.tstatus,"nextfile",0)
                self.fileenable = int(self.redis.hget(self.tstatus, "fileenable"))
                if self.fileenable:
                    if self.ser.in_waiting:
                        recstr = self.ser.read(self.bytes_number)  # self.bytes_number
                        self.dstfile.write(recstr)
                        self.redis.hset(self.tstatus,"trstatus","write")
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
                    self.redis.hset(self.tstatus, "trstatus", "write")
                    break

        logging.info("测试接收文件完成")

    def read(self):
        times = 1
        filestatus = 0
        #与tserver建立连接初始化...
        self.ininConnect()


        self.filetype = self.redis.hget(self.tstatus,"files")
        self.times = int(self.redis.hget(self.tstatus, "reporttimes"))
        self.redis.hset(self.tstatus, "transmit", 1)
        self.dstfile = open(self.dstpath+self.filetype, "wb")
        logging.info("准备接收数据...")

        while True:
            if times>3*self.times:
                break
            self.trstatus = self.redis.hget(self.tstatus,"trstatus")

            if self.trstatus=="read":
                rdata = ""
                self.bytes_number = int(self.redis.hget(self.tstatus, "bytes_number"))
                self.fileenable = int(self.redis.hget(self.tstatus, "fileenable"))
                if self.ser.in_waiting:
                    if self.fileenable:
                        rdata = self.ser.read(self.bytes_number)
                        self.dstfile.write(rdata)
                        filestatus = 1
                    else:
                        if filestatus:
                            self.dstfile.close()
                            logging.info(("接收生成文件大小",os.path.getsize(self.dstpath+self.filetype)))
                            if self.getFileMd5(self.dstpath+self.filetype)==self.redis.hget(self.tstatus,"srcmd5"):
                                self.md5_success += 1
                        try:
                            self.receive_start = time.time()
                            rdata = self.ser.read(self.bytes_number).decode("utf-8")
                            self.receive_end = time.time()
                        except:
                            pass
                        self.startcontent = self.redis.hget(self.tstatus,"ascii")
                        logging.info(("接收到的字节大小：",len(rdata.encode("utf-8"))))
                        yield rdata == self.startcontent
                        if int(self.redis.hget(self.tstatus,"srcfile")) and times < 3 * self.times:
                            self.redis.hset(self.tstatus,"fileenable",1)
                            self.dstfile = open(self.dstpath+self.filetype, "wb")
                        filestatus = 0
                        times += 1

                if self.redis.hget(self.tstatus, "write") == "0":
                    self.redis.hmset(self.tstatus, {"end": 1, "read": 0})
                    break
                self.redis.hset(self.tstatus, "trstatus", "write")

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
                logging.info("测试失败!")
            elif result == True:
                if (len(self.startcontent)) == 1:
                    self.sc_success += 1
                elif 1 < len(self.startcontent) < 256:
                    self.mc_success += 1
                elif len(self.startcontent) == 256:
                    self.ac_success += 1
                    #接收数据速率
                    if self.receive_end - self.receive_start:
                        self.receive_speed += self.bytes_number/(self.receive_end - self.receive_start) /1024
                    else:
                        self.receive_speed_zero = True
                logging.info("测试通过!")
        self.transmit_speed = float(self.redis.hget(self.tstatus,"transmitspeed"))
        self.report()