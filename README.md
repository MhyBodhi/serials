串口本机、多机收发测试
=============

## 测试项
  * ascii码
      1. 单个ascii码
      2. 多个ascii码
      3. 全部ascii码
  * 文件md5
      1.文件格式不限制

## 选项与使用
### 参数
  1. 指定测试端，必须参数
    - -tr为本机自收发测试
    - -t指定本机为发送数据端
    - -r指定本机为接受数据端
  2. 指定波特率
    - -b指定单个或多个波特率,多个以逗号分隔eg.-b 115200,9600,19200，默认值115200
  3. 指定测试设备
    - -n单个或多个设备，指定多个设备时为开启多线程模式eg.-n /dev/ttyXRUSB0,/dev/ttyXRUSB1,/dev/ttyXRUSB2，必选参数，无默认值
  4. 指定测试源文件路径,本地或网络路径
    - -p 指定本地或网络路径作为传输源文件,eg.-p /home/kylin/a.jpg or -p https://ss0.bdstatic.com/.../xxx.jpg，默认值为一网络路径
    - 支持txt、png、jpg、doc、pdf、mp3、MP4等文件格式，严格上文件格式无要求
  5. 指定测试次数
    - -c 指定测试次数number,eg.-c 10，默认值为10次

## 例子
  * linux：
    1. 自收发,eg.sudo python3 ../main/start.py  -tr -n /dev/ttyXRUSB0,/dev/ttyXRUSB1,/dev/ttyXRUSB2 -c 3 -p /home/kylin/a.jpg
    2. 发送数据端,eg.sudo python3 ../main/start.py -n /dev/ttyXRUSB0 -t -b 115200 -c 3 -p /home/kylin/a.txt
    3. 接收数据端,eg.sudo python3 ../main/start.py -n /dev/ttyXRUSB0 -r -b 115200
  * windows:
    1. 自收发,eg.sudo python3 ../main/start.py  -tr -n com3,com4,com5 -c 3 -p C:\Users\zhang\Desktop\a.jpg
    2. 发送数据端,eg.sudo python3 ../main/start.py -n com3 -t -b 115200 -c 3 -p C:\Users\zhang\Desktop\a.jpg
    3. 接收数据端,eg.sudo python3 ../main/start.py -n com3 -r -b 115200
