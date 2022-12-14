#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : unknown
# @Time : 2022/11/1 11:21
# -------------------------------
#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : unknown
# @Time : 2022/8/23 13:05
# -------------------------------
#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : unknown
# @Time : 2022/10/24 22:09
# -------------------------------
# !/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : unknown
# @Time : 2022/8/22 18:13
# -------------------------------
# cron "11 * * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('zj电信养猫');
"""
1.环境变量说明:
    必须  TELECOM_PHONE : 电信手机号
    必须  TELECOM_PASSWORD : 电信服务密码 填写后会执行更多任务
"""
from os import environ, path as os_path
from re import findall
from time import sleep, time, mktime, strptime, strftime

account = environ.get("TELECOM_PHONE") if environ.get("TELECOM_PHONE") else ""
pwd = environ.get("TELECOM_PASSWORD") if environ.get("TELECOM_PASSWORD") else ""
if account == "" or pwd == "":
    print("请填写电信账号密码")
    # exit(0)
"""
aes加密解密工具 目前仅支持ECB/CBC 块长度均为128位 padding只支持pkcs7/zero_padding(aes中没有pkcs5 能用的pkcs5其实是执行的pkcs7) 后续有需要再加
pycryptdemo限制 同一个aes加密对象不能即加密又解密 所以当加密和解密都需要执行时 需要重新new一个对象增加额外开销
 -- A cipher object is stateful: once you have encrypted a message , you cannot encrypt (or decrypt) another message using the same object.　
"""
from Crypto.Cipher import AES, DES, DES3
from binascii import b2a_hex, a2b_hex
from base64 import b64encode, b64decode


class Crypt:
    def __init__(self, crypt_type: str, key, iv=None, mode="ECB"):
        """

        :param crypt_type: 对称加密类型 支持AES, DES, DES3
        :param key: 密钥 (aes可选 16/32(24位暂不支持 以后遇到有需要再补)  des 固定为8 des3 24(暂不支持16 16应该也不会再使用了) 一般都为24 分为8长度的三组 进行三次des加密
        :param iv: 偏移量
        :param mode: 模式 CBC/ECB
        """
        if crypt_type.upper() not in ["AES", "DES", "DES3"]:
            raise Exception("加密类型错误, 请重新选择 AES/DES/DES3")
        self.crypt_type = AES if crypt_type.upper() == "AES" else DES if crypt_type.upper() == "DES" else DES3
        self.block_size = self.crypt_type.block_size
        if self.crypt_type == DES:
            self.key_size = self.crypt_type.key_size
        elif self.crypt_type == DES3:
            self.key_size = self.crypt_type.key_size[1]
        else:
            if len(key) <= 16:
                self.key_size = self.crypt_type.key_size[0]
            elif len(key) > 24:
                self.key_size = self.crypt_type.key_size[2]
            else:
                self.key_size = self.crypt_type.key_size[1]
                print("当前aes密钥的长度只填充到24 若需要32 请手动用 chr(0) 填充")
        if len(key) > self.key_size:
            key = key[:self.key_size]
        else:
            if len(key) % self.key_size != 0:
                key = key + (self.key_size - len(key) % self.key_size) * chr(0)
        self.key = key.encode("utf-8")
        if mode == "ECB":
            self.mode = self.crypt_type.MODE_ECB
        elif mode == "CBC":
            self.mode = self.crypt_type.MODE_CBC
        else:
            raise Exception("您选择的加密模式错误")
        if iv is None:
            self.cipher = self.crypt_type.new(self.key, self.mode)
        else:
            if isinstance(iv, str):
                iv = iv[:self.block_size]
                self.cipher = self.crypt_type.new(self.key, self.mode, iv.encode("utf-8"))
            elif isinstance(iv, bytes):
                iv = iv[:self.block_size]
                self.cipher = self.crypt_type.new(self.key, self.mode, iv)
            else:
                raise Exception("偏移量不为字符串")

    def encrypt(self, data, padding="pkcs7", b64=False):
        """

        :param data: 目前暂不支持bytes 只支持string 有需求再补
        :param padding: pkcs7/pkck5 zero
        :param b64: 若需要得到base64的密文 则为True
        :return:
        """
        pkcs7_padding = lambda s: s + (self.block_size - len(s.encode()) % self.block_size) * chr(
            self.block_size - len(s.encode()) % self.block_size)
        zero_padding = lambda s: s + (self.block_size - len(s) % self.block_size) * chr(0)
        pad = pkcs7_padding if padding == "pkcs7" else zero_padding
        data = self.cipher.encrypt(pad(data).encode("utf8"))
        encrypt_data = b64encode(data) if b64 else b2a_hex(data)  # 输出hex或者base64
        return encrypt_data.decode('utf8')

    def decrypt(self, data, b64=False):
        """
        对称加密的解密
        :param data: 支持bytes base64 hex list 未做填充 密文应该都是数据块的倍数 带有需求再补
        :param b64: 若传入的data为base64格式 则为True
        :return:
        """
        if isinstance(data, list):
            data = bytes(data)
        if not isinstance(data, bytes):
            data = b64decode(data) if b64 else a2b_hex(data)
        decrypt_data = self.cipher.decrypt(data).decode()
        # 去掉padding
        # pkcs7_unpadding = lambda s: s.replace(s[-1], "")
        # zero_unpadding = lambda s: s.replace(chr(0), "")
        # unpadding = pkcs7_unpadding if padding=="pkcs7" else zero_unpadding
        unpadding = lambda s: s.replace(s[-1], "")
        return unpadding(decrypt_data)

