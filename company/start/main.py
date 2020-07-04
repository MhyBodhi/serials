import csv
import os
import threading
from threading import Lock
import serial
from realize.tserver import TSerial
from realize.rserial import RSerial
from trlocal.trlocal import Serial
from basic.basic import logging


def run(ser,server,args):
    if server=="t":
        r = TSerial(ser,args)
        r.run()
    elif server=="r":
        r = RSerial(ser,args)
        r.run()
    elif server=="tr":
        lock = Lock()
        r = Serial(ser, lock,args)
        r.run()

def main(baudrate,args,server):
    devices = []
    devices.extend(args.devices.split(","))
    logging.info((devices,baudrate))
    sers = []
    for device in devices:
        try:
            sers.append(serial.Serial(device, baudrate, timeout=None))
        except:
            pass
    logging.info(sers)
    plist = []
    if not sers:
        logging.info("设备读取失败")
        return
    for ser in sers:
        plist.append(threading.Thread(target=run, args=(ser,server,args)))
    for i in plist:
        i.start()
    for j in plist:
        j.join()
    if server == "r":
        report()

def report():
    csvfiles = [file for file in os.listdir(".") if file.endswith("csv")]
    try:
        with open("../total.csv", "a", newline="", encoding="utf-8") as f:
            fw_csv = csv.writer(f)
            for csvfile in csvfiles:
                with open(csvfile, "r", encoding="utf-8") as fl:
                    fr_csv = csv.reader(fl)
                    for row in fr_csv:
                        fw_csv.writerow(row)
                try:
                    os.remove(csvfile)
                except:
                    pass
    except Exception as e:
        return