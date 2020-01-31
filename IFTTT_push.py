# -*- coding: utf-8 -*-

import json
import requests
import pandas as paths
import socket

from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

get_Data_URL = "https://view.inews.qq.com/g2/getOnsInfo"
sub_doc_path = 'subscribed_urls.csv'

post_url_p1 = "https://maker.ifttt.com/trigger/"
post_url_p2 = "/with/key/"
post_urls = ["https://view.inews.qq.com/g2/getOnsInfo/program_push/with/key/fP7Zt7dO7IqmDBZI49uEUfagP4rnYK9gD5jTLYmKMRG",]
host_name = socket.gethostname()


def output_log(log_text): print("[", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "] ", log_text)

def get_data():
    output_log("开启一轮推送。\n")
    try:
        global post_urls
        post_urls = read_urls(sub_doc_path)
        output_log("读取到" + str(len(post_urls)) + "条订阅地址。\n")
    except:
        output_log("订阅地址获取失败！请检查程序！\n")
    
    output_log("正获取数据自 " + get_Data_URL)

    try:
        res = requests.post(get_Data_URL, {"name": "disease_h5"})
        res_timeline = requests.post(get_Data_URL, {"name": "wuwei_ww_time_line"})
        data = json.loads(json.loads(res.text)['data'])
        news = json.loads(json.loads(res_timeline.text)['data'])

        data_dome = data['chinaTotal']
        text_dome = "\\n🇨🇳全国数据：\\n截止" + str(data['lastUpdateTime']) + " GMT+8：\\n确诊:" + str(data_dome['confirm']) + "\\t疑似:" + str(data_dome['suspect']) + "\\n死亡:" + str(data_dome['dead']) + "\\t治愈:" + str(data_dome['heal'])
        
        text_dome = text_dome + "\\n\\n📰最新消息："
        for i in range(4):
            text_dome = text_dome + "\\n[]" + news[i]['time'] + "]" + news[i]['title']

        data_prov = data['areaTree'][0]['children'][25]
        text_prov = "\\n🏙宁夏数据：\\n确诊:"
        text_prov = text_prov + str(data_prov['total']['confirm']) + "(+" + str(data_prov['today']['confirm']) + ")\\t疑似:" + str(data_prov['total']['suspect']) + "(+" + str(data_prov['today']['suspect']) + ")\\n死亡:" + str(data_prov['total']['dead']) + "(+" + str(data_prov['today']['dead']) + ")\\t\\t治愈:" + str(data_prov['total']['heal']) + "(+" + str(data_prov['today']['heal']) + ")\\n"
        for city in data_prov['children']:
            text_prov = text_prov + "▪" + city['name'] + "数据:\\n确诊:" + str(city['total']['confirm']) + "(+" + str(city['today']['confirm']) + ")\\t\\t疑似:" + str(city['total']['suspect']) + "(+" + str(city['today']['suspect']) + ")\\n死亡:" + str(city['total']['dead']) + "(+" + str(city['today']['dead']) + ")\\t\\t治愈:" + str(city['total']['heal']) + "(+" + str(city['today']['confirm']) + ")\\n"

        output_log("数据获取成功，准备推送至IFTTT。")
        IFTTT_push(text_dome, text_prov, False)
    except:
        try:
            IFTTT_push("数据获取失败。", "请拨冗通知服务运营者。", True)
            output_log("数据获取失败！请检查程序！\n")
        except:
            output_log("数据获取失败！请检查网路！\n")
    
    output_log("本轮推送结束。")
#    vars = (res, res, data_dome, text_dome, data_prov, text_prov, text_prov)
#    for var in vars: del var
#    output_log("变量释放完成。\n")

def IFTTT_push(push_text_1, push_text_2, silent_mode):
    push_val1_text = "2019-nCoV 数据推送\\n推送时间：" + datetime.now().strftime("%Y-%m-%d %H:%M") + " GMT+8\\n推送设备：" + host_name + "\\n推送内容："
    push_val2_text = "\\n" + push_text_1
    push_val3_text = "\\n" + push_text_2 + "\\n"
    body = "{ \"value1\": \"" + push_val1_text + "\", \"value2\": \"" + push_val2_text + "\", \"value3\": \"" + push_val3_text + "\" }"
    headers = { 'Content-Type': 'application/json' }

    try:
        for url in post_urls:
            requests.post(url, data = body.encode('utf-8'), headers = headers)
            if not silent_mode: output_log("已完成对" + str(len(post_urls)) + "个地址的推送。\n")
    except:
        output_log("推送失败，请检查设置！\n")

def read_urls(path):
    a = paths.read_csv(path)
    names = a['event_name']
    keys  = a['key']
    urls  = [post_url_p1 + names[i] + post_url_p2 + keys[i] for i in range(len(names))]
    return urls

if __name__ == "__main__":
    post_urls = read_urls(sub_doc_path)
    IFTTT_push("程序已上线。","推送模式：整点推送。", True)

    output_log("程序已上线。")
    output_log("当前设备 Host Name: " + host_name + "\n")

    output_log("开始运行推送服务。推送模式：整点推送。\n")
    get_data()
    scheduler = BlockingScheduler()
    trigger = CronTrigger(hour='*/1')
    scheduler.add_job(get_data,trigger)
    scheduler.start()