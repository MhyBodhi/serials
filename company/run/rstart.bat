@echo off
rem 此以windows作为标准主板(默认com不存在问题)
python start.py -r -n com7 rem 接收端测试,测试参数由发送端决定
rem python start.py -r -n com7 -b 115200,9600 rem 发送端指定多个波特率，接收端也需要指定
pause