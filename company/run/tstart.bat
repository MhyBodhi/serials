@echo off
rem 此以windows作为标准主板(默认com不存在问题)
python ../main/start.py -n com7 -t -a -b 115200 -c 100 rem 指定波特率测试100次ascii码
rem python ../main/start.py -n com7 -t -a -b 115200,9600 -c 100 rem 指定多个波特率测试100次ascii码
rem python ../main/start.py -n com7 -t -s -b 115200 rem 指定波特率测试速率
rem python ../main/start.py -n com7 -t -f -b 115200 -p ../main/a.txt -c 10 rem 传输文件
rem python ../main/start.py -n com7 -t -f -b 115200,9600 -p ../main/a.txt -c 10 rem 指定多个波特率,传输文件
rem python ../main/start.py -n com7 -t -f -b 115200 -p ../main/a.jpg,../main/a.txt,../main/a.doc -c 5 rem 指定多个文件传输
rem python ../main/start.py -n com7 -t -s -f -a -b 115200 -p ../main/a.jpg,../main/a.txt,../main/a.doc -c 5 rem 测试所有项
rem python ../main/start.py -n /dev/ttyXRUSB0,/dev/ttyXRUSB1,/dev/ttyXRUSB2 -t -s -f -a -b 115200 -p ../main/a.jpg,../main/a.txt,../main/a.doc -c 5 rem 多进程测试所
pause