from Crypto.PublicKey.RSA import importKey, construct
from Crypto.Cipher import PKCS1_v1_5
from base64 import b64encode


class RSA_Encrypt:
    def __init__(self, key):
        if isinstance(key, str):
            # 若提供的rsa公钥不为pem格式 则先将hex转化为pem格式
            # self.key = bytes.fromhex(key) if "PUBLIC KEY" not in key else key.encode()
            self.key = self.public_key(key) if "PUBLIC KEY" not in key else key.encode()
        else:
            print("提供的公钥格式不正确")

    def public_key(self, rsaExponent, rsaModulus=10001):
        e = int(rsaExponent, 16)
        n = int(rsaModulus, 16)  # snipped for brevity
        pubkey = construct((n, e)).export_key()
        return pubkey

    def encrypt(self, data, b64=False):
        pub_key = importKey(self.key)
        cipher = PKCS1_v1_5.new(pub_key)
        rsa_text = cipher.encrypt(data.encode("utf8"))
        rsa_text = b64encode(rsa_text).decode() if b64 else rsa_text.hex()
        return rsa_text
"""
营业厅登录获取token loginAuthCipherAsymmertric参数解密参考自 github@QGCliveDavis https://github.com/QGCliveDavis 感谢大佬
"""
from requests import post
from datetime import datetime
from xml.etree.ElementTree import XML
from uuid import uuid4
from sys import path
from json import dumps, dump, load


