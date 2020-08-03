@echo off
rem 此以windows作为标准主板(默认com不存在问题)
rem python ../main/start.py -n com7 -t -a -b 115200 -c 100 
rem python ../main/start.py -n com7 -t -a -b 115200,9600 -c 100 
rem python ../main/start.py -n com7 -t -s -b 115200 
rem python ../main/start.py -n com7 -t -f -b 115200 -p ../main/a.txt -c 10
rem python ../main/start.py -n com7 -t -f -b 115200,9600 -p ../main/a.txt -c 10 
rem python ../main/start.py -n com7 -t -f -b 115200 -p ../main/a.jpg,../main/a.txt,../main/a.doc -c 5 
python ../main/start.py -n com7 -t -s -f -a -b 115200 -p ../main/a.jpg,../main/a.txt,../main/a.doc -c 5
rem python ../main/start.py -n /dev/ttyXRUSB0,/dev/ttyXRUSB1,/dev/ttyXRUSB2 -t -s -f -a -b 115200 -p ../main/a.jpg,../main/a.txt,../main/a.doc -c 5
pause