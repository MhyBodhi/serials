import sys
import csv
import os
import time
from multiprocessing import Process,Lock
from threading import Thread
import serial

def run(ser,server,args):
    if server=="t":
        from realize.tserial import TSerial
        r = TSerial(ser,args)
        r.run()
    elif server=="r":
        from realize.rserial import RSerial
        r = RSerial(ser,args)
        r.run()
    elif server=="tr":
        from realize.trserial import TRSerial
        lock = Lock()
        r = TRSerial(ser, lock,args)
        r.run()

def main(baudrate,args,server):
    devices = []
    devices.extend(args.devices.split(","))
    print((devices,baudrate))
    sers = []
    for device in devices:
        try:
            sers.append(serial.Serial(device, baudrate,timeout=10))
        except:
            pass
    print(sers)
    plist = []
    if not sers:
        print("设备读取失败")
        return
    for ser in sers:
        if sys.platform == "win32":
            plist.append(Thread(target=run, args=(ser,server,args)))
        else:
            plist.append(Process(target=run, args=(ser,server,args)))
    for i in plist:
        i.start()
    for j in plist:
        j.join()
    # if server == "r" or server == "tr":
    #     report()

def getTime():
    now = time.strftime("%Y-%m-%d_%H_%M_%S")
    return now

def report():
    csvfiles = [file for file in os.listdir("../report/") if file.endswith("csv")]
    try:
        with open("../total.csv", "a", newline="", encoding="utf-8") as f:
            fw_csv = csv.writer(f)
            for csvfile in csvfiles:
                with open("../report/"+csvfile, "r", encoding="utf-8") as fl:
                    fr_csv = csv.reader(fl)
                    for row in fr_csv:
                        fw_csv.writerow(row)
    except Exception as e:
        print("生成总报告发生错误:",e)
        return