import os
import sys
sys.path.append("..")
import argparse
from ready import os,main

def start():
    if sys.platform=="win32":
        os.system("start ..\__init__.bat")
    else:
        os.system("bash ../__init__.sh")
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--times",type=int,default=10, help="test_times:number")
    parser.add_argument("-n", "--devices", default=None, help="devices_name:eg./dev/ttyXRUSB0,/dev/ttyXRUSB1>...")
    parser.add_argument("-b", default="115200", help="baudrates:eg.115200,9600...")
    parser.add_argument("-p",default="https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1596023159431&di=3f7647e07996527f0d5ecd12dbaf9aac&imgtype=0&src=http%3A%2F%2Fimg.ewebweb.com%2Fuploads%2F20190506%2F13%2F1557121349-oATrxwXZgC.jpg",help="path:Local address eg./home/kylin/a.jpg or network address eg.https://www.baidu.com/.../xxx.jpg")
    parser.add_argument("-t", action='store_true', default=False, help="main-up txserver:listening transmit data")
    parser.add_argument("-r", action='store_true', default=False, help="main-up rxserver:listening receive data")
    parser.add_argument("-tr", action='store_true', default=False, help="main-up run:listening transmit and receive data on this machine")
    #测试Ascii码选项
    parser.add_argument("-a",action='store_true', default=False, help="add Test ASCII code")
    #测试文件传输选项
    parser.add_argument("-f",action='store_true', default=False, help="add Test file transfer")
    #测试传输速率选项
    parser.add_argument("-s",action='store_true', default=False, help="add Test transmission rate")
    #测试所有项
    parser.add_argument("-A",action='store_true', default=False, help="add Test All")
    #清理生成的子报告
    try:
        for file in [file for file in os.listdir("../report/") if file.endswith("csv")]:
            os.remove("../report/"+file)
    except:
        pass
    try:
        os.remove("../total.csv")
    except:
        pass
    baudrates = []
    args = parser.parse_args()
    if True not in [args.a,args.s,args.f,args.A]:
        print("请输入测试项...")
        parser.print_help()
        sys.exit()
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