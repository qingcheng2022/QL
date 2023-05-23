# 软件：快手极速版
# 功能：签到 开启宝箱
# 抓包 Cookie：以下两条任意一个的 body 里都可以找到
# 抓包 签到的__NS_sig3：开着抓包软件登录，抓 https://nebula.kuaishou.com/rest/n/nebula/sign/sign?__NS_sig3= 这条链接里请求体的__NS_sig3=xxxx部分
# 抓包 开启宝箱的__NS_sig3：开着抓包软件登录，抓 https://nebula.kuaishou.com/rest/n/nebula/box/explore?__NS_sig3= 这条链接里请求体的__NS_sig3=xxxx部分
# 变量格式：export ksjsb='Cookie & __NS_sig3 & 开启宝箱的__NS_sig3'  多个账号用 @ 隔开
# 定时：一天十次
# cron：0 20 2,4,6,8,10,12,14,16,18,20 * * ? 


import os
import time
import requests
# const $ = new Env("快手极速");
# 获取环境变量 Ksjsb 里的内容 并检查 Ksjsb 变量是否存在
variable = os.getenv('Ksjsb')
if not variable:
    print('【快手极速版】: 未填写变量 Ksjsb')
    exit()

# 定义请求头
headers = {
    "Host": "nebula.kuaishou.com",
    "User-Agent": "Mozilla/5.0 (Linux; Android 12; M2012K11AC Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/90.0.4430.226 KsWebView/1.8.90.603 (rel) Mobile Safari/537.36 Yoda/3.1.2-rc1 ksNebula/11.4.10.5532 OS_PRO_BIT/64 MAX_PHY_MEM/11600 AZPREFIX/yz ICFO/0 StatusHT/36 TitleHT/43 NetType/WIFI ISLP/0 ISDM/0 ISLB/0 locale/zh-cn CT/0 ISLM/-1",
    "Cookie": ""
}

Pattitionan = variable.split('@') # 分割
Account = len(Pattitionan) # 账号数量
print(f"找到 {Account} 个账号 \n")
for index, value in enumerate(Pattitionan):
    headers["Cookie"] = value
    sign_in = value.split('&')[1] if '&' in value else ''
    sign_open = value.split('&')[2] if len(value.split('&')) >= 3 else ''

    # 判断账号是否有效
    url = 'https://nebula.kuaishou.com/rest/n/nebula/activity/earn/overview/basicInfo'
    Return = requests.get(url, headers=headers).json()
    if 'result' in Return:
        if Return['result'] == 1:
            print(f'======== ▷ 第 {index + 1} 个账号 ◁ ========')
        else:
            print(f'======== ▷ 第 {index + 1} 个账号 ◁ ========')
            print(f'账号 {index + 1}: Cookie 已经失效了')
            continue
    else:
        print('The script fails')
        break

    # 签到
    print('---------- 签到 ----------')
    if not sign_in:
        print('签到: 未找到 __NS_sig3')
    else:
        url = f'https://nebula.kuaishou.com/rest/n/nebula/sign/sign?__NS_sig3={sign_in}&sigCatVer=1&source=popup'
        Return = requests.get(url, headers=headers).json()
        try:
            if Return.get('result') == 1:
                print(Return['data']['toast'])
            elif Return.get('result') == 10901:
                print('签到: 今天已经签到过了')
            else:
                print(f'签到: {Return.get("error_msg")}')
        except Exception:
            pass

    # 开启宝箱
    print('---------- 宝箱 ----------')
    if not sign_open:
        print('开启宝箱: 未找到 __NS_sig3')
    else:
        url = f'https://nebula.kuaishou.com/rest/n/nebula/box/explore?__NS_sig3={sign_open}&sigCatVer=1&isOpen=true&isReadyOfAdPlay=true'
        Return = requests.get(url, headers=headers).json()
        try:
            if Return.get('result') == 1:
                data = Return.get('data')
                if data.get('commonAwardPopup') != None:
                    print("开启宝箱: " + str(Return['data']['commonAwardPopup']['awardAmount']) + '金币')
                    print('可开启宝箱: ' + str(Return['data']['remainingCount']) + ' 个')
                    print('已开启宝箱: ' + str(Return['data']['openedCount']) + ' 个')
                elif data.get('openTime') == -1:
                    print("开启宝箱: 今日宝箱已达上限")
                else:
                    print('开启宝箱: 请在 ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(Return['data']['treasureBoxOpenTimestamp'] / 1000 )) + ' 开启宝箱')
            else:
                print(f'开启宝箱: {Return.get(error_msg)}')
        except Exception:
            pass

    # 账号信息
    print('-------- 账号信息 --------')
    url = 'https://nebula.kuaishou.com/rest/n/nebula/activity/earn/overview/basicInfo'
    Return = requests.get(url, headers=headers).json()
    try:
        if Return['result'] == 1: 
            print('我的昵称: ' + Return['data']['userData']['nickname'])
            print('我的等级: ' + Return['data']['ugGrowthLevelInfo']['levelName'])
            print('我的余额: ' + str(Return['data']['totalCash']))
            print('我的金币: ' + str(Return['data']['totalCoin']))
        else:
            print('未找到账号信息')
    except Exception:
        pass
