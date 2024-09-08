# !/usr/bin/python3
# -- coding: utf-8 --
"""
打开小程序或APP-我的-积分, 捉以下几种url之一,把整个url放到变量 sfsyUrl 里,多账号换行分割
https://mcs-mimp-web.sf-express.com/mcs-mimp/share/weChat/activityRedirect
https://mcs-mimp-web.sf-express.com/mcs-mimp/share/app/shareRedirect
每天跑一到两次就行
"""
# cron: 11 6,9,12,15,18 * * *
# const $ = new Env("顺丰速运");
import hashlib
import json
import os
import random
import time
import re
from datetime import datetime, timedelta
from sys import exit
import requests
from urllib3.exceptions import InsecureRequestWarning

# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

IS_DEV = False

if os.path.isfile('notify.py'):
    from notify import send

    print("加载通知服务成功！")
else:
    print("加载通知服务失败!")
send_msg = ''
one_msg = ''


def Log(cont=''):
    global send_msg, one_msg
    print(cont)
    if cont:
        one_msg += f'{cont}\n'
        send_msg += f'{cont}\n'


# 1905 #0945 #6332 #6615 2559
inviteId = [
    '8C3950A023D942FD93BE9218F5BFB34B', 'EF94619ED9C84E968C7A88CFB5E0B5DC', '9C92BD3D672D4B6EBB7F4A488D020C79',
    '803CF9D1E0734327BDF67CDAE1442B0E', '00C81F67BE374041A692FA034847F503']


