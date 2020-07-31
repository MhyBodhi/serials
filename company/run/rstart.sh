#!/bin/bin
sudo python3 ../main/start.py -r -n /dev/ttySWK0 # 接收端测试,测试参数由发送端决定
#sudo python3 ../main/start.py -r -n /dev/ttySWK0 -b 115200,9600 # 发送端指定多个波特率，接收端也需要指定