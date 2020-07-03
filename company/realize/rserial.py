import time
from basic.basic import logging,Basic


class RSerial(Basic):
    def __init__(self,ser,args):
        super().__init__(ser,args)
        self.dstfile = open(self.fileprefix+"dst","wb")
        self.devices = self.redis.hvals("devices")

    def read(self):
        times = 1
        filestatus = 0
        while True:
            if self.ser.in_waiting:
                device_data = ""
                try:
                    device_data = self.ser.read(20).decode("utf-8")
                    logging.info(("包含设备名称数据：",device_data))
                except Exception as e:
                    print("错误1:", e)
                    pass
                try:
                    self.device_name =  [device  for device in self.devices if device in device_data][0]
                    logging.info(("设备名称:",self.device_name))
                except Exception as e:
                    print("错误2:",e)
                if self.device_name:
                    logging.info("执行到了这里...")
                    self.tstatus = self.device_name + "status"
                    logging.info(("self.tstatus", self.tstatus))
                    logging.info(("缓冲区大小", self.ser.in_waiting))
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

        #清理input缓冲区
        while True:
            if self.redis.hget(self.tstatus,"ok")=="1":
                self.ser.reset_input_buffer()
                break
        self.redis.hset(self.tstatus, "transmit", 1)
        self.times = int(self.redis.hget(self.tstatus,"reporttimes"))
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
                            if self.getFileMd5(self.fileprefix+"dst")==self.redis.hget(self.tstatus,"srcmd5"):
                                self.md5_success += 1
                        logging.info(("接收到的bytes-number", self.bytes_number))
                        try:
                            rdata = self.ser.read(self.bytes_number).decode("utf-8")
                        except:
                            pass
                        self.startcontent = self.redis.hget(self.tstatus,"ascii")
                        logging.info(("接收到的数据：",rdata))
                        yield rdata == self.startcontent
                        if int(self.redis.hget(self.tstatus,"srcfile")) and times < 3 * self.times:
                            self.redis.hset(self.tstatus,"fileenable",1)
                            self.dstfile = open(self.fileprefix+"dst", "wb")
                        filestatus = 0
                        times += 1
                if self.redis.hget(self.tstatus, "write") == "0":
                    self.redis.hmset(self.tstatus, {"end": 1, "read": 0})
                    break
                self.redis.hset(self.tstatus, "trstatus", "write")

    def run(self):
        logging.info("start receive...")
        results = self.read()
        for result in results:
            if result == False:
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
                logging.info("测试通过!")
        self.report()