class TelecomLogin:
    def __init__(self, account, pwd):
        self.account = account
        self.pwd = pwd
        self.deviceUid = uuid4().hex
    def login(self):
        url = "https://appgologin.189.cn:9031/login/client/userLoginNormal"
        timestamp = datetime.now().__format__("%Y%m%d%H%M%S")
        key = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofd\nWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18\nqFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMi\nPMpq0/XKBO8lYhN/gwIDAQAB\n-----END PUBLIC KEY-----"
        body = {
            "headerInfos": {
                "code": "userLoginNormal",
                "timestamp": timestamp,
                "broadAccount": "",
                "broadToken": "",
                "clientType": "#9.6.1#channel50#iPhone 14 Pro Max#",
                "shopId": "20002",
                "source": "110003",
                "sourcePassword": "Sid98s",
                "token": "",
                "userLoginName": self.account
            },
            "content": {
                "attach": "test",
                "fieldData": {
                    "loginType": "4",
                    "accountType": "",
                    "loginAuthCipherAsymmertric": RSA_Encrypt(key).encrypt(f"iPhone 14 15.4.{self.deviceUid[:12]}{self.account}{timestamp}{self.pwd}0$$$0.", b64=True),
                    "deviceUid": self.deviceUid[:16],
                    "phoneNum": self.get_phoneNum(self.account),
                    "isChinatelecom": "0",
                    "systemVersion": "15.4.0",
                    "authentication": self.pwd
                }
            }
        }
        headers = {
            "user-agent": "iPhone 14 Pro Max/9.6.1",

        }

        data = post(url, headers=headers, json=body).json()
        print(data)
        code = data["responseData"]["resultCode"]
        if code != "0000":
            print("登陆失败, 接口日志" + str(data))
            return None
        self.token = data["responseData"]["data"]["loginSuccessResult"]["token"]
        self.userId = data["responseData"]["data"]["loginSuccessResult"]["userId"]
        userinfo = {"telecom_token": self.token, "telecom_userId": self.userId}
        with open("./zjdx.json", "w") as f:
            dump(userinfo, f)
        return True

    def get_ticket(self):
        url = "https://appgologin.189.cn:9031/map/clientXML"
        body = f"<Request>\n<HeaderInfos>\n		<Code>getSingle</Code>\n		<Timestamp>{datetime.now().__format__('%Y%m%d%H%M%S')}</Timestamp>\n		<BroadAccount></BroadAccount>\n		<BroadToken></BroadToken>\n		<ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType>\n		<ShopId>20002</ShopId>\n		<Source>110003</Source>\n		<SourcePassword>Sid98s</SourcePassword>\n		<Token>{self.token}</Token>\n		<UserLoginName>{self.account}</UserLoginName>\n	</HeaderInfos>\n	<Content>\n		<Attach>test</Attach>\n		<FieldData>\n			<TargetId>{self.encrypt_userid(self.userId)}</TargetId>\n			<Url>4a6862274835b451</Url>\n		</FieldData>\n	</Content>\n</Request>"
        headers = {
            "User-Agent": "samsung SM-G9750/9.4.0",
            "Content-Type": "text/xml; charset=utf-8",
            "Content-Length": "694",
            "Host": "appgologin.189.cn:9031",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        }
        xml_data = post(url, headers=headers, data=body).text
        print(xml_data)
        doc = XML(xml_data)
        secret_ticket = doc.find("ResponseData/Data/Ticket").text
        print("secret: " + secret_ticket)
        ticket = self.decrypt_ticket(secret_ticket)
        print("ticket: " + ticket)
        return ticket
    def main(self):
        if os_path.exists("./zjdx.json"):
            try:
                with open("./zjdx.json", "rb") as f:
                    userinfo = load(f)
                self.token = userinfo["telecom_token"]
                self.userId = userinfo["telecom_userId"]
            except:
                print(f"读取 zjdx.json 文件异常 请删除该文件后重新执行")
        else:
            if self.login() is None:
                return "10086"
        try:
            ticket = self.get_ticket()
        except:
            if self.login() is None:
                return "10086"
            ticket = self.get_ticket()
        return ticket
    @staticmethod
    def get_phoneNum(phone):
        result = ""
        for i in phone:
            result += chr(ord(i) + 2)
        return result
    @staticmethod
    def decrypt_ticket(secret_ticket):
        key = "1234567`90koiuyhgtfrdewsaqaqsqde"
        iv = "\0\0\0\0\0\0\0\0"
        # ticket = des3_cbc_decrypt(key, bytes(TelecomLogin.process_text(secret_ticket)), iv)
        ticket = Crypt("des3", key, iv, "CBC").decrypt(TelecomLogin.process_text(secret_ticket))
        return ticket
    @staticmethod
    def encrypt_userid(userid):
        key = "1234567`90koiuyhgtfrdewsaqaqsqde"
        iv = bytes([0] * 8)
        targetId = Crypt("des3", key, iv, "CBC").encrypt(userid)
        return targetId

    @staticmethod
    def process_text(text):
        length = len(text) >> 1
        bArr = [0] * length
        if len(text) % 2 == 0:
            i2 = 0
            i3 = 0
            while i2 < length:
                i4 = i3 + 1
                indexOf = "0123456789abcdef0123456789ABCDEF".find(text[i3])
                if indexOf != -1:
                    bArr[i2] = (((indexOf & 15) << 4) + ("0123456789abcdef0123456789ABCDEF".find(text[i4]) & 15))
                    i2 += 1
                    i3 = i4 + 1
                else:
                    print("转化失败 大概率是明文输入错误")
        return bArr