class RUN:
    def __init__(self, info, index):
        global one_msg
        one_msg = ''
        split_info = info.split('@')
        url = split_info[0]
        len_split_info = len(split_info)
        last_info = split_info[len_split_info - 1]
        self.send_UID = None
        if len_split_info > 0 and "UID_" in last_info:
            self.send_UID = last_info
        self.index = index + 1
        Log(f"\n---------开始执行第{self.index}个账号>>>>>")
        self.s = requests.session()
        self.s.verify = False
        self.headers = {
            'Host': 'mcs-mimp-web.sf-express.com',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090b19)XWEB/11253',
            'accept': 'application/json, text/plain, */*',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'zh-CN,zh',
            'platform': 'MINI_PROGRAM',

        }
        self.anniversary_black = False
        self.member_day_black = False
        self.member_day_red_packet_drew_today = False
        self.member_day_red_packet_map = {}
        self.login_res = self.login(url)
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.answer = False
        self.max_level = 8
        self.packet_threshold = 1 << (self.max_level - 1)

    def get_deviceId(self, characters='abcdef0123456789'):
        result = ''
        for char in 'xxxxxxxx-xxxx-xxxx':
            if char == 'x':
                result += random.choice(characters)
            elif char == 'X':
                result += random.choice(characters).upper()
            else:
                result += char
        return result

    def login(self, sfurl):
        ress = self.s.get(sfurl, headers=self.headers)
        # print(ress.text)
        self.user_id = self.s.cookies.get_dict().get('_login_user_id_', '')
        self.phone = self.s.cookies.get_dict().get('_login_mobile_', '')
        self.mobile = self.phone[:3] + "*" * 4 + self.phone[7:]
        if self.phone != '':
            Log(f'用户:【{self.mobile}】登陆成功')
            return True
        else:
            Log(f'获取用户信息失败')
            return False

    def getSign(self):
        timestamp = str(int(round(time.time() * 1000)))
        token = 'wwesldfs29aniversaryvdld29'
        sysCode = 'MCS-MIMP-CORE'
        data = f'token={token}&timestamp={timestamp}&sysCode={sysCode}'
        signature = hashlib.md5(data.encode()).hexdigest()
        data = {
            'sysCode': sysCode,
            'timestamp': timestamp,
            'signature': signature
        }
        self.headers.update(data)
        return data

    def do_request(self, url, data={}, req_type='post'):
        self.getSign()
        try:
            if req_type.lower() == 'get':
                response = self.s.get(url, headers=self.headers)
            elif req_type.lower() == 'post':
                response = self.s.post(url, headers=self.headers, json=data)
            else:
                raise ValueError('Invalid req_type: %s' % req_type)
            res = response.json()
            return res
        except requests.exceptions.RequestException as e:
            print('Request failed:', e)
            return None
        except json.JSONDecodeError as e:
            print('JSON decoding failed:', e)
            return None

    def sign(self):
        print(f'>>>>>>开始执行签到')
        json_data = {"comeFrom": "vioin", "channelFrom": "WEIXIN"}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskSignPlusService~automaticSignFetchPackage'
        response = self.do_request(url, data=json_data)
        # print(response)
        if response.get('success') == True:
            count_day = response.get('obj', {}).get('countDay', 0)
            if response.get('obj') and response['obj'].get('integralTaskSignPackageVOList'):
                packet_name = response["obj"]["integralTaskSignPackageVOList"][0]["packetName"]
                Log(f'>>>签到成功，获得【{packet_name}】，本周累计签到【{count_day + 1}】天')
            else:
                Log(f'今日已签到，本周累计签到【{count_day + 1}】天')
        else:
            print(f'签到失败！原因：{response.get("errorMessage")}')

    def superWelfare_receiveRedPacket(self):
        print(f'>>>>>>超值福利签到')
        json_data = {
            'channel': 'czflqdlhbxcx'
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberActLengthy~redPacketActivityService~superWelfare~receiveRedPacket'
        response = self.do_request(url, data=json_data)
        # print(response)
        if response.get('success') == True:
            gift_list = response.get('obj', {}).get('giftList', [])
            if response.get('obj', {}).get('extraGiftList', []):
                gift_list.extend(response['obj']['extraGiftList'])
            gift_names = ', '.join([gift['giftName'] for gift in gift_list])
            receive_status = response.get('obj', {}).get('receiveStatus')
            status_message = '领取成功' if receive_status == 1 else '已领取过'
            Log(f'超值福利签到[{status_message}]: {gift_names}')
        else:
            error_message = response.get('errorMessage') or json.dumps(response) or '无返回'
            print(f'超值福利签到失败: {error_message}')

    def get_SignTaskList(self, END=False):
        if not END: print(f'>>>开始获取签到任务列表')
        json_data = {
            'channelType': '3',
            'deviceId': self.get_deviceId(),
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskStrategyService~queryPointTaskAndSignFromES'
        response = self.do_request(url, data=json_data)
        # print(response)
        if response.get('success') == True and response.get('obj') != []:
            totalPoint = response["obj"]["totalPoint"]
            if END:
                Log(f'当前积分：【{totalPoint}】')
                return
            Log(f'执行前积分：【{totalPoint}】')
            for task in response["obj"]["taskTitleLevels"]:
                self.taskId = task["taskId"]
                self.taskCode = task["taskCode"]
                self.strategyId = task["strategyId"]
                self.title = task["title"]
                status = task["status"]
                skip_title = ['用行业模板寄件下单', '去新增一个收件偏好', '参与积分活动']
                if status == 3:
                    print(f'>{self.title}-已完成')
                    continue
                if self.title in skip_title:
                    print(f'>{self.title}-跳过')
                    continue
                else:
                    # print("taskId:", taskId)
                    # print("taskCode:", taskCode)
                    # print("----------------------")
                    self.doTask()
                    time.sleep(3)
                self.receiveTask()

    def doTask(self):
        print(f'>>>开始去完成【{self.title}】任务')
        json_data = {
            'taskCode': self.taskCode,
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonRoutePost/memberEs/taskRecord/finishTask'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            print(f'>【{self.title}】任务-已完成')
        else:
            print(f'>【{self.title}】任务-{response.get("errorMessage")}')

    def receiveTask(self):
        print(f'>>>开始领取【{self.title}】任务奖励')
        json_data = {
            "strategyId": self.strategyId,
            "taskId": self.taskId,
            "taskCode": self.taskCode,
            "deviceId": self.get_deviceId()
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskStrategyService~fetchIntegral'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            print(f'>【{self.title}】任务奖励领取成功！')
        else:
            print(f'>【{self.title}】任务-{response.get("errorMessage")}')

    def do_honeyTask(self):
        # 做任务
        json_data = {"taskCode": self.taskCode}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberEs~taskRecord~finishTask'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            print(f'>【{self.taskType}】任务-已完成')
        else:
            print(f'>【{self.taskType}】任务-{response.get("errorMessage")}')


    def get_coupom(self):
        print('>>>执行领取生活权益领券任务')
        # 领取生活权益领券
        # https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberGoods~pointMallService~createOrder

        json_data = {
            "from": "Point_Mall",
            "orderSource": "POINT_MALL_EXCHANGE",
            "goodsNo": self.goodsNo,
            "quantity": 1,
            "taskCode": self.taskCode
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberGoods~pointMallService~createOrder'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            print(f'>领券成功！')
        else:
            print(f'>领券失败！原因：{response.get("errorMessage")}')

    def get_coupom_list(self):
        print('>>>获取生活权益券列表')
        # 领取生活权益领券
        # https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberGoods~pointMallService~createOrder

        json_data = {
            "memGrade": 1,
            "categoryCode": "SHTQ",
            "showCode": "SHTQWNTJ"
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberGoods~mallGoodsLifeService~list'
        response = self.do_request(url, data=json_data)
        # print(response)
        if response.get('success') == True:
            goodsList = response["obj"][0]["goodsList"]
            for goods in goodsList:
                exchangeTimesLimit = goods['exchangeTimesLimit']
                if exchangeTimesLimit >= 7:
                    self.goodsNo = goods['goodsNo']
                    print(f'当前选择券号：{self.goodsNo}')
                    self.get_coupom()
                    break
        else:
            print(f'>领券失败！原因：{response.get("errorMessage")}')



    def addDeliverPrefer(self):
        print(f'>>>开始【{self.title}】任务')
        json_data = {
            "country": "中国",
            "countryCode": "A000086000",
            "province": "北京市",
            "provinceCode": "A110000000",
            "city": "北京市",
            "cityCode": "A111000000",
            "county": "东城区",
            "countyCode": "A110101000",
            "address": "1号楼1单元101",
            "latitude": "",
            "longitude": "",
            "memberId": "",
            "locationCode": "010",
            "zoneCode": "CN",
            "postCode": "",
            "takeWay": "7",
            "callBeforeDelivery": 'false',
            "deliverTag": "2,3,4,1",
            "deliverTagContent": "",
            "startDeliverTime": "",
            "selectCollection": 'false',
            "serviceName": "",
            "serviceCode": "",
            "serviceType": "",
            "serviceAddress": "",
            "serviceDistance": "",
            "serviceTime": "",
            "serviceTelephone": "",
            "channelCode": "RW11111",
            "taskId": self.taskId,
            "extJson": "{\"noDeliverDetail\":[]}"
        }
        url = 'https://ucmp.sf-express.com/cx-wechat-member/member/deliveryPreference/addDeliverPrefer'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            print('新增一个收件偏好，成功')
        else:
            print(f'>【{self.title}】任务-{response.get("errorMessage")}')

    

    def member_day_index(self):
        print('====== 会员日活动 ======')
        try:
            invite_user_id = random.choice([invite for invite in inviteId if invite != self.user_id])
            payload = {'inviteUserId': invite_user_id}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayIndexService~index'

            response = self.do_request(url, data=payload)
            if response.get('success'):
                lottery_num = response.get('obj', {}).get('lotteryNum', 0)
                can_receive_invite_award = response.get('obj', {}).get('canReceiveInviteAward', False)
                if can_receive_invite_award:
                    self.member_day_receive_invite_award(invite_user_id)
                self.member_day_red_packet_status()
                Log(f'会员日可以抽奖{lottery_num}次')
                for _ in range(lottery_num):
                    self.member_day_lottery()
                if self.member_day_black:
                    return
                self.member_day_task_list()
                if self.member_day_black:
                    return
                self.member_day_red_packet_status()
            else:
                error_message = response.get('errorMessage', '无返回')
                Log(f'查询会员日失败: {error_message}')
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_receive_invite_award(self, invite_user_id):
        try:
            payload = {'inviteUserId': invite_user_id}

            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayIndexService~receiveInviteAward'

            response = self.do_request(url, payload)
            if response.get('success'):
                product_name = response.get('obj', {}).get('productName', '空气')
                Log(f'会员日奖励: {product_name}')
            else:
                error_message = response.get('errorMessage', '无返回')
                Log(f'领取会员日奖励失败: {error_message}')
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_lottery(self):
        try:
            payload = {}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayLotteryService~lottery'

            response = self.do_request(url, payload)
            if response.get('success'):
                product_name = response.get('obj', {}).get('productName', '空气')
                Log(f'会员日抽奖: {product_name}')
            else:
                error_message = response.get('errorMessage', '无返回')
                Log(f'会员日抽奖失败: {error_message}')
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_task_list(self):
        try:
            payload = {'activityCode': 'MEMBER_DAY', 'channelType': 'MINI_PROGRAM'}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~taskList'

            response = self.do_request(url, payload)
            if response.get('success'):
                task_list = response.get('obj', [])
                for task in task_list:
                    if task['status'] == 1:
                        if self.member_day_black:
                            return
                        self.member_day_fetch_mix_task_reward(task)
                for task in task_list:
                    if task['status'] == 2:
                        if self.member_day_black:
                            return
                        if task['taskType'] in ['SEND_SUCCESS', 'INVITEFRIENDS_PARTAKE_ACTIVITY', 'OPEN_SVIP',
                                                'OPEN_NEW_EXPRESS_CARD', 'OPEN_FAMILY_CARD', 'CHARGE_NEW_EXPRESS_CARD',
                                                'INTEGRAL_EXCHANGE']:
                            pass
                        else:
                            for _ in range(task['restFinishTime']):
                                if self.member_day_black:
                                    return
                                self.member_day_finish_task(task)
            else:
                error_message = response.get('errorMessage', '无返回')
                Log('查询会员日任务失败: ' + error_message)
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_finish_task(self, task):
        try:
            payload = {'taskCode': task['taskCode']}

            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberEs~taskRecord~finishTask'

            response = self.do_request(url, payload)
            if response.get('success'):
                Log('完成会员日任务[' + task['taskName'] + ']成功')
                self.member_day_fetch_mix_task_reward(task)
            else:
                error_message = response.get('errorMessage', '无返回')
                Log('完成会员日任务[' + task['taskName'] + ']失败: ' + error_message)
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_fetch_mix_task_reward(self, task):
        try:
            payload = {'taskType': task['taskType'], 'activityCode': 'MEMBER_DAY', 'channelType': 'MINI_PROGRAM'}

            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~fetchMixTaskReward'

            response = self.do_request(url, payload)
            if response.get('success'):
                Log('领取会员日任务[' + task['taskName'] + ']奖励成功')
            else:
                error_message = response.get('errorMessage', '无返回')
                Log('领取会员日任务[' + task['taskName'] + ']奖励失败: ' + error_message)
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_receive_red_packet(self, hour):
        try:
            payload = {'receiveHour': hour}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayTaskService~receiveRedPacket'

            response = self.do_request(url, payload)
            if response.get('success'):
                print(f'会员日领取{hour}点红包成功')
            else:
                error_message = response.get('errorMessage', '无返回')
                print(f'会员日领取{hour}点红包失败: {error_message}')
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_red_packet_status(self):
        try:
            payload = {}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayPacketService~redPacketStatus'
            response = self.do_request(url, payload)
            if response.get('success'):
                packet_list = response.get('obj', {}).get('packetList', [])
                for packet in packet_list:
                    self.member_day_red_packet_map[packet['level']] = packet['count']

                for level in range(1, self.max_level):
                    count = self.member_day_red_packet_map.get(level, 0)
                    while count >= 2:
                        self.member_day_red_packet_merge(level)
                        count -= 2
                packet_summary = []
                remaining_needed = 0

                for level, count in self.member_day_red_packet_map.items():
                    if count == 0:
                        continue
                    packet_summary.append(f"[{level}级]X{count}")
                    int_level = int(level)
                    if int_level < self.max_level:
                        remaining_needed += 1 << (int_level - 1)

                Log("会员日合成列表: " + ", ".join(packet_summary))

                if self.member_day_red_packet_map.get(self.max_level):
                    Log(f"会员日已拥有[{self.max_level}级]红包X{self.member_day_red_packet_map[self.max_level]}")
                    self.member_day_red_packet_draw(self.max_level)
                else:
                    remaining = self.packet_threshold - remaining_needed
                    Log(f"会员日距离[{self.max_level}级]红包还差: [1级]红包X{remaining}")

            else:
                error_message = response.get('errorMessage', '无返回')
                Log(f'查询会员日合成失败: {error_message}')
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_red_packet_merge(self, level):
        try:
            # for key,level in enumerate(self.member_day_red_packet_map):
            #     pass
            payload = {'level': level, 'num': 2}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayPacketService~redPacketMerge'

            response = self.do_request(url, payload)
            if response.get('success'):
                Log(f'会员日合成: [{level}级]红包X2 -> [{level + 1}级]红包')
                self.member_day_red_packet_map[level] -= 2
                if not self.member_day_red_packet_map.get(level + 1):
                    self.member_day_red_packet_map[level + 1] = 0
                self.member_day_red_packet_map[level + 1] += 1
            else:
                error_message = response.get('errorMessage', '无返回')
                Log(f'会员日合成两个[{level}级]红包失败: {error_message}')
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_red_packet_draw(self, level):
        try:
            payload = {'level': str(level)}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayPacketService~redPacketDraw'
            response = self.do_request(url, payload)
            if response and response.get('success'):
                coupon_names = [item['couponName'] for item in response.get('obj', [])] or []

                Log(f"会员日提取[{level}级]红包: {', '.join(coupon_names) or '空气'}")
            else:
                error_message = response.get('errorMessage') if response else "无返回"
                Log(f"会员日提取[{level}级]红包失败: {error_message}")
                if "没有资格参与活动" in error_message:
                    self.memberDay_black = True
                    print("会员日任务风控")
        except Exception as e:
            print(e)

    def Autumn_2024_index(self):
        print('====== 查询中秋活动状态 ======')
        invite_user_id = random.choice([invite for invite in inviteId if invite != self.user_id])
        try:
            self.headers['channel'] = 'newExpressWX'
            self.headers[
                'referer'] = f'https://mcs-mimp-web.sf-express.com/origin/a/mimp-activity/midAutumn2024?mobile={self.mobile}&userId={self.user_id}&path=/origin/a/mimp-activity/midAutumn2024&supportShare=&inviteUserId={invite_user_id}&from=24zqxcx'
            payload = {}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonNoLoginPost/~memberNonactivity~midAutumn2024IndexService~index'

            response = self.do_request(url, payload)
            # print(response)
            if response.get('success'):
                obj = response.get('obj', [{}])
                acEndTime = obj.get('acEndTime', '')
                # 获取当前时间并格式化
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                comparison_time = datetime.strptime(acEndTime, "%Y-%m-%d %H:%M:%S")
                # 比较当前时间是否小于比较时间
                is_less_than = datetime.now() < comparison_time
                if is_less_than:
                    print('中秋活动进行中....')
                    return True
                else:
                    print('中秋活动已结束')
                    return False
            else:
                error_message = response.get('errorMessage', '无返回')
                if '没有资格参与活动' in error_message:
                    self.Autumn_2024_black = True
                    Log('会员日任务风控')
                return False
        except Exception as e:
            print(e)
            return False

    def Autumn_2024_Game_indexInfo(self):
        Log('====== 开始中秋游戏 ======')
        try:
            payload = {}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2024GameService~indexInfo'

            response = self.do_request(url, payload)
            # print(response)
            if response.get('success'):
                obj = response.get('obj', [{}])
                maxPassLevel = obj.get('maxPassLevel', '')
                ifPassAllLevel = obj.get('ifPassAllLevel', '')
                if maxPassLevel != 30:
                    self.Autumn_2024_win(maxPassLevel)
                else:
                    self.Autumn_2024_win(0)

            else:
                error_message = response.get('errorMessage', '无返回')
                if '没有资格参与活动' in error_message:
                    self.Autumn_2024_black = True
                    Log('会员日任务风控')
                return False
        except Exception as e:
            print(e)
            return False

    def Autumn_2024_Game_init(self):
        Log('====== 开始中秋活动游戏 ======')
        try:
            payload = {}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2024GameService~init'

            response = self.do_request(url, payload)
            # print(response)
            if response.get('success'):
                obj = response.get('obj', [{}])
                currentIndex = obj.get('currentIndex', '')
                ifPassAllLevel = obj.get('ifPassAllLevel', '')
                if currentIndex != 30:
                    self.Autumn_2024_win(currentIndex)
                else:
                    self.Autumn_2024_win(0)

            else:
                error_message = response.get('errorMessage', '无返回')
                if '没有资格参与活动' in error_message:
                    self.Autumn_2024_black = True
                    Log('会员日任务风控')
                return False
        except Exception as e:
            print(e)
            return False

    def Autumn_2024_weeklyGiftStatus(self):
        print('====== 查询每周礼包领取状态 ======')
        try:
            payload = {}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2024IndexService~weeklyGiftStatus'

            response = self.do_request(url, payload)
            # print(response)
            if response.get('success'):
                obj = response.get('obj', [{}])
                for gift in obj:
                    received = gift['received']
                    receiveStartTime = gift['receiveStartTime']
                    receiveEndTime = gift['receiveEndTime']
                    print(f'>>> 领取时间：【{receiveStartTime} 至 {receiveEndTime}】')
                    if received:
                        print('> 该礼包已领取')
                        continue
                    receive_start_time = datetime.strptime(receiveStartTime, "%Y-%m-%d %H:%M:%S")
                    receive_end_time = datetime.strptime(receiveEndTime, "%Y-%m-%d %H:%M:%S")
                    is_within_range = receive_start_time <= datetime.now() <= receive_end_time
                    if is_within_range:
                        print(f'>> 开始领取礼包：')
                        self.Autumn_2024_receiveWeeklyGift()
            else:
                error_message = response.get('errorMessage', '无返回')
                if '没有资格参与活动' in error_message:
                    self.Autumn_2024_black = True
                    Log('会员日任务风控')
        except Exception as e:
            print(e)

    def Autumn_2024_receiveWeeklyGift(self):
        invite_user_id = random.choice([invite for invite in inviteId if invite != self.user_id])
        try:
            payload = {"inviteUserId": invite_user_id}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2024IndexService~receiveWeeklyGift'

            response = self.do_request(url, payload)
            # print(response)
            if response.get('success'):
                obj = response.get('obj', [{}])
                if obj == [{}]:
                    print('> 领取失败')
                    return False
                for gifts in obj:
                    productName = gifts['productName']
                    amount = gifts['amount']
                    print(f'> 领取【{productName} x {amount}】成功')
            else:
                error_message = response.get('errorMessage', '无返回')
                if '没有资格参与活动' in error_message:
                    self.Autumn_2024_black = True
                    Log('会员日任务风控')
        except Exception as e:
            print(e)

    def Autumn_2024_taskList(self):
        print('====== 查询推币任务列表 ======')
        try:
            payload = {
                "activityCode": "MIDAUTUMN_2024",
                "channelType": "MINI_PROGRAM"
            }
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~taskList'

            response = self.do_request(url, payload)
            # print(response)
            if response.get('success'):
                obj = response.get('obj', [{}])
                for task in obj:
                    taskType = task['taskType']
                    self.taskName = task['taskName']
                    status = task['status']
                    if status == 3:
                        Log(f'> 任务【{self.taskName}】已完成')
                        continue
                    self.taskCode = task.get('taskCode', None)
                    if self.taskCode:
                        self.Autumn_2024_finishTask()
                    if taskType == 'PLAY_ACTIVITY_GAME':
                        self.Autumn_2024_Game_init()
            else:
                error_message = response.get('errorMessage', '无返回')
                if '没有资格参与活动' in error_message:
                    self.Autumn_2024_black = True
                    Log('会员日任务风控')
        except Exception as e:
            print(e)

    def Autumn_2024_coinStatus(self, END=False):
        Log('====== 查询月饼信息 ======')
        # try:
        payload = {}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2024CoinService~coinStatus'

        response = self.do_request(url, payload)
        # print(response)
        if response.get('success'):
            obj = response.get('obj', None)
            if obj == None: return False
            accountCurrencyList = obj.get('accountCurrencyList', [])
            pushedTimesToday = obj.get('pushedTimesToday', '')
            pushedTimesTotal = obj.get('pushedTimesTotal', '')
            PUSH_TIMES_balance = 0
            self.COIN_balance = 0
            WELFARE_CARD_balance = 0
            for li in accountCurrencyList:
                if li['currency'] == 'PUSH_TIMES':
                    PUSH_TIMES_balance = li['balance']
                if li['currency'] == 'COIN':
                    self.COIN_balance = li['balance']
                if li['currency'] == 'WELFARE_CARD':
                    WELFARE_CARD_balance = li['balance']

            PUSH_TIMES = PUSH_TIMES_balance
            if END:
                if PUSH_TIMES_balance > 0:
                    for i in range(PUSH_TIMES_balance):
                        print(f'>> 开始第【{PUSH_TIMES_balance + 1}】次推币')
                        self.Autumn_2024_pushCoin()
                        PUSH_TIMES -= 1
                        pushedTimesToday += 1
                        pushedTimesTotal += 1
                Log(f'> 剩余推币次数：【{PUSH_TIMES}】')
                Log(f'> 当前月饼：【{self.COIN_balance}】')
                # Log(f'> 当前发财卡：【{WELFARE_CARD_balance}】')
                Log(f'> 今日推币：【{pushedTimesToday}】次')
                Log(f'> 总推币：【{pushedTimesTotal}】次')
            else:
                print(f'> 剩余推币次数：【{PUSH_TIMES_balance}】')
                print(f'> 当前月饼：【{self.COIN_balance}】')
                # Log(f'> 当前发财卡：【{WELFARE_CARD_balance}】')
                print(f'> 今日推币：【{pushedTimesToday}】次')
                print(f'> 总推币：【{pushedTimesTotal}】次')

            self.Autumn_2024_givePushTimes()
        else:
            error_message = response.get('errorMessage', '无返回')
            if '没有资格参与活动' in error_message:
                self.Autumn_2024_black = True
                Log('会员日任务风控')
        # except Exception as e:
        #     print(e)

    def Autumn_2024_pushCoin(self):
        try:
            payload = {"plateToken": None}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2024CoinService~pushCoin'

            response = self.do_request(url, payload)
            # print(response)
            if response.get('success'):
                obj = response.get('obj', [{}])
                drawAward = obj.get('drawAward', '')
                self.COIN_balance += drawAward
                print(f'> 获得：【{drawAward}】月饼')

            else:
                error_message = response.get('errorMessage', '无返回')
                if '没有资格参与活动' in error_message:
                    self.Autumn_2024_black = True
                    Log('会员日任务风控')
        except Exception as e:
            print(e)

    def Autumn_2024_givePushTimes(self):
        Log('====== 领取赠送推币次数 ======')
        try:
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2024CoinService~givePushTimes'

            response = self.do_request(url)
            # print(response)
            if response.get('success'):
                obj = response.get('obj', 0)
                print(f'> 获得：【{obj}】次推币机会')
            else:
                error_message = response.get('errorMessage', '无返回')
                if '没有资格参与活动' in error_message:
                    self.Autumn_2024_black = True
                    Log('> 会员日任务风控')
                print(error_message)
        except Exception as e:
            print(e)

    def Autumn_2024_finishTask(self):
        try:
            payload = {
                "taskCode": self.taskCode
            }
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberEs~taskRecord~finishTask'

            response = self.do_request(url, payload)
            # print(response)
            if response.get('success'):
                obj = response.get('obj', False)
                Log(f'> 完成任务【{self.taskName}】成功')
            else:
                error_message = response.get('errorMessage', '无返回')
                if '没有资格参与活动' in error_message:
                    self.Autumn_2024_black = True
                    Log('会员日任务风控')
        except Exception as e:
            print(e)

    def Autumn_2024_win(self, level):
        try:
            for i in range(level, 31):
                print(f'开始第【{i}】关')
                payload = {"levelIndex": i}
                url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2024GameService~win'

                response = self.do_request(url, payload)
                # print(response)
                if response.get('success'):
                    obj = response.get('obj', [{}])
                    currentAwardList = obj.get('currentAwardList', [])
                    if currentAwardList != []:
                        for award in currentAwardList:
                            currency = award.get('currency', '')
                            amount = award.get('amount', '')
                            print(f'> 获得：【{currency}】x{amount}')
                    else:
                        print(f'> 本关无奖励')
                    # random_time =random.randint(10,15)
                    # print(f'>> 等待{random_time}秒 <<')
                    # time.sleep(random_time)
                else:
                    error_message = response.get('errorMessage', '无返回')
                    print(error_message)
                    if '没有资格参与活动' in error_message:
                        self.Autumn_2024_black = True
                        Log('会员日任务风控')
        except Exception as e:
            print(e)

    def main(self):
        global one_msg
        wait_time = random.randint(1000, 3000) / 1000.0  # 转换为秒
        time.sleep(wait_time)  # 等待
        one_msg = ''
        if not self.login_res: return False
        # 执行签到任务
        self.sign()
        self.superWelfare_receiveRedPacket()
        self.get_SignTaskList()
        self.get_SignTaskList(True)

        current_date = datetime.now().day
        if 26 <= current_date <= 28:
            self.member_day_index()

        else:
            print('未到指定时间不执行会员日任务')

        if self.Autumn_2024_index():
            self.Autumn_2024_weeklyGiftStatus()
            self.Autumn_2024_coinStatus()
            self.Autumn_2024_taskList()
            self.Autumn_2024_Game_init()
            self.Autumn_2024_coinStatus(True)
        return True


def get_quarter_end_date():
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year

    # 计算下个季度的第一天
    next_quarter_first_day = datetime(current_year, ((current_month - 1) // 3 + 1) * 3 + 1, 1)

    # 计算当前季度的最后一天
    quarter_end_date = next_quarter_first_day - timedelta(days=1)

    return quarter_end_date.strftime("%Y-%m-%d")


def is_activity_end_date(end_date):
    current_date = datetime.now().date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    return current_date == end_date





if __name__ == '__main__':
    APP_NAME = '顺丰速运'
    ENV_NAME = 'SFSY'
    CK_NAME = 'url'
    print(f'''
✨✨✨ {APP_NAME}脚本✨✨✨
✨ 功能：
      积分签到
      签到任务
      中秋任务
✨ 抓包步骤：
      打开{APP_NAME}APP或小程序
      点击我的
      打开抓包工具
      点击“积分”，以下几种url之一：
        https://mcs-mimp-web.sf-express.com/mcs-mimp/share/weChat/activityRedirect
        https://mcs-mimp-web.sf-express.com/mcs-mimp/share/app/shareRedirect
    多账号#、@、换行分割 
✨ 设置青龙变量：
export {ENV_NAME}='url'多账号#分割

✨✨✨ ✨✨✨
    ''')

    #分割变量
    if ENV_NAME in os.environ:
        tokens = re.split("@|#|\n",os.environ.get(ENV_NAME))
    elif "sfsyUrl" in os.environ:
        print("调用变量")
        tokens = re.split("@|#|\n",os.environ.get("sfsyUrl"))
    else:
        tokens =['']
        print(f'无{ENV_NAME}变量')
    #     #exit()
    #tokens =['']
    local_version = '2024.09.03'
   
    # print(tokens)
    if len(tokens) > 0:
        print(f"\n>>>>>>>>>>共获取到{len(tokens)}个账号<<<<<<<<<<")
        for index, infos in enumerate(tokens):
            run_result = RUN(infos, index).main()
            if not run_result: continue
