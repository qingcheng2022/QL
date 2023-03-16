#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------

from requests import get, post

class RsaPost:
    def __init__(self):
        self.key=""

    def init(self):
        self.msg = ""
        self.ua = f"Mozilla/5.0 (Linux; Android 10; SAMSUNG SM-N9600) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/19.1 Chrome/102.0.5005.125 Mobile Safari/537.36"
        self.headers = {
            "Host": "webapi.the-x.cn:8090",
            "Connection": "keep-alive",
            "Content-Length": '366',
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Signature": "fce4bad30d31a9fb255168027dcbe98302b0f11561f723f30242112eeffa1e3b",
            "X-Requested-With": "XMLHttpRequest",
            "ser-Agent": "Mozilla/5.0 (Linux; Android 10; SAMSUNG SM-N9600) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/19.1 Chrome/102.0.5005.125 Mobile Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://the-x.cn",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://the-x.cn/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        self.key = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+ugG5A8cZ3FqUKDwM57GM4io6\nJGcStivT8UdGt67PEOihLZTw3P7371+N47PrmsCpnTRzbTgcupKtUv8ImZalYk65\ndU8rjC/ridwhw9ffW2LBwvkEnDkkKKRi2liWIItDftJVBiWOh17o6gfbPoNrWORc\nAdcbpk2L+udld5kZNwIDAQAB\n-----END PUBLIC KEY-----"

    def req(self, url, method, data=None):
        if method == "GET":
            data = get(url, headers=self.headers).json()
            return data
        elif method.upper() == "POST":
            data = post(url, headers=self.headers, data=data).json()
            return data
        else:
            print("您当前使用的请求方式有误,请检查")

    # 获取任务列表
    def get_Auth(self,message):
        url = f"http://yun.tustbpf.top:8811/?codeToken={message}"
        msg = self.req(url, "GET")
        if(msg['code']==0):
            data=msg['auth']
        return data

    def main(self):
        self.init()
        self.get_Auth('21223')
        
if __name__ == "__main__":
    rsa=RsaPost()
    rsa.main()