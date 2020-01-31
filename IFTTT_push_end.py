# -*- coding: utf-8 -*-
import requests
import socket
import pandas as paths
from datetime import datetime

get_Data_URL = "https://view.inews.qq.com/g2/getOnsInfo"
sub_doc_path = 'subscribed_urls.csv'

post_url_p1 = "https://maker.ifttt.com/trigger/"
post_url_p2 = "/with/key/"
post_urls = ["https://maker.ifttt.com/trigger/program_push/with/key/fP7Zt7dO7IqmDBZI49uEUfagP4rnYK9gD5jTLYmKMRG",]

def read_urls(path):
    a = paths.read_csv(path)
    names = a['event_name']
    keys  = a['key']
    urls  = [post_url_p1 + names[i] + post_url_p2 + keys[i] for i in range(len(names))]
    return urls

host_name = socket.gethostname()

push_val1_text = "2019-nCoV 数据推送\\n推送时间：" + datetime.now().strftime("%Y-%m-%d %H:%M") + " GMT+8\\n推送设备：" + host_name + "\\n推送内容："
push_val2_text = "\\n" + "程序下线。"
push_val3_text = "\\n" + "如果没有提前接到通知，请拨冗通知服务运营者，谢谢！" + "\\n\\n"
body = "{ \"value1\": \"" + push_val1_text + "\", \"value2\": \"" + push_val2_text + "\", \"value3\": \"" + push_val3_text + "\" }"
headers = { 'Content-Type': 'application/json' }

for url in post_urls:
    requests.post(url, data = body.encode('utf-8'), headers = headers)