tg_userId = environ.get("TG_USER_ID")
tgbot_token = environ.get("TG_BOT_TOKEN")
tg_push_api = environ.get("TG_API_HOST")
pushplus_token = environ.get("PUSH_PLUS_TOKEN")

def tgpush(title, content):
    url = f"https://api.telegram.org/bot{tgbot_token}/sendMessage"
    if tg_push_api != "":
        url = f"https://{tg_push_api}/bot{tgbot_token}/sendMessage"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'chat_id': str(tg_userId), 'text': f"{title}\n{content}", 'disable_web_page_preview': 'true'}
    try:
        post(url, headers=headers, data=data, timeout=10)
    except:
        print('推送失败')
def pushplus(title, content):
    url = "http://www.pushplus.plus/send"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "token": pushplus_token,
        "title": title,
        "content": content
    }
    try:
        post(url, headers=headers, data=dumps(data))
    except:
        print('推送失败')
def push(title, content):
    if pushplus_token != "" and pushplus_token != "no":
        pushplus(title, content)
    if tgbot_token != "" and tgbot_token != "no" and tg_userId != "":
        tgpush(title, content)
from requests import Session
class ZJDX:
    def __init__(self):
        self.session = Session()
    def getToken(self):
        url = "https://hdmf.k189.cn/actServ/userJoin/getToken"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
        }
        req = self.session.post(url, headers=headers)
        self.cookie = findall(r"HttpOnly, (.*?) ", req.headers["Set-Cookie"])[0]
        self.csrf_token = req.headers["csrf_token"]
    def loginByTicket(self, ticket):
        url = "https://hdmf.k189.cn/actServ/userJoin/loginByTicket"
        body = {"ticket":ticket,
                "channelId":"69",
                "posId":"2255-65089-69"}
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
            "access-Control-Allow-Origin": "*",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Length": "246",
            "Content-Type": "application/json;charset=UTF-8",
            "csrf_token": self.csrf_token,
            "Host": "hdmf.k189.cn",
            "Origin": "https://hdmf.k189.cn",
            "Pragma": "no-cache",
            "Referer": f"https://hdmf.k189.cn/signinHd/?aid=B906E608F3BDD49908F1176191A4260B&channelId=61&posId=2055-0-61&posName=81A71A7418D764B0D0BC8294E7027131&channelName=D23F21F5710593990D72A94F16F7D351&ticket={ticket}",
            "sec-ch-ua": "\"Chromium\";v=\"106\", \"Google Chrome\";v=\"106\", \"Not;A=Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        req = self.session.post(url, headers=headers, json=body)
        self.ticket = ticket
        # print(self.session.cookies)
        # print(self.csrf_token)
    def check_in(self):
        url = "https://hdmf.k189.cn/actServ/userActivity/querySignInData"
        body = {"aid":"6E4E000E04F48858480E1C7C3D3FAC88"}
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
            "access-Control-Allow-Origin": "*",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Length": "42",
            "Content-Type": "application/json;charset=UTF-8",
            "csrf_token": self.csrf_token,
            "Host": "hdmf.k189.cn",
            "Origin": "https://hdmf.k189.cn",
            "Pragma": "no-cache",
            "Referer": f"https://hdmf.k189.cn/signinHd/?aid=6E4E000E04F48858480E1C7C3D3FAC88&channelId=69&posId=2255-65089-69&posName=81A71A7418D764B0D0BC8294E7027131&channelName=D23F21F5710593990D72A94F16F7D351&ticket={self.ticket}",
            "sec-ch-ua": "\"Chromium\";v=\"106\", \"Google Chrome\";v=\"106\", \"Not;A=Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        self.session.post(url, headers=headers, json=body)
        # print(self.session.cookies)
        # print(self.csrf_token)
        url = "https://hdmf.k189.cn/actServ/userActivity/signIn"
        data = self.session.post(url, headers=headers, json=body).json()
        print(data)
        url = "https://hdmf.k189.cn/actServ/activityData/findPrizes"
        data = self.session.post(url, headers=headers, json=body).json()
        print(data)
        print("----------------")
        if data["code"] == 200:
            print(f"总计兑换{data['result']['awardsNum'][1]['value']}", f"累积获得{data['result']['awardsNum'][1]['value']}")
            push(f"浙江电信 - 天天签到领话费 - {data['result']['userPhone']}", f"累积获得{data['result']['awardsNum'][1]['value']}")
    def check_in1(self):
        url = "https://hdmf.k189.cn/actServ/userActivity/querySignInData"
        body = {"aid":"B906E608F3BDD49908F1176191A4260B"}
        # self.headers = {
        #     "Accept": "application/json, text/plain, */*",
        #     "Accept-Encoding": "gzip, deflate, br",
        #     "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
        #     "access-Control-Allow-Origin": "*",
        #     "Cache-Control": "no-cache",
        #     "Connection": "keep-alive",
        #     "Content-Length": "42",
        #     "Content-Type": "application/json;charset=UTF-8",
        #     "csrf_token": self.csrf_token,
        #     "Host": "hdmf.k189.cn",
        #     "Origin": "https://hdmf.k189.cn",
        #     "Pragma": "no-cache",
        #     "Referer": f"https://hdmf.k189.cn/acquireHd/?aid=B906E608F3BDD49908F1176191A4260B&channelId=61&posId=2055-0-61&posName=6BA7AD4FF25C0E4ECB07BF12E9EA4FEC3EA6416930B5BDB8B7DCA5BC2BCC8DA1&channelName=830156D1FE75A8D582A4B8170D42B295&channel=2055-0-61&ticket={self.ticket}",
        #     "sec-ch-ua": "\"Chromium\";v=\"106\", \"Google Chrome\";v=\"106\", \"Not;A=Brand\";v=\"99\"",
        #     "sec-ch-ua-mobile": "?0",
        #     "sec-ch-ua-platform": "\"Windows\"",
        #     "Sec-Fetch-Dest": "empty",
        #     "Sec-Fetch-Mode": "cors",
        #     "Sec-Fetch-Site": "same-origin",
        #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
        #     "X-Requested-With": "XMLHttpRequest"
        # }
        print(self.session.post(url, headers=self.headers, json=body).json())
        # print(self.session.cookies)
        # print(self.csrf_token)
        url = "https://hdmf.k189.cn/actServ/userActivity/signIn"
        data = self.session.post(url, headers=self.headers, json=body).json()
        print(data)
    def finish_task(self, taskcode):
        url1 = "https://wapzj.189.cn/zhuanti/hdmf/ActivityHDMF/sendRwPrize.whtml"
        body = f"activity_id=HDMF1970&taskCode={taskcode}&channelId=61&posCode=2055-0-61"
        # cookie = "cityCode=zj; JSESSIONID=940E7946BC83AC8CC3F4EB9A6209FAEB.node1; WT_SS=1668866493827new; X-LB=2.38a.617587e6.1f90;"
        # cookie += ""
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Length": "0",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "wapzj.189.cn",
            "Origin": "https://wapzj.189.cn",
            "Pragma": "no-cache",
            # "Cookie": cookie,
            "Referer": "https://wapzj.189.cn/mall/5zyphj/?channel=raisegame&cmpid=nom-kf-zj-wapyewu-zt-raisegame-5zyphj",
            "sec-ch-ua": "\"Google Chrome\";v=\"107\", \"Chromium\";v=\"107\", \"Not=A?Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        url = "https://wapzj.189.cn/zhuanti/hdmf/utils/ParamsUtils/getParams.whtml"
        print(self.session.post(url, headers=headers).json())
        print(self.session.post(url1, headers=headers, data=body).json())
    def share(self):
        url = "https://hdmf.k189.cn/actServ/task/doTask"
        body = {"taskId":"1657702935631","aid":"B906E608F3BDD49908F1176191A4260B"}
        data = post(url, headers=self.headers, json=body).json()
        print(data)

    def task_login(self, taskcode):
        url = "https://hdmf.k189.cn/actServ/userJoin/loginToWangTingNew"
        body = {"aid":"B906E608F3BDD49908F1176191A4260B","channel":"2055-0-61","posCode":"2055-0-61","posName":"6BA7AD4FF25C0E4ECB07BF12E9EA4FEC3EA6416930B5BDB8B7DCA5BC2BCC8DA1","channelName":"830156D1FE75A8D582A4B8170D42B295","url":"mall/zhuantixskddts/?channel=raisegame","hdmf_url":f"https://hdmf.k189.cn/acquireHd/?aid=B906E608F3BDD49908F1176191A4260B&channelId=61&posId=2055-0-61&posName=6BA7AD4FF25C0E4ECB07BF12E9EA4FEC3EA6416930B5BDB8B7DCA5BC2BCC8DA1&channelName=830156D1FE75A8D582A4B8170D42B295&channel=2055-0-61&ticket={self.ticket}&secInfo=B7AFDEBFED54CCCC96856D5ECBB7BBB6","channelId":"61","task_code":taskcode,"timer":"15"}
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
            "access-Control-Allow-Origin": "*",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Length": "805",
            "Content-Type": "application/json;charset=UTF-8",
            "csrf_token": self.csrf_token,
            "Host": "hdmf.k189.cn",
            "Origin": "https://hdmf.k189.cn",
            "Pragma": "no-cache",
            "Referer": "https://hdmf.k189.cn/acquireHd/?aid=B906E608F3BDD49908F1176191A4260B&channelId=61&posId=2055-0-61&posName=6BA7AD4FF25C0E4ECB07BF12E9EA4FEC3EA6416930B5BDB8B7DCA5BC2BCC8DA1&channelName=830156D1FE75A8D582A4B8170D42B295&channel=2055-0-61&ticket=8b2fac983c75e228e6aa00989fd59980bf9c821217d28511f05a47f33926bcc4d853d31f34668cb8d205bded08058e1b2d47ce19d4b0c44af879745b77967c083f654425de2ce27e06bfb03c2bd34fc5f53077045c23dcd22c3b4fa03cbf8951&secInfo=B7AFDEBFED54CCCC96856D5ECBB7BBB6",
            "sec-ch-ua": "\"Google Chrome\";v=\"107\", \"Chromium\";v=\"107\", \"Not=A?Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        url = self.session.post(url, headers=headers, json=body).json()["result"]
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Host": "wapzj.189.cn",
            "Pragma": "no-cache",
            "Referer": "https://hdmf.k189.cn/",
            "sec-ch-ua": "\"Google Chrome\";v=\"107\", \"Chromium\";v=\"107\", \"Not=A?Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
        }
        req = self.session.get(url, headers=headers)

    def food(self):
        url1 = "https://hdmf.k189.cn/actServ/task/rTaskTime"
        url = "https://hdmf.k189.cn/actServ/task/bgTimeTask"
        body = {"taskId": "1657682963913", "aid": "B906E608F3BDD49908F1176191A4260B"}
        self.headers = {"Accept": "application/json, text/plain, */*", "Accept-Encoding": "gzip, deflate, br",
                        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7", "access-Control-Allow-Origin": "*",
                        "Cache-Control": "no-cache", "Connection": "keep-alive", "Content-Length": "42",
                        "Content-Type": "application/json;charset=UTF-8", "csrf_token": self.csrf_token,
                        "Host": "hdmf.k189.cn", "Origin": "https://hdmf.k189.cn", "Pragma": "no-cache",
                        "Referer": f"https://hdmf.k189.cn/acquireHd/?aid=B906E608F3BDD49908F1176191A4260B&channelId=61&posId=2055-0-61&posName=6BA7AD4FF25C0E4ECB07BF12E9EA4FEC3EA6416930B5BDB8B7DCA5BC2BCC8DA1&channelName=830156D1FE75A8D582A4B8170D42B295&channel=2055-0-61&ticket={self.ticket}",
                        "sec-ch-ua": "\"Chromium\";v=\"106\", \"Google Chrome\";v=\"106\", \"Not;A=Brand\";v=\"99\"",
                        "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": "\"Windows\"", "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
                        "X-Requested-With": "XMLHttpRequest", "Cookie": self.cookie}
        data = post(url1, headers=self.headers, json=body).json()
        try:
            left_time = int(mktime(strptime(data["result"]["time"], "%Y-%m-%d %H:%M:%S"))) - int(round(time())) + (
                    9 - int(strftime("%z")[2])) * 3600
            if 0 < left_time <= 300:
                print(f"等待{left_time + 5}秒后喂食")
                sleep(left_time + 5)
            elif left_time > 300:
                print("距离本次喂食完成剩余时间大于五分钟 本次不喂食")
                return
        except:
            data = post(url, headers=self.headers, json=body).json()
            print(data)
    def get_findPrizes(self):
        url = "https://hdmf.k189.cn/actServ/activityData/findPrizes"
        body = {"aid": "B906E608F3BDD49908F1176191A4260B"}
        data = self.session.post(url, headers=self.headers, json=body).json()
        print(data)
        if data["code"] == 200:
            #score = int(data['result']['awardsNum'][0]['value'])
            #print(score)
            # print(f"当前共有猫粮{str(score)}")
            return data
        return 0
            # push("浙江电信", f"总计兑换{data['result']['awardsNum'][0]['value']}")
    def exchange(self):
        url = "https://hdmf.k189.cn/actServ/userActivity/exchangePrizes"
        awardIdList = ["8EDCAC7677F290D0F821D0EBE666A26D", "79C2FD1B12135C2F63FAEE603E52E2A3"]
        for awardId in awardIdList:
            body = {"awardId":awardId,"aid":"4BB166928C96907BE9A485AD2FB58ABF"}
            data = post(url, headers=self.headers, json=body).json()
            print(data)
            sleep(10)
    def lotter(self):
        url = "https://hdmf.k189.cn/actServ/userActivity/instantLottery"
        body = {"authorizerAppid":"null","aid":"A18C6B5B1F70A9CC6983581D10ABC74C"}
        data = post(url, headers=self.headers, json=body).json()
        print(data)
        findPrizes = self.get_findPrizes()
        push(f"浙江电信 - 云养猫小窝 - {findPrizes['result']['userPhone']}", f"{data['result']['massage']}")
    def main(self):
        self.getToken()
        self.loginByTicket(TelecomLogin(account, pwd).main())
        self.food()
        if datetime.now().hour == 9:
            self.check_in()
            self.check_in1()
            if datetime.now().day == 1:
                self.exchange()
            taskcode_list = ["1657702206332", "1657683473029"]  # 1657702206332 体验服务 1次  1657683473029 旅行 5次
            for taskcode in taskcode_list:
                finish_num = 1 if taskcode == "1657702206332" else 5
                for i in range(finish_num):
                    zjdx.task_login(taskcode)
                    zjdx.finish_task(taskcode)
                    sleep(15)
                zjdx.share()
        findPrizes = self.get_findPrizes()
        if findPrizes['result']['awardsNum'][0]['value'] >= 99:
            print(f"当前猫粮大于100 抽奖")
            self.lotter()

if __name__ == '__main__':
    zjdx = ZJDX()
    zjdx.main()
