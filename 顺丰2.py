#2025/1/6 遍历生活特权所有分组的券进行领券，券没啥用但完成可领取30点丰蜜目前一天拉满155点
#变量名：sfsyUrl
#格式：多账号用&分割或创建多个变量sfsyUrl
#关于参数获取如下两种方式：
#❶顺丰APP绑定微信后，添加机器人发送：顺丰
#或者
#❷打开小程序或APP-我的-积分, 手动抓包以下几种URL之一
#https://mcs-mimp-web.sf-express.com/mcs-mimp/share/weChat/shareGiftReceiveRedirect
#https://mcs-mimp-web.sf-express.com/mcs-mimp/share/app/shareRedirect

# const $ = new Env('顺丰速运')
# cron: 31 6,9,12,15,18 * * *
import hashlib
import json
import os
import random
import time
from datetime import datetime, timedelta
from sys import exit
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from urllib.parse import unquote

# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

IS_DEV = False
if os.path.isfile('DEV_ENV.py'):
    import DEV_ENV

    IS_DEV = True


#from notify import send

send_msg = ''
one_msg = ''


def Log(cont=''):
    global send_msg, one_msg
    print(cont)
    if cont:
        one_msg += f'{cont}\n'
        send_msg += f'{cont}\n'


inviteId = ['']


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
        print(f"\n{'='*20} 🔄 开始执行第{self.index}个账号 🔄 {'='*20}")
        self.s = requests.session()
        self.s.verify = False
        self.headers = {
            'Host': 'mcs-mimp-web.sf-express.com',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090551) XWEB/6945 Flue',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
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
        self.all_logs = []  # 初始化all_logs属性
        self.today = datetime.now().strftime('%Y-%m-%d')
        # self.answer = APP_INFO.get('ANSWER', []).get(self.today, False)
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
        try:
            decoded_url = unquote(sfurl)
            ress = self.s.get(decoded_url, headers=self.headers)
            self.user_id = self.s.cookies.get_dict().get('_login_user_id_', '')
            self.phone = self.s.cookies.get_dict().get('_login_mobile_', '')
            self.mobile = self.phone[:3] + "*" * 4 + self.phone[7:] if self.phone else ''
            
            if self.phone:
                Log(f'👤 用户:【{self.mobile}】登陆成功')
                return True
            else:
                Log(f'❌ 获取用户信息失败')
                return False
        except Exception as e:
            Log(f'❌ 登录异常: {str(e)}')
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
        print(f'🎯 开始执行签到')
        json_data = {"comeFrom": "vioin", "channelFrom": "WEIXIN"}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskSignPlusService~automaticSignFetchPackage'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            count_day = response.get('obj', {}).get('countDay', 0)
            if response.get('obj') and response['obj'].get('integralTaskSignPackageVOList'):
                packet_name = response["obj"]["integralTaskSignPackageVOList"][0]["packetName"]
                Log(f'✨ 签到成功，获得【{packet_name}】，本周累计签到【{count_day + 1}】天')
            else:
                Log(f'📝 今日已签到，本周累计签到【{count_day + 1}】天')
        else:
            print(f'❌ 签到失败！原因：{response.get("errorMessage")}')

    def superWelfare_receiveRedPacket(self):
        print(f'🎁 超值福利签到')
        json_data = {
            'channel': 'czflqdlhbxcx'
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberActLengthy~redPacketActivityService~superWelfare~receiveRedPacket'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            gift_list = response.get('obj', {}).get('giftList', [])
            if response.get('obj', {}).get('extraGiftList', []):
                gift_list.extend(response['obj']['extraGiftList'])
            gift_names = ', '.join([gift['giftName'] for gift in gift_list])
            receive_status = response.get('obj', {}).get('receiveStatus')
            status_message = '领取成功' if receive_status == 1 else '已领取过'
            Log(f'🎉 超值福利签到[{status_message}]: {gift_names}')
        else:
            error_message = response.get('errorMessage') or json.dumps(response) or '无返回'
            print(f'❌ 超值福利签到失败: {error_message}')

    def get_SignTaskList(self, END=False):
        if not END: print(f'🎯 开始获取签到任务列表')
        json_data = {
            'channelType': '1',
            'deviceId': self.get_deviceId(),
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskStrategyService~queryPointTaskAndSignFromES'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True and response.get('obj') != []:
            totalPoint = response["obj"]["totalPoint"]
            if END:
                Log(f'💰 当前积分：【{totalPoint}】')
                return
            Log(f'💰 执行前积分：【{totalPoint}】')
            for task in response["obj"]["taskTitleLevels"]:
                self.taskId = task["taskId"]
                self.taskCode = task["taskCode"]
                self.strategyId = task["strategyId"]
                self.title = task["title"]
                status = task["status"]
                skip_title = ['用行业模板寄件下单', '去新增一个收件偏好', '参与积分活动']
                if status == 3:
                    print(f'✨ {self.title}-已完成')
                    continue
                if self.title in skip_title:
                    print(f'⏭️ {self.title}-跳过')
                    continue
                else:
                    # print("taskId:", taskId)
                    # print("taskCode:", taskCode)
                    # print("----------------------")
                    self.doTask()
                    time.sleep(3)
                self.receiveTask()

    def doTask(self):
        print(f'🎯 开始去完成【{self.title}】任务')
        json_data = {
            'taskCode': self.taskCode,
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonRoutePost/memberEs/taskRecord/finishTask'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            print(f'✨ 【{self.title}】任务-已完成')
        else:
            print(f'❌ 【{self.title}】任务-{response.get("errorMessage")}')

    def receiveTask(self):
        print(f'🎁 开始领取【{self.title}】任务奖励')
        json_data = {
            "strategyId": self.strategyId,
            "taskId": self.taskId,
            "taskCode": self.taskCode,
            "deviceId": self.get_deviceId()
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskStrategyService~fetchIntegral'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            print(f'✨ 【{self.title}】任务奖励领取成功！')
        else:
            print(f'❌ 【{self.title}】任务-{response.get("errorMessage")}')

    def do_honeyTask(self):
        # 做任务
        json_data = {"taskCode": self.taskCode}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberEs~taskRecord~finishTask'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            print(f'>【{self.taskType}】任务-已完成')
        else:
            print(f'>【{self.taskType}】任务-{response.get("errorMessage")}')

    def receive_honeyTask(self):
        print('>>>执行收取丰蜜任务')
        # 收取
        self.headers['syscode'] = 'MCS-MIMP-CORE'
        self.headers['channel'] = 'wxwdsj'
        self.headers['accept'] = 'application/json, text/plain, */*'
        self.headers['content-type'] = 'application/json;charset=UTF-8'
        self.headers['platform'] = 'MINI_PROGRAM'
        json_data = {"taskType": self.taskType}
        # print(json_data)
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeIndexService~receiveHoney'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            print(f'收取任务【{self.taskType}】成功！')
        else:
            print(f'收取任务【{self.taskType}】失败！原因：{response.get("errorMessage")}')


    def get_coupom(self, goods):  
        # 请求参数
        json_data = {
            "from": "Point_Mall",
            "orderSource": "POINT_MALL_EXCHANGE",
            "goodsNo": goods['goodsNo'],
            "quantity": 1,
            "taskCode": self.taskCode
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberGoods~pointMallService~createOrder'
    
        # 发起领券请求
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
           # print(f'> 领券成功！')
            return True  # 领取成功
        else:
           # print(f'> 领券失败！原因：{response.get("errorMessage")}')
            return False  # 领取失败
    
    
    def get_coupom_list(self):        
        # 请求参数
        json_data = {
            "memGrade": 2,
            "categoryCode": "SHTQ",
            "showCode": "SHTQWNTJ"
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberGoods~mallGoodsLifeService~list'
    
        # 发起获取券列表请求
        response = self.do_request(url, data=json_data)
    
        if response.get('success') == True:
            # 遍历所有分组的券列表
            all_goods = []
            for obj in response.get("obj", []):  # 遍历所有券分组
                goods_list = obj.get("goodsList", [])
                all_goods.extend(goods_list)  # 收集到一个总列表中
               
            # 尝试领取
            for goods in all_goods:
                exchange_times_limit = goods.get('exchangeTimesLimit', 0)
    
                # 检查券是否可兑换
                if exchange_times_limit >= 1:
                    #print(f'尝试领取：{goods["goodsName"]}')
                    
                    # 尝试领取券
                    if self.get_coupom(goods):
                        print('✨ 成功领取券，任务结束！')
                        return  # 成功领取后退出
            print('📝 所有券尝试完成，没有可用的券或全部领取失败。')
        else:
            print(f'> 获取券列表失败！原因：{response.get("errorMessage")}')



    def get_honeyTaskListStart(self):
        print('🍯 开始获取采蜜换大礼任务列表')
        # 任务列表
        json_data = {}
        self.headers['channel'] = 'wxwdsj'
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeIndexService~taskDetail'

        response = self.do_request(url, data=json_data)
        # print(response)
        if response.get('success') == True:
            for item in response["obj"]["list"]:
                self.taskType = item["taskType"]
                status = item["status"]
                if status == 3:
                    print(f'✨ 【{self.taskType}】-已完成')
                    continue
                if "taskCode" in item:
                    self.taskCode = item["taskCode"]
                    if self.taskType == 'DAILY_VIP_TASK_TYPE':
                        self.get_coupom_list()
                    else:
                        self.do_honeyTask()
                if self.taskType == 'BEES_GAME_TASK_TYPE':
                    self.honey_damaoxian()
                time.sleep(2)

    def honey_damaoxian(self):
        print('>>>执行大冒险任务')
        # 大冒险
        gameNum = 5
        for i in range(1, gameNum):
            json_data = {
                'gatherHoney': 20,
            }
            if gameNum < 0: break
            print(f'>>开始第{i}次大冒险')
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeGameService~gameReport'
            response = self.do_request(url, data=json_data)
            # print(response)
            stu = response.get('success')
            if stu:
                gameNum = response.get('obj')['gameNum']
                print(f'>大冒险成功！剩余次数【{gameNum}】')
                time.sleep(2)
                gameNum -= 1
            elif response.get("errorMessage") == '容量不足':
                print(f'> 需要扩容')
                self.honey_expand()
            else:
                print(f'>大冒险失败！【{response.get("errorMessage")}】')
                break

    def honey_expand(self):
        print('>>>容器扩容')
        # 大冒险
        gameNum = 5

        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeIndexService~expand'
        response = self.do_request(url, data={})
        # print(response)
        stu = response.get('success', False)
        if stu:
            obj = response.get('obj')
            print(f'>成功扩容【{obj}】容量')
        else:
            print(f'>扩容失败！【{response.get("errorMessage")}】')

    def honey_indexData(self, END=False):
        if not END: print('\n🍯 开始执行采蜜换大礼任务')
        # 邀请
        random_invite = random.choice([invite for invite in inviteId if invite != self.user_id])
        self.headers['channel'] = 'wxwdsj'
        json_data = {"inviteUserId": random_invite}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeIndexService~indexData'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            usableHoney = response.get('obj').get('usableHoney')
            if END:
                Log(f'🍯 当前丰蜜：【{usableHoney}】')
                return
            Log(f'🍯 执行前丰蜜：【{usableHoney}】')
            taskDetail = response.get('obj').get('taskDetail')
            activityEndTime = response.get('obj').get('activityEndTime', '')
            activity_end_time = datetime.strptime(activityEndTime, "%Y-%m-%d %H:%M:%S")
            current_time = datetime.now()

            if current_time.date() == activity_end_time.date():
                Log("⚠️ 本期活动今日结束，请及时兑换")
            else:
                print(f'📅 本期活动结束时间【{activityEndTime}】')

            if taskDetail != []:
                for task in taskDetail:
                    self.taskType = task['type']
                    self.receive_honeyTask()
                    time.sleep(2)

    def EAR_END_2023_TaskList(self):
        print('\n🎭 开始年终集卡任务')
        # 任务列表
        json_data = {
            "activityCode": "YEAREND_2024",
            "channelType": "MINI_PROGRAM"
        }
        self.headers['channel'] = '24nzdb'
        self.headers['platform'] = 'MINI_PROGRAM'
        self.headers['syscode'] = 'MCS-MIMP-CORE'

        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~taskList'

        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            for item in response["obj"]:
                self.title = item["taskName"]
                self.taskType = item["taskType"]
                status = item["status"]
                if status == 3:
                    print(f'✨ 【{self.taskType}】-已完成')
                    continue
                if self.taskType == 'INTEGRAL_EXCHANGE':
                    self.EAR_END_2023_ExchangeCard()
                elif self.taskType == 'CLICK_MY_SETTING':
                    self.taskCode = item["taskCode"]
                    self.addDeliverPrefer()
                if "taskCode" in item:
                    self.taskCode = item["taskCode"]
                    self.doTask()
                    time.sleep(3)
                    self.EAR_END_2023_receiveTask()
                else:
                    print(f'⚠️ 暂时不支持【{self.title}】任务')

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

    def EAR_END_2023_ExchangeCard(self):
        print(f'>>>开始积分兑换年卡')
        json_data = {
            "exchangeNum": 2,
            "activityCode": "YEAREND_2024",
            "channelType": "MINI_PROGRAM"
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonNoLoginPost/~memberNonactivity~yearEnd2024TaskService~integralExchange'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            receivedAccountList = response['obj']['receivedAccountList']
            for card in receivedAccountList:
                print(f'>获得：【{card["urrency"]}】卡【{card["amount"]}】张！')
        else:
            print(f'>【{self.title}】任务-{response.get("errorMessage")}')

    def EAR_END_2023_receiveTask(self):
        print(f'>>>开始领取【{self.title}】任务奖励')
        json_data = {
            "taskType": self.taskType,
            "activityCode": "YEAREND_2024",
            "channelType": "MINI_PROGRAM"
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonNoLoginPost/~memberNonactivity~yearEnd2024TaskService~fetchMixTaskReward'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            print(f'>【{self.title}】任务奖励领取成功！')
        else:
            print(f'>【{self.title}】任务-{response.get("errorMessage")}')

    def anniversary2024_weekly_gift_status(self):
        print(f'\n>>>>>>>开始周年庆任务')
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2024IndexService~weeklyGiftStatus'
        response = self.do_request(url)
        if response.get('success') == True:
            weekly_gift_list = response.get('obj', {}).get('weeklyGiftList', [])
            for weekly_gift in weekly_gift_list:
                if not weekly_gift.get('received'):
                    receive_start_time = datetime.strptime(weekly_gift['receiveStartTime'], '%Y-%m-%d %H:%M:%S')
                    receive_end_time = datetime.strptime(weekly_gift['receiveEndTime'], '%Y-%m-%d %H:%M:%S')
                    current_time = datetime.now()
                    # print(current_time)
                    # print(receive_start_time)
                    # print(receive_end_time)
                    if receive_start_time <= current_time <= receive_end_time:
                        self.anniversary2024_receive_weekly_gift()
        else:
            error_message = response.get('errorMessage') or json.dumps(response) or '无返回'
            print(f'查询每周领券失败: {error_message}')
            if '系统繁忙' in error_message or '用户手机号校验未通过' in error_message:
                self.anniversary_black = True

    def anniversary2024_receive_weekly_gift(self):
        print(f'>>>开始领取每周领券')
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2024IndexService~receiveWeeklyGift'
        response = self.do_request(url)
        if response.get('success'):
            product_names = [product['productName'] for product in response.get('obj', [])]
            print(f'每周领券: {product_names}')
        else:
            error_message = response.get('errorMessage') or json.dumps(response) or '无返回'
            print(f'每周领券失败: {error_message}')
            if '系统繁忙' in error_message or '用户手机号校验未通过' in error_message:
                self.anniversary_black = True

    def anniversary2024_taskList(self):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~taskList'
        data = {
            'activityCode': 'ANNIVERSARY_2024',
            'channelType': 'MINI_PROGRAM'
        }
        response = self.do_request(url, data)
        if response and response.get('success'):
            tasks = response.get('obj', [])
            # 过滤出状态为1的任务并尝试接收奖励
            for task in filter(lambda x: x['status'] == 1, tasks):
                if self.anniversary_black:
                    return
                for _ in range(task['canReceiveTokenNum']):
                    self.anniversary2024_fetchMixTaskReward(task)
            # 过滤出状态为2的任务并完成任务
            for task in filter(lambda x: x['status'] == 2, tasks):
                if self.anniversary_black:
                    return
                if task['taskType'] in ['PLAY_ACTIVITY_GAME', 'PLAY_HAPPY_ELIMINATION', 'PARTAKE_SUBJECT_GAME']:
                    pass
                elif task['taskType'] == 'FOLLOW_SFZHUNONG_VEDIO_ID':
                    pass
                elif task['taskType'] in ['BROWSE_VIP_CENTER', 'GUESS_GAME_TIP', 'CREATE_SFID', 'CLICK_MY_SETTING',
                                          'CLICK_TEMPLATE', 'REAL_NAME', 'SEND_SUCCESS_RECALL', 'OPEN_SVIP',
                                          'OPEN_FAST_CARD', 'FIRST_CHARGE_NEW_EXPRESS_CARD', 'CHARGE_NEW_EXPRESS_CARD',
                                          'INTEGRAL_EXCHANGE']:
                    pass
                else:
                    for _ in range(task['restFinishTime']):
                        if self.anniversary_black:
                            break
                        self.anniversary2024_finishTask(task)

    def anniversary2024_finishTask(self, task):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonRoutePost/memberEs/taskRecord/finishTask'
        data = {'taskCode': task['taskCode']}
        response = self.do_request(url, data)
        if response and response.get('success'):
            print('完成任务[%s]成功' % task['taskName'])
            # 完成任务后获取任务奖励的逻辑
            self.anniversary2024_fetchMixTaskReward(task)
        else:
            print('完成任务[%s]失败: %s' % (
                task['taskName'], response.get('errorMessage') or (json.dumps(response) if response else '无返回')))

    def anniversary2024_fetchMixTaskReward(self, task):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2024TaskService~fetchMixTaskReward'
        data = {
            'taskType': task['taskType'],
            'activityCode': 'ANNIVERSARY_2024',
            'channelType': 'MINI_PROGRAM'
        }
        response = self.do_request(url, data)
        if response and response.get('success'):
            reward_info = response.get('obj', {}).get('account', {})
            received_list = [f"[{item['currency']}]X{item['amount']}" for item in
                             reward_info.get('receivedAccountList', [])]
            turned_award = reward_info.get('turnedAward', {})
            if turned_award.get('productName'):
                received_list.append(f"[优惠券]{turned_award['productName']}")
            print('领取任务[%s]奖励: %s' % (task['taskName'], ', '.join(received_list)))
        else:
            error_message = response.get('errorMessage') or json.dumps(response) or '无返回'
            print('领取任务[%s]奖励失败: %s' % (task['taskName'], error_message))
            if '用户手机号校验未通过' in error_message:
                self.anniversary_black = True

    def anniversary2024_unbox(self):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2024CardService~unbox'
        response = self.do_request(url, {})
        if response and response.get('success'):
            account_info = response.get('obj', {}).get('account', {})
            unbox_list = [f"[{item['currency']}]X{item['amount']}" for item in
                          account_info.get('receivedAccountList', [])]
            print('拆盒子: %s' % ', '.join(unbox_list) or '空气')
        else:
            error_message = response.get('errorMessage') or json.dumps(response) or '无返回'
            print('拆盒子失败: %s' % error_message)
            if '用户手机号校验未通过' in error_message:
                self.anniversary_black = True

    def anniversary2024_game_list(self):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2024GameParkService~list'
        response = self.do_request(url, {})
        try:
            if response['success']:
                topic_pk_info = response['obj'].get('topicPKInfo', {})
                search_word_info = response['obj'].get('searchWordInfo', {})
                happy_elimination_info = response['obj'].get('happyEliminationInfo', {})

                if not topic_pk_info.get('isPassFlag'):
                    print('开始话题PK赛')
                    # 这里调用话题PK赛列表相关函数
                    self.anniversary2024_TopicPk_topicList()

                if not search_word_info.get('isPassFlag') or not search_word_info.get('isFinishDailyFlag'):
                    print('开始找字游戏')
                    for i in range(1, 11):
                        wait_time = random.randint(1000, 3000) / 1000.0  # 转换为秒
                        time.sleep(wait_time)
                        if not self.anniversary2024_SearchWord_win(i):
                            break

                if not happy_elimination_info.get('isPassFlag') or not happy_elimination_info.get('isFinishDailyFlag'):
                    print('开始消消乐')
                    for i in range(1, 31):
                        wait_time = random.randint(2000, 4000) / 1000.0  # 转换为秒
                        time.sleep(wait_time)
                        if not self.anniversary2024_HappyElimination_win(i):
                            break
            else:
                error_message = response['errorMessage'] or json.dumps(response) or '无返回'
                print('查询游戏状态失败: ' + error_message)
                if '用户手机号校验未通过' in error_message:
                    self.anniversary_black = True
        except Exception as e:
            print(str(e))

    def anniversary2024_SearchWord_win(self, index):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2024SearchWordService~win'
        success = True
        try:
            data = {'index': index}
            response = self.do_request(url, data)
            if response and response.get('success'):
                currency_list = response.get('obj', {}).get('currencyDTOList', [])
                rewards = ', '.join([f"[{c.get('currency')}]X{c.get('amount')}" for c in currency_list])
                print(f'找字游戏第{index}关通关成功: {rewards if rewards else "未获得奖励"}')
            else:
                error_message = response.get('errorMessage') or json.dumps(response) or '无返回'
                print(f'找字游戏第{index}关失败: {error_message}')
                if '系统繁忙' in error_message:
                    success = False
        except Exception as e:
            print(e)
        finally:
            return success

    def anniversary2024_HappyElimination_win(self, index):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2024HappyEliminationService~win'
        success = True
        data = {'index': index}
        response = self.do_request(url, data)
        try:
            if response and response.get('success'):
                is_award = response['obj'].get('isAward')
                currency_dto_list = response['obj'].get('currencyDTOList', [])
                rewards = ', '.join([f"[{c.get('currency')}]X{c.get('amount')}" for c in currency_dto_list])
                print(f'第{index}关通关: {rewards if rewards else "未获得奖励"}')
            else:
                error_message = response.get('errorMessage') or json.dumps(response) or '无返回'
                print(f'第{index}关失败: {error_message}')
                if '系统繁忙' in error_message:
                    success = False
        except Exception as e:
            print(e)
            success = False
        finally:
            return success

    def anniversary2024_TopicPk_chooseSide(self, index):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2024TopicPkService~chooseSide'
        success = True
        data = {'index': index, 'choose': 0}  # 选择某一边
        response = self.do_request(url, data)
        try:
            if response and response.get('success'):
                currency_dto_list = response['obj'].get('currencyDTOList', [])
                rewards = ', '.join([f"[{c.get('currency')}]X{c.get('amount')}" for c in currency_dto_list])
                print(f'话题PK赛选择话题{index}成功： {rewards if rewards else "未获得奖励"}')
            else:
                error_message = response['errorMessage'] or json.dumps(response) or '无返回'
                print(f'话题PK赛选择话题{index}失败： {error_message}')
                if '系统繁忙' in error_message:
                    success = False
        except Exception as e:
            print(e)
            success = False
        finally:
            return success

    def anniversary2024_TopicPk_topicList(self):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2024TopicPkService~topicList'
        response = self.do_request(url, {})
        try:
            if response and response.get('success'):
                topics = response['obj'].get('topics', [])
                for topic in topics:
                    if not topic.get('choose'):
                        index = topic.get('index', 1)
                        wait_time = random.randint(2000, 4000) / 1000.0  # 转换为秒
                        time.sleep(wait_time)  # 等待
                        if not self.anniversary2024_TopicPk_chooseSide(index):
                            break
            else:
                error_message = response['errorMessage'] or json.dumps(response) or '无返回'
                print(f'📝 查询话题PK赛记录失败： {error_message}')
        except Exception as e:
            print(e)

    def anniversary2024_queryAccountStatus_refresh(self):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2024CardService~queryAccountStatus'
        response = self.do_request(url, {})
        try:
            if not response or not response.get('success'):
                error_message = response['errorMessage'] or json.dumps(response) or '无返回'
                print(f'📝 查询账户状态失败： {error_message}')
        except Exception as e:
            print(e)

    def anniversary2024_TopicPk_chooseSide(self, index):
        success = True
        data = {
            'index': index,
            'choose': 0
        }
        self.headers['channel'] = '31annizyw'
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2024TopicPkService~chooseSide'
        result = self.do_request(url, data, 'post')

        if result and result.get('success'):
            currency_dto_list = result.get('obj', {}).get('currencyDTOList', [])
            if currency_dto_list:
                rewards = [f"[{currency['currency']}]{currency['amount']}次" for currency in currency_dto_list]
                print(f'🎭 话题PK赛第{index}个话题选择成功: {", ".join(rewards)}')
            else:
                print(f'🎭 话题PK赛第{index}个话题选择成功')
        else:
            error_message = result.get('errorMessage') if result else '无返回'
            print(f'📝 话题PK赛第{index}个话题失败: {error_message}')
            if error_message and '系统繁忙' in error_message:
                success = False

        return success

    def anniversary2024_titleList(self):
        return
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2024GuessService~titleList'
        response = self.do_request(url)

        if response and response.get('success'):

            guess_title_info_list = response.get('obj', {}).get('guessTitleInfoList', [])
            today_titles = [title for title in guess_title_info_list if title['gameDate'] == self.today]
            for title_info in today_titles:
                if title_info['answerStatus']:
                    print('📝 今日已回答过竞猜')
                else:
                    answer = self.answer
                    if answer:
                        self.anniversary2024_answer(title_info, answer)
                        print(f'📝 进行了答题: {answer}')
        else:
            error_message = response.get('errorMessage') if response else '无返回'
            print(f'📝 查询每日口令竞猜失败: {error_message}')

    def anniversary2024_titleList_award(self):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2024GuessService~titleList'
        response = self.do_request(url)

        if response and response.get('success'):

            guess_title_info_list = response.get('obj', {}).get('guessTitleInfoList', [])
            today_awards = [title for title in guess_title_info_list if title['gameDate'] == self.today]

            for award_info in today_awards:
                if award_info['answerStatus']:
                    awards = award_info.get('awardList', []) + award_info.get('puzzleList', [])
                    awards_description = ', '.join([f"{award['productName']}" for award in awards])
                    print(f'🎁 口令竞猜奖励: {awards_description}' if awards_description else '📝 今日无奖励')
                else:
                    print('📝 今日还没回答竞猜')
        else:
            error_message = response.get('errorMessage') if response else '无返回'
            print(f'📝 查询每日口令竞猜奖励失败: {error_message}')

    # 向API发送答题请求
    def anniversary2024_answer(self, answer_info):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2024GuessService~answer'
        data = {'period': answer_info['period'], 'answerInfo': answer_info}
        response = self.do_request(url, data)
        if response and response.get('success'):
            print('📝 口令竞猜回答成功')
            self.anniversary2024_titleList_award()  # 通过奖励接口验证答案
        else:
            error_message = response.get('errorMessage') if response else '无返回'
            print(f'📝 口令竞猜回答失败: {error_message}')

    # 查询账户状态
    def anniversary2024_queryAccountStatus(self):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2024CardService~queryAccountStatus'
        result = self.do_request(url)
        if result.get('success'):
            account_currency_list = result.get('obj', {}).get('accountCurrencyList', [])
            unbox_chance_currency = [currency for currency in account_currency_list if
                                     currency.get('currency') == 'UNBOX_CHANCE']
            unbox_chance_balance = unbox_chance_currency[0].get('balance') if unbox_chance_currency else 0

            # print('可以拆' + str(unbox_chance_balance) + '次盒子')
            # while unbox_chance_balance > 0:
            #     self.anniversary2024_unbox()
            #     unbox_chance_balance -= 1
        else:
            error_message = result.get('errorMessage') or json.dumps(result) or '无返回'
            print('📝 查询已收集拼图失败: ' + error_message)

        result = self.do_request(url)
        if result.get('success'):
            account_currency_list = result.get('obj', {}).get('accountCurrencyList', [])
            account_currency_list = [currency for currency in account_currency_list if
                                     currency.get('currency') != 'UNBOX_CHANCE']
            if account_currency_list:
                cards_li = account_currency_list
                card_info = []
                self.cards = {
                    'CARD_1': 0,
                    'CARD_2': 0,
                    'CARD_3': 0,
                    'CARD_4': 0,
                    'CARD_5': 0,
                    'CARD_6': 0,
                    'CARD_7': 0,
                    'CARD_8': 0,
                    'CARD_9': 0,
                    'COMMON_CARD': 0
                }
                for card in cards_li:
                    currency_key = card.get('currency')
                    if currency_key in self.cards:
                        self.cards[currency_key] = int(card.get('balance'))
                    card_info.append('[' + card.get('currency') + ']X' + str(card.get('balance')))

                Log(f'📝 已收集拼图: {card_info}')
                cards_li.sort(key=lambda x: x.get('balance'), reverse=True)

            else:
                print('📝 还没有收集到拼图')
        else:
            error_message = result.get('errorMessage') or json.dumps(result) or '无返回'
            print('📝 查询已收集拼图失败: ' + error_message)

    def do_draw(self, cards):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2024CardService~collectDrawAward'
        data = {"accountList": cards}
        response = self.do_request(url, data)
        if response and response.get('success'):
            data = response.get('obj', {})
            productName = data.get('productName', '')
            Log(f'🎁 抽奖成功,获得{productName}')
            return True
        else:
            error_message = response.get('errorMessage') if response else '无返回'
            print(f'📝 抽奖失败: {error_message}')
            return False

    def convert_common_card(self, cards, target_card):
        # 如果共通卡(COMMON_CARD)的数量大于0，转化成目标卡
        if cards['COMMON_CARD'] > 0:
            cards['COMMON_CARD'] -= 1
            cards[target_card] += 1
            return True
        return False

    def can_draw(self, cards, n):
        # 判断是否有足够的不同卡进行抽奖
        distinct_cards = sum(1 for card, amount in cards.items() if card != 'COMMON_CARD' and amount > 0)
        return distinct_cards >= n

    def draw(self, cards, n):
        drawn_cards = []
        for card, amount in sorted(cards.items(), key=lambda item: item[1]):
            if card != 'COMMON_CARD' and amount > 0:
                cards[card] -= 1
                drawn_cards.append(card)
                if len(drawn_cards) == n:
                    break
        if len(drawn_cards) == n:
            "📝 没有足够的卡进行抽奖"
        if self.do_draw(drawn_cards):
            return drawn_cards  # 返回本次抽奖使用的卡
        else:
            return None

    def simulate_lottery(self, cards):
        while self.can_draw(cards, 9):
            used_cards = self.draw(cards, 9)
            print("🎁 进行了一次9卡抽奖，消耗卡片: ", used_cards)
        while self.can_draw(cards, 7) or self.convert_common_card(cards, 'CARD_1'):
            if not self.can_draw(cards, 7):
                continue
            used_cards = self.draw(cards, 7)
            print("🎁 进行了一次7卡抽奖，消耗卡片: ", used_cards)
        while self.can_draw(cards, 5) or self.convert_common_card(cards, 'CARD_1'):
            if not self.can_draw(cards, 5):
                continue
            used_cards = self.draw(cards, 5)
            print("🎁 进行了一次5卡抽奖，消耗卡片: ", used_cards)
        while self.can_draw(cards, 3) or self.convert_common_card(cards, 'CARD_1'):
            if not self.can_draw(cards, 3):
                continue
            used_cards = self.draw(cards, 3)
            print("🎁 进行了一次3卡抽奖，消耗卡片: ", used_cards)

    def anniversary2024_task(self):
        self.anniversary2024_weekly_gift_status()
        if self.anniversary_black:
            return
        # self.anniversary2024_titleList()
        # self.anniversary2024_game_list()
        # self.anniversary2024_taskList()
        self.anniversary2024_queryAccountStatus()
        target_time = datetime(2025, 4, 3, 14, 0)
        # self.simulate_lottery(self.cards)
        if datetime.now() > target_time:
            print('📅 周年庆活动即将结束，开始自动抽奖')
            self.simulate_lottery(self.cards)
        else:
            print('📅 未到自动抽奖时间')

    def member_day_index(self):
        print('🎭 会员日活动')
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
                Log(f'🎁 会员日可以抽奖{lottery_num}次')
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
                Log(f'📝 查询会员日失败: {error_message}')
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('📝 会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_receive_invite_award(self, invite_user_id):
        try:
            payload = {'inviteUserId': invite_user_id}

            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayIndexService~receiveInviteAward'

            response = self.do_request(url, payload)
            if response.get('success'):
                product_name = response.get('obj', {}).get('productName', '空气')
                Log(f'🎁 会员日奖励: {product_name}')
            else:
                error_message = response.get('errorMessage', '无返回')
                Log(f'📝 领取会员日奖励失败: {error_message}')
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('📝 会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_lottery(self):
        try:
            payload = {}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayLotteryService~lottery'

            response = self.do_request(url, payload)
            if response.get('success'):
                product_name = response.get('obj', {}).get('productName', '空气')
                Log(f'🎁 会员日抽奖: {product_name}')
            else:
                error_message = response.get('errorMessage', '无返回')
                Log(f'📝 会员日抽奖失败: {error_message}')
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('📝 会员日任务风控')
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
                Log('📝 查询会员日任务失败: ' + error_message)
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('📝 会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_finish_task(self, task):
        try:
            payload = {'taskCode': task['taskCode']}

            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberEs~taskRecord~finishTask'

            response = self.do_request(url, payload)
            if response.get('success'):
                Log('📝 完成会员日任务[' + task['taskName'] + ']成功')
                self.member_day_fetch_mix_task_reward(task)
            else:
                error_message = response.get('errorMessage', '无返回')
                Log('📝 完成会员日任务[' + task['taskName'] + ']失败: ' + error_message)
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('📝 会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_fetch_mix_task_reward(self, task):
        try:
            payload = {'taskType': task['taskType'], 'activityCode': 'MEMBER_DAY', 'channelType': 'MINI_PROGRAM'}

            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~fetchMixTaskReward'

            response = self.do_request(url, payload)
            if response.get('success'):
                Log('🎁 领取会员日任务[' + task['taskName'] + ']奖励成功')
            else:
                error_message = response.get('errorMessage', '无返回')
                Log('📝 领取会员日任务[' + task['taskName'] + ']奖励失败: ' + error_message)
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('📝 会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_receive_red_packet(self, hour):
        try:
            payload = {'receiveHour': hour}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayTaskService~receiveRedPacket'

            response = self.do_request(url, payload)
            if response.get('success'):
                print(f'🎁 会员日领取{hour}点红包成功')
            else:
                error_message = response.get('errorMessage', '无返回')
                print(f'📝 会员日领取{hour}点红包失败: {error_message}')
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('📝 会员日任务风控')
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

                Log("📝 会员日合成列表: " + ", ".join(packet_summary))

                if self.member_day_red_packet_map.get(self.max_level):
                    Log(f"🎁 会员日已拥有[{self.max_level}级]红包X{self.member_day_red_packet_map[self.max_level]}")
                    self.member_day_red_packet_draw(self.max_level)
                else:
                    remaining = self.packet_threshold - remaining_needed
                    Log(f"📝 会员日距离[{self.max_level}级]红包还差: [1级]红包X{remaining}")

            else:
                error_message = response.get('errorMessage', '无返回')
                Log(f'📝 查询会员日合成失败: {error_message}')
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('📝 会员日任务风控')
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
                Log(f'🎁 会员日合成: [{level}级]红包X2 -> [{level + 1}级]红包')
                self.member_day_red_packet_map[level] -= 2
                if not self.member_day_red_packet_map.get(level + 1):
                    self.member_day_red_packet_map[level + 1] = 0
                self.member_day_red_packet_map[level + 1] += 1
            else:
                error_message = response.get('errorMessage', '无返回')
                Log(f'📝 会员日合成两个[{level}级]红包失败: {error_message}')
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('📝 会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_red_packet_draw(self, level):
        try:
            payload = {'level': str(level)}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayPacketService~redPacketDraw'
            response = self.do_request(url, payload)
            if response and response.get('success'):
                coupon_names = [item['couponName'] for item in response.get('obj', [])] or []

                Log(f"🎁 会员日提取[{level}级]红包: {', '.join(coupon_names) or '空气'}")
            else:
                error_message = response.get('errorMessage') if response else "无返回"
                Log(f"📝 会员日提取[{level}级]红包失败: {error_message}")
                if "没有资格参与活动" in error_message:
                    self.memberDay_black = True
                    print("📝 会员日任务风控")
        except Exception as e:
            print(e)

    def DRAGONBOAT_2024_index(self):
        print('📝 查询财神活动状态')
        invite_user_id = random.choice([invite for invite in inviteId if invite != self.user_id])
        try:
            self.headers['channel'] = '24nzdb'
            self.headers[
                'referer'] = f'https://mcs-mimp-web.sf-express.com/origin/a/mimp-activity/yearEnd2024?mobile={self.mobile}&userId={self.user_id}&path=/origin/a/mimp-activity/yearEnd2024&supportShare=&inviteUserId={invite_user_id}&from=newExpressWX'
            payload = {}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonNoLoginPost/~memberNonactivity~yearEnd2024IndexService~index'

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
                    print('📝 推财神进行中....')
                    return True
                else:
                    print('📝 推财神活动已结束')
                    return False
            else:
                error_message = response.get('errorMessage', '无返回')
                if '没有资格参与活动' in error_message:
                    self.DRAGONBOAT_2024_black = True
                    Log('📝 会员日任务风控')
                return False
        except Exception as e:
            print(e)
            return False

    def DRAGONBOAT_2024_Game_indexInfo(self):
        Log('🎭 开始推财神游戏')
        try:
            payload = {}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~yearEnd2024GameService~indexInfo'

            response = self.do_request(url, payload)
            # print(response)
            if response.get('success'):
                obj = response.get('obj', [{}])
                maxPassLevel = obj.get('maxPassLevel', '')
                ifPassAllLevel = obj.get('ifPassAllLevel', '')
                if maxPassLevel != 30:
                    self.DRAGONBOAT_2024_win(maxPassLevel)
                else:
                    self.DRAGONBOAT_2024_win(0)

            else:
                error_message = response.get('errorMessage', '无返回')
                if '没有资格参与活动' in error_message:
                    self.DRAGONBOAT_2024_black = True
                    Log('📝 会员日任务风控')
                return False
        except Exception as e:
            print(e)
            return False

    def DRAGONBOAT_2024_Game_init(self):
        Log('🎭 开始推财神游戏')
        try:
            payload = {}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~yearEnd2024GameService~init'

            response = self.do_request(url, payload)
            # print(response)
            if response.get('success'):
                obj = response.get('obj', [{}])
                currentIndex = obj.get('currentIndex', '')
                ifPassAllLevel = obj.get('ifPassAllLevel', '')
                if currentIndex != 30:
                    self.DRAGONBOAT_2024_win(currentIndex)
                else:
                    self.DRAGONBOAT_2024_win(0)

            else:
                error_message = response.get('errorMessage', '无返回')
                if '没有资格参与活动' in error_message:
                    self.DRAGONBOAT_2024_black = True
                    Log('📝 会员日任务风控')
                return False
        except Exception as e:
            print(e)
            return False

    def DRAGONBOAT_2024_weeklyGiftStatus(self):
        print('📝 查询每周礼包领取状态')
        try:
            payload = {}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~yearEnd2024IndexService~weeklyGiftStatus'

            response = self.do_request(url, payload)
            # print(response)
            if response.get('success'):
                obj = response.get('obj', [{}])
                for gift in obj:
                    received = gift['received']
                    receiveStartTime = gift['receiveStartTime']
                    receiveEndTime = gift['receiveEndTime']
                    print(f'📝 领取时间：【{receiveStartTime} 至 {receiveEndTime}】')
                    if received:
                        print('📝 该礼包已领取')
                        continue
                    receive_start_time = datetime.strptime(receiveStartTime, "%Y-%m-%d %H:%M:%S")
                    receive_end_time = datetime.strptime(receiveEndTime, "%Y-%m-%d %H:%M:%S")
                    is_within_range = receive_start_time <= datetime.now() <= receive_end_time
                    if is_within_range:
                        print(f'🎁 开始领取礼包：')
                        self.DRAGONBOAT_2024_receiveWeeklyGift()
            else:
                error_message = response.get('errorMessage', '无返回')
                if '没有资格参与活动' in error_message:
                    self.DRAGONBOAT_2024_black = True
                    Log('📝 会员日任务风控')
        except Exception as e:
            print(e)

    def DRAGONBOAT_2024_receiveWeeklyGift(self):
        invite_user_id = random.choice([invite for invite in inviteId if invite != self.user_id])
        try:
            payload = {"inviteUserId": invite_user_id}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~yearEnd2024IndexService~receiveWeeklyGift'

            response = self.do_request(url, payload)
            # print(response)
            if response.get('success'):
                obj = response.get('obj', [{}])
                if obj == [{}]:
                    print('📝 领取失败')
                    return False
                for gifts in obj:
                    productName = gifts['productName']
                    amount = gifts['amount']
                    print(f'🎁 领取【{productName} x {amount}】成功')
            else:
                error_message = response.get('errorMessage', '无返回')
                if '没有资格参与活动' in error_message:
                    self.DRAGONBOAT_2024_black = True
                    Log('📝 会员日任务风控')
        except Exception as e:
            print(e)

    def DRAGONBOAT_2024_taskList(self):
        print('📝 查询推币任务列表')
        try:
            payload = {
                "activityCode": "DRAGONBOAT_2024",
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
                        Log(f'📝 任务【{self.taskName}】已完成')
                        continue
                    self.taskCode = task.get('taskCode', None)
                    if self.taskCode:
                        self.DRAGONBOAT_2024_finishTask()
                    if taskType == 'PLAY_ACTIVITY_GAME':
                        self.DRAGONBOAT_2024_Game_init()
            else:
                error_message = response.get('errorMessage', '无返回')
                if '没有资格参与活动' in error_message:
                    self.DRAGONBOAT_2024_black = True
                    Log('📝 会员日任务风控')
        except Exception as e:
            print(e)

    def DRAGONBOAT_2024_coinStatus(self, END=False):
        Log('📝 查询金币信息')
        # try:
        payload = {}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~yearEnd2024CoinService~coinStatus'

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
                        print(f'📝 开始第【{PUSH_TIMES_balance + 1}】次推币')
                        self.DRAGONBOAT_2024_pushCoin()
                        PUSH_TIMES -= 1
                        pushedTimesToday += 1
                        pushedTimesTotal += 1
                Log(f'📝 剩余推币次数：【{PUSH_TIMES}】')
                Log(f'📝 当前金币：【{self.COIN_balance}】')
                # Log(f'> 当前发财卡：【{WELFARE_CARD_balance}】')
                Log(f'📝 今日推币：【{pushedTimesToday}】次')
                Log(f'📝 总推币：【{pushedTimesTotal}】次')
            else:
                print(f'📝 剩余推币次数：【{PUSH_TIMES_balance}】')
                print(f'📝 当前金币：【{self.COIN_balance}】')
                # Log(f'> 当前发财卡：【{WELFARE_CARD_balance}】')
                print(f'📝 今日推币：【{pushedTimesToday}】次')
                print(f'📝 总推币：【{pushedTimesTotal}】次')

            self.DRAGONBOAT_2024_givePushTimes()
        else:
            error_message = response.get('errorMessage', '无返回')
            if '没有资格参与活动' in error_message:
                self.DRAGONBOAT_2024_black = True
                Log('📝 会员日任务风控')
        # except Exception as e:
        #     print(e)

    def DRAGONBOAT_2024_pushCoin(self):
        try:
            payload = {"plateToken": None}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~yearEnd2024CoinService~pushCoin'

            response = self.do_request(url, payload)
            # print(response)
            if response.get('success'):
                obj = response.get('obj', [{}])
                drawAward = obj.get('drawAward', '')
                self.COIN_balance += drawAward
                print(f'📝 获得：【{drawAward}】金币')

            else:
                error_message = response.get('errorMessage', '无返回')
                if '没有资格参与活动' in error_message:
                    self.DRAGONBOAT_2024_black = True
                    Log('📝 会员日任务风控')
        except Exception as e:
            print(e)

    def DRAGONBOAT_2024_givePushTimes(self):
        Log('🎁 领取赠送推币次数')
        try:
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~yearEnd2024CoinService~givePushTimes'

            response = self.do_request(url)
            # print(response)
            if response.get('success'):
                obj = response.get('obj', 0)
                print(f'🎁 获得：【{obj}】次推币机会')
            else:
                error_message = response.get('errorMessage', '无返回')
                if '没有资格参与活动' in error_message:
                    self.DRAGONBOAT_2024_black = True
                    Log('📝 会员日任务风控')
                print(error_message)
        except Exception as e:
            print(e)

    def DRAGONBOAT_2024_finishTask(self):
        try:
            payload = {
                "taskCode": self.taskCode
            }
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberEs~taskRecord~finishTask'

            response = self.do_request(url, payload)
            # print(response)
            if response.get('success'):
                obj = response.get('obj', False)
                Log(f'📝 完成任务【{self.taskName}】成功')
            else:
                error_message = response.get('errorMessage', '无返回')
                if '没有资格参与活动' in error_message:
                    self.DRAGONBOAT_2024_black = True
                    Log('📝 会员日任务风控')
        except Exception as e:
            print(e)

    def DRAGONBOAT_2024_win(self, level):
        try:
            for i in range(level, 16):
                print(f'> 正在开始第【{i}】关...')
                payload = {"levelIndex": i}
                url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~dragonBoat2024GameService~win"
                response = self.do_request(url, payload)
                if response.get('success'):
                    obj = response.get('obj', {})
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
                        self.DRAGONBOAT_2024_black = True
                        Log('会员日任务风控')
        except Exception as e:
            print(e)
            
    def znq2025(self):
        """
        查询32周年庆任务列表，并处理任务逻辑（集成新接口）
        """
        try:
            self.get_anniversary_wishes()

            payload = {"activityCode": "ANNIVERSARY_2025", "channelType": "SFAPP"}
            url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~taskList"
            response = self.do_request(url, payload)

            if isinstance(response, dict) and response.get('success'):
                tasks = response.get('obj', [])
                for task in tasks:
                    taskType = task.get('taskType', None)
                    taskName = task.get('taskName', '未知任务')
                    taskCode = task.get('taskCode', None)
                    taskStatus = task.get('status', 0)

                    Log(f"> 正在处理任务【{taskName}】，类型：【{taskType}】，状态：【{taskStatus}】")

                    # 跳过已完成任务
                    if taskStatus == 3:
                        Log(f"> 任务【{taskName}】已完成，跳过")
                        continue

                    # 如果任务类型是"PLAY_ACTIVITY_GAME"，处理闯关逻辑
                    if taskType == 'PLAY_ACTIVITY_GAME':
                        try:
                            u = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~yearEnd2024GameService~resurrect"
                            resurrect_payload = {}  # 该接口不需要参数
                            rs = self.do_request(u, resurrect_payload)

                            if rs.get('success'):
                                obj = rs.get('obj', {})
                                user_status = obj.get('userStatus', 1)  # 默认值为 1，表示第一关
                                resurrect_time = obj.get('resurrectTime', 0)  # 复活次数

                                # 提示用户当前所在关卡
                                Log(f"> 当前用户在第【{user_status}】关")
                                Log(f"> 用户已经复活了【{resurrect_time}】次")

                                # 开始闯关
                                Log(f"> 开始闯关，从第 {user_status} 关开始")
                                self.DRAGONBOAT_2025_win(user_status)
                            else:
                                error_message = rs.get('errorMessage', '未知错误')
                                Log(f"> 无法获取用户关卡：{error_message}")
                        except Exception as e:
                            import traceback
                            Log(f"获取用户当前关卡时出现异常：{e}\n{traceback.format_exc()}")

                    # 如果有其他任务处理逻辑
                    if taskCode:
                        self.DRAGONBOAT_2025_finishTask(taskCode, taskName)
                    if taskType == "GIVING_BLESS":
                        self.send_anniversary_wish()

            self.exchange_integral(1)
            
            #开始抽奖
            # self.zcs()
        except Exception as e:
            import traceback
            Log(f"任务查询时出现异常：{e}\n{traceback.format_exc()}")

    def get_anniversary_wishes(self):
        """获取32周年愿望列表"""
        try:
            url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2025WishService~getWishes"
            response = self.do_request(url, {})  # 空请求体
            
            if isinstance(response, dict) and response.get('success'):
                wish_data = response.get('obj', {})
                Log(f"当前许愿总数：{wish_data.get('wishedNum', 0)}")
                return wish_data.get('wishes', [])
            return []
        except Exception as e:
            Log(f"获取愿望列表异常：{str(e)}")
            return []

    def send_anniversary_wish(self):
        """发送32周年愿望"""
        try:
            url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2025WishService~sendWish"
            response = self.do_request(url, {})  # 空请求体
            
            if isinstance(response, dict) and response.get('success'):
                result = response.get('obj', {})
                Log(f"注册日期：{result.get('registerDate')} 累计天数：{result.get('registerDaysNum')}")
                return result
            return None
        except Exception as e:
            Log(f"发送愿望异常：{str(e)}")
            return None

    def exchange_integral(self, exchange_num=1):
        """积分兑换"""
        try:
            url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2025TaskService~integralExchange"
            payload = {
                "exchangeNum": exchange_num,
                "activityCode": "ANNIVERSARY_2025"
            }
            response = self.do_request(url, payload)
            
            if isinstance(response, dict) and response.get('success'):
                result = response.get('obj', {})
                accounts = result.get('currentAccountList', [])
                for acc in accounts:
                    Log(f"{acc.get('currency')} 总数：{acc.get('totalAmount')} 剩余：{acc.get('balance')}")
                return result
            return None
        except Exception as e:
            Log(f"积分兑换异常：{str(e)}")
            return None
    
    def cxcs(self):
        Log('====== 开始抽勋章 ======')
        try:
            # 查询剩余机会
            query_payload = {}
            query_url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2025ClaimService~claimStatus'
            query_response = self.do_request(query_url, query_payload)

            if query_response.get('success') and query_response.get('obj'):
                obj = query_response.get('obj')
                # 获取当前 WEALTH_CHANCE 次数
                current_account_list = obj.get('currentAccountList', [])
                claim_change = 0
                # for account in current_account_list:
                #     if account.get('currency') == 'CLAIM_CHANCE':
                #         claim_change = account.get('balance', 0)
                #         break
                claim_change = current_account_list[0].get('balance',0)
                # self.fecth_chance()
                Log(f'当前有 {claim_change} 次抽勋章机会')

                # 开始抽奖
                if claim_change > 0:
                    draw_url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2025ClaimService~claim"
                    for i in range(claim_change):
                        Log(f'>>> 开始第 {i + 1} 次抽勋章')
                        draw_payload = {}
                        draw_response = self.do_request(draw_url, draw_payload)

                        if draw_response.get('success') and draw_response.get('obj'):
                            draw_obj = draw_response.get('obj')
                            # 提取抽中的奖励列表
                            received_account_list = draw_obj.get('receivedAccountList', [])

                            for reward in received_account_list:
                                currency = reward.get('currency', 'UNKNOWN')
                                amount = reward.get('amount', 0)

                                # 映射 currency 到勋章名称
                                if currency == 'DAI_BI':
                                    Log(f'抽中勋章：坐以待币 x{amount}')
                                elif currency == 'DING_ZHU':
                                    Log(f'抽中勋章：都顶得住 x{amount}')
                                elif currency == 'ZHI_SHUI':
                                    Log(f'抽中勋章：心如止水 x{amount}')
                                elif currency == 'CHENG_GONG':
                                    Log(f'抽中勋章：成功人士 x{amount}')
                                elif currency == 'GAN_FAN':
                                    Log(f'抽中勋章：干饭圣体 x{amount}')
                                elif currency == 'TIETIE_CARD':
                                    Log(f'抽中勋章：贴贴卡 x{amount}')
                                else:
                                    Log(f'抽中勋章：未知奖励【{currency}】x{amount}')
                        else:
                            error_message = draw_response.get('errorMessage', '无返回')
                            Log(f'抽奖失败: {error_message}')
                        time.sleep(5)  # 等待 1 秒，避免触发风控
                else:
                    Log('没有剩余的抽勋章机会')

            else:
                # 如果查询失败，打印错误信息
                error_message = query_response.get('errorMessage', '无法查询抽财神机会')
                Log(f'查询抽勋章机会失败，原因：{error_message}')

        except Exception as e:
            import traceback
            Log(f'抽勋章时出现异常：{e}\n{traceback.format_exc()}')

        Log('====== 抽勋章结束 ======')

    def index2025(self):
        Log(f'====== {self.mobile}开始查询勋章状态 ======')

        try:
            # 查询勋章卡片
            query_payload = {}
            query_url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2025ClaimService~claimStatus"
            query_response = self.do_request(query_url, query_payload)

            if query_response.get('success') and query_response.get('obj'):
                obj = query_response.get('obj', {})
                current_account_list = obj.get('currentAccountList', [])

                # 初始化各路财神的计数
                wealth_counts = {
                    "坐以待币": 0,
                    "都顶得住": 0,
                    "心如止水": 0,
                    "成功人士": 0,
                    "干饭圣体": 0,
                    "贴贴卡":0,

                }

                # 遍历账户列表，根据 currency 类型进行统计
                for account in current_account_list:
                    currency = account.get('currency')
                    balance = account.get('balance', 0)
                    if currency == "GAN_FAN":  # 干饭圣体
                        wealth_counts["干饭圣体"] += balance
                    elif currency == "ZHI_SHUI":  # 心如止水
                        wealth_counts["心如止水"] += balance
                    elif currency == "DING_ZHU":  # 都顶得住
                        wealth_counts["都顶得住"] += balance
                    elif currency == "DAI_BI":  # 西路财神
                        wealth_counts["坐以待币"] += balance
                    elif currency == "CHENG_GONG":  # 南路财神
                        wealth_counts["成功人士"] += balance
                    elif currency=="TIETIE_CARD":
                        wealth_counts["贴贴卡"] += balance

                # 打印结果
                account_log = (
                    f"账号：{self.mobile}\n"
                    f"干饭圣体有 {wealth_counts['干饭圣体']} 个\n"
                    f"心如止水有 {wealth_counts['心如止水']} 个\n"
                    f"都顶得住有 {wealth_counts['都顶得住']} 个\n"
                    f"坐以待币有 {wealth_counts['坐以待币']} 个\n"
                    f"成功人士有 {wealth_counts['成功人士']} 个\n"
                    f"贴贴卡 {wealth_counts['贴贴卡']} \n"
                )
                Log(account_log)
                self.all_logs.append(account_log)

                # if wealth_counts["幸运值"] == 10:
                #     lucky_message = f"{self.mobile} 当前幸运值已满，请尽快抽奖！"
                #     Log(lucky_message)
                #     self.all_logs.append(lucky_message)  # 添加幸运值满额提示
            else:
                error_log = f"账号：{self.mobile} 查询失败或数据为空"
                Log(error_log)
                self.all_logs.append(error_log)
        except Exception as e:
            import traceback
            Log(f"查询32周年庆卡状态时出现异常: {e}\n{traceback.format_exc()}")
            
    def DRAGONBOAT_2025_win(self, level):
        """
        闯关逻辑，从指定关卡开始闯到最后一关（第 15 关）。
        """
        try:
            for i in range(level, 16):  # 遍历关卡，从当前关卡到第 15 关（包含第 15 关）
                Log(f"> {self.mobile} 正在开始第【{i}】关...")
                payload = {"levelIndex": i}
                url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~yearEnd2024GameService~win"

                # 发起请求
                response = self.do_request(url, payload)

                if response.get('success'):
                    obj = response.get('obj', {})
                    current_award_list = obj.get('currentAwardList', [])

                    # 打印奖励信息
                    if current_award_list:
                        for award in current_award_list:
                            currency = award.get('currency', '未知奖励')
                            amount = award.get('amount', 0)

                            # 根据 currency 提示对应财神
                            if currency == "EAST_WEALTH":
                                Log(f">{self.mobile} 第【{i}】关成功，获得奖励：【东路财神】x{amount}")
                            elif currency == "LOVE_SIGN":
                                Log(f">{self.mobile} 第【{i}】关成功，获得奖励：【北路财神】x{amount}")
                            elif currency == "MIDDLE_WEALTH":
                                Log(f">{self.mobile} 第【{i}】关成功，获得奖励：【中路财神】x{amount}")
                            elif currency == "WEALTH_CHANCE":
                                Log(f">{self.mobile} 第【{i}】关成功，获得奖励：【西路财神】x{amount}")
                            elif currency == "SOUTH_WEALTH":
                                Log(f">{self.mobile} 第【{i}】关成功，获得奖励：【南路财神】x{amount}")
                            else:
                                Log(f">{self.mobile} 第【{i}】关成功，获得奖励：【{currency}】x{amount}")
                    else:
                        Log(f"> {self.mobile} 第【{i}】关成功，无奖励")

                    # 检查是否是最后一关
                    next_level_index = obj.get('nextLevelIndex', None)
                    if next_level_index is None or next_level_index > 15:
                        Log(f"> {self.mobile} 恭喜完成所有关卡！")
                        break

                else:
                    # 如果请求失败，打印错误信息
                    error_message = response.get('errorMessage', '无返回')
                    Log(f"> {self.mobile} 第【{i}】关失败，错误信息：【{error_message}】")
                    if '没有资格参与活动' in error_message:
                        self.DRAGONBOAT_2024_black = True
                        Log(f"> {self.mobile} 检测到会员日任务风控，停止操作")
                    break  # 停止闯关
                time.sleep(3)  # 等待 3 秒避免触发风控
        except Exception as e:
            import traceback
            Log(f"{self.mobile} 闯关时出现异常：{e}\n{traceback.format_exc()}")
            
    def DRAGONBOAT_2025_finishTask(self, taskCode, taskName):
        """
        完成指定任务
        """
        try:
            payload = {"taskCode": taskCode}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberEs~taskRecord~finishTask'

            # 发起请求
            response = self.do_request(url, payload)
            Log(f"完成任务接口响应: {response}")

            # 验证响应是否成功
            if isinstance(response, dict) and response.get('success'):
                obj = response.get('obj', None)
                if obj is True:  # 特殊情况：obj 为 True，任务完成成功但无额外数据
                    Log(f"> {taskName}-已完成")
                    return True
                elif obj is False:  # 特殊情况：obj 为 False
                    Log(f"> {taskName}-未完成，失败原因：返回的 obj 为 False，任务可能无效或已完成")
                    return False
                elif isinstance(obj, dict):  # obj 是字典，正常处理
                    data = obj.get('data', [])
                    Log(f"> {taskName}-已完成，返回数据：{data}")
                    return True
                else:  # obj 类型未知
                    Log(f"> {taskName}-未完成，失败原因：返回的 obj 类型未知，实际为: {obj}")
                    return False
            else:
                error_message = response.get('errorMessage', '无返回') if isinstance(response, dict) else '未知错误'
                Log(f"> {taskName}-未完成，失败原因：{error_message}")
                return False
        except Exception as e:
            import traceback
            Log(f"{taskName}-未完成，任务代码：【{taskCode}】，异常信息：{e}\n{traceback.format_exc()}")
            return False

    def main(self):
        global one_msg
        wait_time = random.randint(1000, 3000) / 1000.0  
        time.sleep(wait_time)  
        one_msg = ''
        if not self.login_res: return False
        
        print('\n' + '='*30 + '🚚 顺丰速运 开始执行 🚚' + '='*30 + '\n')
        
        # 执行签到任务
        self.sign()
        self.superWelfare_receiveRedPacket()
        self.get_SignTaskList()
        self.get_SignTaskList(True)

        # 执行丰蜜任务
        self.get_honeyTaskListStart()
        self.honey_indexData()
        self.honey_indexData(True)

        # 执行32周年庆任务
        self.znq2025()
        time.sleep(5)
        self.cxcs()
        self.index2025()
        activity_end_date = get_quarter_end_date()
        days_left = (activity_end_date - datetime.now()).days
        if days_left == 0:
            message = "今天采蜜活动截止兑换就剩最后0天了，请及时进行兑换"
            Log(message)
        else:
            message = f"今天采蜜活动截止兑换还有{days_left}天，请及时进行兑换"
            Log(message)
        target_time = datetime(2025, 4, 8, 19, 0)
        if datetime.now() < target_time:
            self.EAR_END_2023_TaskList()
            #self.anniversary2024_task()
        else:
            print('🎭 周年庆活动已结束')

        current_date = datetime.now().day
        if 26 <= current_date <= 28:
            self.member_day_index()
        else:
            print('⏰ 未到指定时间不执行会员日任务')
        
        print('\n' + '='*30 + '🚚 顺丰速运 执行完毕 🚚' + '='*30 + '\n')
        
        self.sendMsg()
        return True

    def sendMsg(self, help=False):
          #send("顺丰-通知", one_msg)
          pass

def get_quarter_end_date():
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year

    # 计算下个季度的第一天
    next_quarter_first_day = datetime(current_year, ((current_month - 1) // 3 + 1) * 3 + 1, 1)

    # 计算当前季度的最后一天
    quarter_end_date = next_quarter_first_day - timedelta(days=1)

    return quarter_end_date


def is_activity_end_date(end_date):
    current_date = datetime.now().date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    return current_date == end_date

if __name__ == '__main__':
    APP_NAME = '顺丰速运'
    ENV_NAME = 'sfsyUrl'
    CK_NAME = 'url'
    local_script_name = os.path.basename(__file__)
    local_version = '2025.01.06'
    token = os.getenv(ENV_NAME)
    # 将分隔符从\n改为&
    tokens = token.split('&')
    # print(tokens)
    if len(tokens) > 0:
        print(f"\n{'='*30} 🚚 共获取到{len(tokens)}个账号 🚚 {'='*30}\n")
        for index, infos in enumerate(tokens):
            run_result = RUN(infos, index).main()
            if not run_result: continue
