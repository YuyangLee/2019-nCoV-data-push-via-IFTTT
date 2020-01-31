# -*- coding: utf-8 -*-
import requests
import socket
from datetime import datetime

post_url = "https://maker.ifttt.com/trigger/program_push/with/key/fP7Zt7dO7IqmDBZI49uEUfagP4rnYK9gD5jTLYmKMRG"
host_name = socket.gethostname()

push_val1_text = "2019-nCoV 数据推送\\n推送时间：" + datetime.now().strftime("%Y-%m-%d %H:%M") + " GMT+8\\n推送设备：" + host_name + "\\n推送内容："
push_val2_text = "\\n" + "程序下线。"
push_val3_text = "\\n" + "如果没有提前接到通知，请拨冗通知服务运营者，谢谢！" + "\\n"
body = "{ \"value1\": \"" + push_val1_text + "\", \"value2\": \"" + push_val2_text + "\", \"value3\": \"" + push_val3_text + "\" }"
headers = { 'Content-Type': 'application/json' }

requests.post(post_url, data = body.encode('utf-8'), headers = headers)