#!/bin/bash
sudo python3 ../main/start.py -n /dev/ttySWK0 -t -a -b 115200 -c 100 # 指定波特率测试100次ascii码
#sudo python3 ../main/start.py -n /dev/ttySWK0 -t -a -b 115200,9600 -c 100 # 指定多个波特率测试100次ascii码
#sudo python3 ../main/start.py -n /dev/ttySWK0 -t -s -b 115200 # 指定波特率,测试速率
#sudo python3 ../main/start.py -n /dev/ttySWK0 -t -f -b 115200 -p ../main/a.txt -c 10 # 传输文件
#sudo python3 ../main/start.py -n /dev/ttySWK0 -t -f -b 115200,9600 -p ../main/a.txt -c 10 # 指定多个波特率,传输文件
#sudo python3 ../main/start.py -n /dev/ttySWK0 -t -f -b 115200 -p ../main/a.jpg,../main/a.txt,../main/a.doc -c 5 # 指定多个文件传输
#sudo python3 ../main/start.py -n /dev/ttySWK0 -t -s -f -a -b 115200 -p ../main/a.jpg,../main/a.txt,../main/a.doc -c 5 # 测试所有项
#sudo python3 ../main/start.py -n /dev/ttyXRUSB0,/dev/ttyXRUSB1,/dev/ttyXRUSB2 -t -s -f -a -b 115200 -p ../main/a.jpg,../main/a.txt,../main/a.doc -c 5 # 多进程测试所有项