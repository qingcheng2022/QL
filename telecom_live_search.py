#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# const $ = new Env('电信营业厅直播抽奖查询');
# -------------------------------
"""
1. 脚本仅供学习交流使用, 请在下载后24h内删除
2. 环境变量说明:
    TELECOM_LOTTERY 手机号码@密码 (密码中间以@分隔，多账号用&链接) 如：export TELECOM_LOTTERY ="189********@123456&199********@123456"
3. 必须登录过 电信营业厅 app的账号才能正常运行
"""
"""
update:
    2022.11.29 增加多账号变量 
    2022.12.01 自动加载直播端口
    2023.03.09 修复直播列表查询 by David
"""
from re import findall
from random import randint
from base64 import b64encode
from time import mktime, strptime, strftime, sleep as time_sleep
from requests import post, get, packages
packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ":HIGH:!DH:!aNULL"
from datetime import datetime, timedelta
from asyncio import wait, sleep, run

import time
import threading

from tools.tool import timestamp, get_environ, print_now
from tools.send_msg import push
from telecom import ChinaTelecom
from sendNotify import send

class TelecomLotter:
    def __init__(self, phone, password):
        self.phone = phone
        chinaTelecom = ChinaTelecom(phone, password)
        chinaTelecom.init()
        chinaTelecom.author()
        self.authorization = chinaTelecom.authorization
        self.ua = chinaTelecom.ua
        self.token = chinaTelecom.token

all_list = []
messages = []
def get_urls():
    urls = []
    for i in range(1, 36):
        if i < 10:
            code_str = '0' + str(i)
        else:
            code_str = str(i)
        url = f'https://xbk.189.cn/xbkapi/lteration/index/recommend/anchorRecommend?provinceCode={code_str}'
        urls.append(url)
    return urls

def get_data(url_):
    ulrArray = url_.split("@")
    url = ulrArray[0]
    author = ulrArray[1]
    random_phone = f"1537266{randint(1000, 9999)}"
    headers = {
        "referer": "https://xbk.189.cn/xbk/newHome?version=9.4.0&yjz=no&l=card&longitude=%24longitude%24&latitude=%24latitude%24&utm_ch=hg_app&utm_sch=hg_sh_shdbcdl&utm_as=xbk_tj&loginType=1",
        "user-agent": f"CtClient;9.6.1;Android;12;SM-G9860;{b64encode(random_phone[5:11].encode()).decode().strip('=+')}!#!{b64encode(random_phone[0:5].encode()).decode().strip('=+')}",
        "authorization": author
    }
    data = get(url, headers=headers).json()
    body = data["data"]
    for i in body:
        if time.strftime('%Y-%m-%d') in i['start_time']:
            if i not in all_list:
                name = i['nickname']
                start_time = i['start_time'].replace(time.strftime('%Y-%m-%d'), '')
                print(f' {start_time} 房间：{name}')
                all_list.append(i)
                messages.append(f' {start_time} 房间：{name}')

def main(phone, password):
    tel = TelecomLotter(phone, password);
    urls = get_urls()
    print('加载今日数据ing...')
    threads = []
    for url in urls:
        url = url + '@' + tel.authorization
        threads.append(
            threading.Thread(target=get_data, args=(url,))
        )

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    list_d = {}
    f = 1
    for i in all_list:
        list_d['liveRoom' + str(f)] = i
        f += 1
    print('数据加载完毕')
    send("星播客直播间：", messages)

if __name__ == '__main__':
    param = get_environ("TELECOM_LOTTERY")
    if param == "" :
        print("未填写相应变量 退出")
        exit(0)  
    for x in param.split('&') :
        tmp = x.split('@')
        if len(tmp) < 2 :
            continue
        print("===================手机号:"+ tmp[0]+"===================")
        main(tmp[0], tmp[1])