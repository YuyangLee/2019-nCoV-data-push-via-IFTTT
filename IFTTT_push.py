# -*- coding: utf-8 -*-
import json
import requests
import pandas as pds
import socket
import datetime

from enum import Enum
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

cur_version = "1.3.0"

get_Data_URL = "https://view.inews.qq.com/g2/getOnsInfo"
sub_doc_path = r"subscribed_urls.csv"

post_url_p1 = "https://maker.ifttt.com/trigger/"
post_url_p2 = "/with/key/"
host_name   = socket.gethostname()

class data_cate(Enum):
    svol_data = 1
    intl_data = 2
    prov_data = 3

CEE_date = datetime.date(2020, 6, 7)               # 这一字符串是推送地址数据的 csv 文件地址
area_requested = ['宁夏', '湖北']                   # 这一列表包含了你订阅数据的省（自治区、直辖市）
ctry_requested = ['美国', '韩国', '钻石号邮轮']      # 这一列表包含了你订阅数据的国家（中国除外）

def output_log(log_text): print("[", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "] ", log_text)

def json_to_text(mark, json_data):
    text = "\\n" + mark + json_data['name'] + "数据:\\n"
    text = text + "确诊:" + str(json_data['total']['confirm']) + "\\t"
    text = text + "疑似:" + str(json_data['total']['suspect']) + "\\n"
    text = text + "死亡:" + str(json_data['total']['dead']) + "\\t"
    text = text + "治愈:" + str(json_data['total']['heal']) + "\\n"
    text = text + "新增确诊:" + str(json_data['today']['confirm']) + "\\n"
    text = text + "治愈率:" + str(json_data['total']['healRate']) + "%\\t"
    text = text + "死亡率:" + str(json_data['total']['deadRate']) + "%\\n"
    return text

def push_data():
    output_log("开启一轮推送。\n")
    try:
        global post_urls
        post_urls = read_urls(sub_doc_path)
        output_log("读取到" + str(len(post_urls)) + "条订阅地址。\n")
    except:
        output_log("订阅地址获取失败！请检查程序！\n")
    
    output_log("正获取数据自 " + get_Data_URL)

    # https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5
    try:
        res = requests.post(get_Data_URL, {"name": "disease_h5"})
        data = json.loads(json.loads(res.text)['data'])

        # print(data)

        data_dome = data['areaTree'][0]
        text_dome = json_to_text("🇨🇳", data_dome)
        text_prov = ""
        text_intl = ""

        data_intl_tree = data['areaTree']
        data_prov_tree = data_intl_tree[0]['children']

        print("\n")
        for area_req in area_requested:
            prov_index = -1
            for i in range(len(data_prov_tree)):
                if data_prov_tree[i]['name'] == area_req:
                    output_log("于国内数据索引 " + str(i) + " 获取到到 " + area_req + "数据。")
                    prov_index = i
                    break
            
            if prov_index >= 0:
                data_prov = data_prov_tree[prov_index]
                text_prov = text_prov + json_to_text("🏙", data_prov)
                
                for data_city in data_prov['children']:
                    text_prov = text_prov + json_to_text("▪", data_city)
        
        print("\n")
        for ctry_req in ctry_requested:
            ctry_index = -1
            for i in range(1, len(data_intl_tree)):
                if data_intl_tree[i]['name'] == ctry_req:
                    output_log("于国际数据索引 " + str(i) + " 获取到到 " + ctry_req + "数据。")
                    ctry_index = i
                    break
            if ctry_index > 0:
                data_intl = data_intl_tree[ctry_index]
                text_intl = text_intl + json_to_text("🌏", data_intl)

        print("\n")
        output_log("数据获取成功，准备推送至IFTTT。")
        IFTTT_push(text_dome, text_intl, False, data_cate.intl_data)
        IFTTT_push(text_prov, "数据全部推送结束", False, data_cate.prov_data)

    except:
        try:
            IFTTT_push("数据获取失败。", "请拨冗通知服务运营者。", True, data_cate.svol_data)
            output_log("数据获取失败！请检查程序！\n")
        except:
            output_log("数据获取失败！请检查网路！\n")
    
    output_log("本轮推送结束。\n\n")

def IFTTT_push(push_text_1, push_text_2, silent_mode, data_cate):
    today    = datetime.date.today()
    CEE_left = (CEE_date - today).days

    if data_cate == data_cate.svol_data:
        push_val1_text = "CVOID-19 数据推送(服务通知)\\n"
    elif data_cate == data_cate.intl_data:
        push_val1_text = "CVOID-19 数据推送(国际数据)\\n"    
    elif data_cate == data_cate.prov_data:
        push_val1_text = "CVOID-19 数据推送(国内数据)\\n"

    push_val1_text = push_val1_text + "推送时间:" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + " GMT+8\\n推送设备:" + host_name + "\\n高考倒计时:" + str(CEE_left) + "天\\n\\n推送内容:"
    push_val2_text = "\\n" + push_text_1
    push_val3_text = "\\n" + push_text_2 + "\\n"
    body = "{ \"value1\": \"" + push_val1_text + "\", \"value2\": \"" + push_val2_text + "\", \"value3\": \"" + push_val3_text + "\" }"
    headers = { 'Content-Type': 'application/json' }

    try:
        for url in post_urls:
            requests.post(url, data = body.encode('utf-8'), headers = headers)
            if not silent_mode: output_log("已完成对" + str(len(post_urls)) + "个地址的推送。")
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

    IFTTT_push("程序已上线。\\n当前版本:" + cur_version, "推送模式:整点推送。\\n", True, data_cate.svol_data)

    output_log("程序已上线。当前版本:" + cur_version)
    output_log("当前设备 Host Name: " + host_name + "\n")

    output_log("开始运行推送服务。推送模式:整点推送。\n")
    push_data()
    scheduler = BlockingScheduler()
    trigger = CronTrigger(hour='*/1')
    scheduler.add_job(push_data,trigger)
    scheduler.start()