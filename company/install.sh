#!/usr/bin/bash
test -e ~/.pip/pip.conf
if [ $? -ne 0 ];then
	mkdir ~/.pip
	cat > ~/.pip/pip.conf <<-MHY
		[global]
		timeout = 6000
		index-url = https://pypi.tuna.tsinghua.edu.cn/simple
		trusted-host = pypi.tuna.tsinghua.edu.cn	
	MHY
fi
sudo apt -y update && sudo apt -y install python3-pip && sudo python3 -m pip install --upgrade pip && sudo python3 -m pip install pyserial && pip install redis && sudo python3 -m pip install requests