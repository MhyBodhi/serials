import os
import sys
sys.path.append("..")
import argparse
from ready import os,main

def start():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--times",type=int,default=10, help="test_times:number")
    parser.add_argument("-n", "--devices", default=None, help="devices_name:eg./dev/ttyXRUSB0,/dev/ttyXRUSB1>...")
    parser.add_argument("-b", default="115200", help="baudrates:eg.115200,9600...")
    parser.add_argument("-p",default="https://ss1.bdstatic.com/70cFvXSh_Q1YnxGkpoWK1HF6hhy/it/u=3455238864,153902017&fm=26&gp=0.jpg",help="path:Local address eg./home/kylin/a.jpg or network address eg.https://www.baidu.com/.../xxx.jpg")
    parser.add_argument("-t", action='store_true', default=False, help="main-up txserver:listening transmit data")
    parser.add_argument("-r", action='store_true', default=False, help="main-up rxserver:listening receive data")
    parser.add_argument("-tr", action='store_true', default=False, help="main-up run:listening transmit and receive data on this machine")

    #清理生成的子报告
    for file in [file for file in os.listdir("../report/") if file.endswith("csv")]:
        os.remove("../report/"+file)
    try:
        os.remove("../total.csv")
    except:
        pass
    baudrates = []
    args = parser.parse_args()
    if (args.tr and args.r) or (args.tr and args.t):
        print("参数输入有误")
        parser.print_help()
        sys.exit()
    elif args.t and args.r:
        print("参数输入有误")
        parser.print_help()
        sys.exit()
    elif args.tr:
        server = "tr"
    elif args.t:
        server = "t"
    elif args.r:
        server = "r"
    else:
        print("\n请输入参数确认发送或接收数据-t or -r \n本地自收发测试请输入参数-tr")
        parser.print_help()
        sys.exit()
    baudrates.extend(args.b.split(","))
    if args.devices==None:
        print("请输入设备名称,-n")
        parser.print_help()
        sys.exit()
    for baudrate in baudrates:
        main(baudrate,args,server)

if __name__ == '__main__':
    start()