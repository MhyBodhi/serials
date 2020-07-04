import sys
sys.path.append("..")
import argparse
from basic.basic import logging
from main import os,main

def start():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--times", type=int, default=10, help="test_times:number")
    parser.add_argument("-n", "--devices", default=None, help="devices_name:eg./dev/ttyXRUSB0,/dev/ttyXRUSB1>...")
    parser.add_argument("-b", default="115200", help="baudrates:eg.115200,9600...")
    parser.add_argument("-p",default="https://ss1.bdstatic.com/70cFvXSh_Q1YnxGkpoWK1HF6hhy/it/u=3455238864,153902017&fm=26&gp=0.jpg",help="url:download image eg.https://www.baidu.com/.../xxx.jpg")
    parser.add_argument("-t", action='store_true', default=False, help="txserver:threading transmit data")
    parser.add_argument("-r", action='store_true', default=False, help="rxserver:listening receive dat")
    parser.add_argument("-tr", action='store_true', default=False, help="trlocal:local transmit and receive data")
    try:
        os.remove("../total.csv")
    except:
        pass
    baudrates = []
    args = parser.parse_args()
    if (args.tr and args.r) or (args.tr and args.t):
        logging.info("参数输入有误")
        parser.print_help()
        sys.exit()
    elif args.t and args.r:
        logging.info("参数输入有误")
        parser.print_help()
        sys.exit()
    elif args.tr:
        server = "tr"
    elif args.t:
        server = "t"
    elif args.r:
        server = "r"
    else:
        logging.info("请输入参数确认发送或接收数据-t or -r \n本地测试请输入参数-tr")
        parser.print_help()
        sys.exit()
    baudrates.extend(args.b.split(","))
    logging.info(baudrates)
    if args.devices==None:
        logging.info("请输入设备名称,-n")
        parser.print_help()
        sys.exit()
    for baudrate in baudrates:
        main(baudrate,args,server)

if __name__ == '__main__':
    start()