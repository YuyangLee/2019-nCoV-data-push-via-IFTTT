# -*- coding: utf-8 -*-
import json
import requests
import pandas as pds
import socket
import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

cur_version = "1.2.0 Alpha"

get_Data_URL = "https://view.inews.qq.com/g2/getOnsInfo"
sub_doc_path = r"subscribed_urls.csv"

post_url_p1 = "https://maker.ifttt.com/trigger/"
post_url_p2 = "/with/key/"
host_name   = socket.gethostname()

CEE_date = datetime.date(2020, 6, 7)    # 这一字符串是推送地址数据的 csv 文件地址
area_requested = ['宁夏', '湖北']        # 这一列表包含了你订阅数据的省（自治区、直辖市）

def output_log(log_text): print("[", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "] ", log_text)

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
        text_dome = "\\n🇨🇳全国数据:\\n截止" + str(data['lastUpdateTime']) + " GMT+8:\\n确诊:" + str(data_dome['confirm']) + "\\t疑似:" + str(data_dome['suspect']) + "\\n死亡:" + str(data_dome['dead']) + "\\t治愈:" + str(data_dome['heal'])
        text_prov = "\\n"

        text_dome = text_dome + "\\n\\n📰最新消息:"
        for i in range(2):
            index = len(news) - 1 - i
            text_dome = text_dome + "\\n[" + news[index]['time'] + "]" + news[index]['title']

        data_prov_tree = data['areaTree'][0]['children']
        for area_req in area_requested:
            prov_index = -1
            for i in range(len(data_prov_tree)):
                if data_prov_tree[i]['name'] == area_req:
                    print("\n")
                    output_log("于索引 " + str(i) + " 获取到到 " + area_req + "数据。")
                    prov_index = i
                    break
            
            if i >= 0:
                data_prov = data_prov_tree[prov_index]
                text_prov = text_prov + "\\n🏙" + area_req + "数据:\\n确诊:"
                text_prov = text_prov + str(data_prov['total']['confirm']) + "\\t疑似:" + str(data_prov['total']['suspect']) + "\\n死亡:" + str(data_prov['total']['dead']) + "\\t\\t治愈:" + str(data_prov['total']['heal']) + "\\n新增确诊:" + str(data_prov['today']['confirm']) + "\\n治愈率:" + str(data_prov['total']['healRate']) + "\\t死亡率:" + str(data_prov['total']['deadRate']) + "\\n"
                if not data_prov['today']['isUpdated']:
                    text_prov = text_prov + "注：此城市新增确诊数据未更新。\\n"
                
                for city in data_prov['children']:
                    output_log("找到" + city['name'] + "数据。")
                    text_prov = text_prov + "▪" + city['name'] + "数据:\\n确诊:" + str(city['total']['confirm']) + "\\t\\t疑似:" + str(city['total']['suspect']) + "\\n死亡:" + str(city['total']['dead']) + "\\t\\t治愈:" + str(city['total']['heal']) + "\\n新增确诊:" + str(city['today']['confirm']) + "\\n治愈率:" + str(city['total']['healRate'] + "\\t死亡率:" + str(city['total']['deadRate'])) + "\\n"
                    if not city['today']['isUpdated']:
                        text_prov = text_prov + "注：此城市新增确诊数据未更新。\\n"

        print("\n")
        output_log("数据获取成功，准备推送至IFTTT。")
        IFTTT_push(text_dome, text_prov, False)
    except:
        try:
            IFTTT_push("数据获取失败。", "请拨冗通知服务运营者。", True)
            output_log("数据获取失败！请检查程序！\n")
        except:
            output_log("数据获取失败！请检查网路！\n")
    
    output_log("本轮推送结束。\n\n")

def IFTTT_push(push_text_1, push_text_2, silent_mode):
    today    = datetime.date.today()
    CEE_left = (CEE_date - today).days

    push_val1_text = "2019-nCoV 数据推送\\n推送时间:" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + " GMT+8\\n推送设备:" + host_name + "\\n高考倒计时:" + str(CEE_left) + "天\\n\\n推送内容:"
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
    a = pds.read_csv(path)
    names = a['event_name']
    keys  = a['key']
    urls  = [post_url_p1 + names[i] + post_url_p2 + keys[i] for i in range(len(names))]
    return urls

if __name__ == "__main__":    
    post_urls = read_urls(sub_doc_path)

    IFTTT_push("程序已上线。\\n当前版本:" + cur_version, "推送模式:整点推送。\\n", True)

    output_log("程序已上线。当前版本:" + cur_version)
    output_log("当前设备 Host Name: " + host_name + "\n")

    output_log("开始运行推送服务。推送模式:整点推送。\n")
    get_data()
    scheduler = BlockingScheduler()
    trigger = CronTrigger(hour='*/1')
    scheduler.add_job(get_data,trigger)
    scheduler.start()