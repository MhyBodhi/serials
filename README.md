串口本机、多机收发测试
=============

## 测试项
  * ascii码
      1. 单个ascii码
      2. 多个ascii码
      3. 全部ascii码
  * 文件md5
      1. 文件格式不限制
  * 传输速率
      1. 发送速率
      2. 接收速率

## 选项与使用
### 参数
  1. 指定测试端，必须参数
    -tr为本机自收发测试
    -t指定本机为发送数据端
    -r指定本机为接受数据端
  2. 指定波特率
    -b指定单个或多个波特率,多个以逗号分隔eg.-b 115200,9600,19200，默认值115200
  3. 指定测试设备
    -n单个或多个设备，指定多个设备时为开启多线程模式eg.-n /dev/ttyXRUSB0,/dev/ttyXRUSB1,/dev/ttyXRUSB2，必选参数，无默认值
  4. 指定测试源文件路径,本地或网络路径
    -p 指定本地或网络路径作为传输源文件,eg.-p /home/kylin/a.jpg or -p https://.../.../xxx.jpg
    执行测试文件队列，文件间以逗号分隔,eg.-p /home/kylin/a.jpg,/home/kylin/a.txt,./a.doc
  5. 指定测试次数
    -c 指定测试次数number,eg.-c 10，默认值为10次
  6. 指定测试项
    -f 增加测试文件
    -a 增加测试Ascii码
    -s 增加测试传输速率
    -A 增加测试所有项

### 例子
        sudo python3 ../main/start.py -n /dev/ttySWK0 -tr -a -b 115200 -c 100 # 指定波特率测试100次ascii码
        sudo python3 ../main/start.py -n /dev/ttySWK0 -tr -a -b 115200,9600 -c 100 # 指定多个波特率测试100次ascii码`
        sudo python3 ../main/start.py -n /dev/ttySWK0 -tr -s -b 115200 # 指定波特率,测试速率
        sudo python3 ../main/start.py -n /dev/ttySWK0 -tr -f -b 115200 -p ../main/a.txt -c 10 # 传输文件
        sudo python3 ../main/start.py -n /dev/ttySWK0 -tr -f -b 115200,9600 -p ../main/a.txt -c 10 # 指定多个波特率,传输文件
        sudo python3 ../main/start.py -n /dev/ttySWK0 -tr -f -b 115200 -p ../main/a.jpg,../main/a.txt,../main/a.doc -c 5 # 指定多个文件传输
        sudo python3 ../main/start.py -n /dev/ttySWK0 -tr -s -f -a -b 115200 -p ../main/a.jpg,../main/a.txt,../main/a.doc -c 5 # 测试所有项
        sudo python3 ../main/start.py -n /dev/ttySWK0,/dev/ttySWK1,/dev/ttyS4 -tr -a -b 115200 -c 100 # 多进程测试ascii码
        sudo python3 ../main/start.py -n /dev/ttySWK0,/dev/ttySWK1,/dev/ttyS4 -tr -s -f -a -b 115200 -p ../main/a.jpg,../main/a.txt,../main/a.doc -c 5 # 多进程测试所有项
   
## 安装
   * 执行bash install.sh安装kylin机依赖
   * 多机收发通过redis建立的通信，需要安装配置redis,修改redis配置文件,将监听地址改为0.0.0.0,启动redis,eg.redis-server xxx.conf 
