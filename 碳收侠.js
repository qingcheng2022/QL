/*

cron: 12 12,14,18,20 * * *


抓碳收侠admin.tanshouxia.com 小程序请求头authorization的值 多账号&或换行 定时如上
⚠️【免责声明】
------------------------------------------
1、此脚本仅用于学习研究，不保证其合法性、准确性、有效性，请根据情况自行判断，本人对此不承担任何保证责任。
2、由于此脚本仅用于学习研究，您必须在下载后 24 小时内将所有内容从您的计算机或手机或任何存储设备中完全删除，若违反规定引起任何事件本人对此均不负责。
3、请勿将此脚本用于任何商业或非法目的，若违反规定请自行对此负责。
4、此脚本涉及应用与本人无关，本人对因此引起的任何隐私泄漏或其他后果不承担任何责任。
5、本人对任何脚本引发的问题概不负责，包括但不限于由脚本错误引起的任何损失和损害。
6、如果任何单位或个人认为此脚本可能涉嫌侵犯其权利，应及时通知并提供身份证明，所有权证明，我们将在收到认证文件确认后删除此脚本。
7、所有直接或间接使用、查看此脚本的人均应该仔细阅读此声明。本人保留随时更改或补充此声明的权利。一旦您使用或复制了此脚本，即视为您已接受此免责声明。
*/

const $ = new Env("碳收侠");
let ckName = `tanshouxia`;
const strSplitor = "#";
const envSplitor = ["&", "\n"];
const notify = $.isNode() ? require("./sendNotify") : "";
const axios = require("axios");
const defaultUserAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.31(0x18001e31) NetType/WIFI Language/zh_CN miniProgram"
const appid = "wx14c173b908e54313"
const wxcenter = process.env.wxcenter || ""

class Public {
    async request(options) {
        return await axios.request(options);
    }
}
class Task extends Public {
    constructor(env) {

        super();
        this.index = $.userIdx++
        let user = env.split("#");
        this.wxid = env
        this.name = ''
        this.token = env
    }
    async getcode() {
        let options = {
            url: `${wxcenter}/api/Wxapp/JSLogin`,
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST',
            data: { "Wxid": "" + this.wxid, "Appid": "" + appid }
        }
        let { data: result } = await this.request(options);
        if (result.Success) {
            let code = result.Data.code
            $.log(`账号[${this.index}]【${this.name}】 获取code成功[${code}]`);
            return code
        } else {
            console.log(result);
        }


    }
    async getphonecode() {
        let options = {
            url: `${wxcenter}/api/Wxapp/GetAllMobile`,
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST',
            data: { "Wxid": "" + this.wxid, "Appid": "" + appid, "Data": "string", "Opt": 0, }
        }
        let { data: result } = await this.request(options);
        if (result.Success) {
            let appidCode = await this.getcode()
            let params = result.Data.Data
            params = JSON.parse(params)
            let { encryptedData, iv, data: phonecode } = params['custom_phone_list'][0]
            phonecode = JSON.parse(phonecode)
            phonecode = phonecode?.code
            if (encryptedData && iv && phonecode && appidCode) {
                await this.login(encryptedData, iv, phonecode, appidCode)
            } else {
                $.log(`账号[${this.index}]【${this.name}】 获取手机号失败`);
            }
        } else {
            console.log(result);
        }


    }
    async login(encryptedData, iv, phonecode, appidCode) {

        /*let options = {
            method: "POST",
            url: "https://admin.tanshouxia.com/api/getWxSessionKey",
            headers: {
                "accept-language": "zh-CN,zh;q=0.9",
                "authtoken": "",
                "content-type": "application/x-www-form-urlencoded",
                "reqdeviceid": "mini",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "sessionid": "",
                "token": "",
                "xweb_xhr": "1",
                "referrer": "https://servicewechat.com/wx14c173b908e54313/84/page-frame.html",
            },
            data: `code=${code}&js_code=${code}&act=getrundata&token=&reqDeviceId=mini`
        }*/
        let data = {
            'code': appidCode,
            'phone_code': phonecode,
            'encryptedData': encryptedData,
            'iv': iv,
            'yaoqingma': '37942446278',
            'token': '',
            'reqDeviceId': 'mini'
        }

        let options = {
            method: 'POST',
            url: 'https://admin.tanshouxia.com/api/wechat_phone_login',
            headers: {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; MI 8 Lite Build/QKQ1.190910.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.103 Mobile Safari/537.36 XWEB/1300473 MMWEBSDK/20240404 MMWEBID/8150 MicroMessenger/8.0.49.2600(0x2800315A) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android',
                'Accept-Encoding': 'gzip,compress,br,deflate',
                'Content-Type': 'application/x-www-form-urlencoded',
                'charset': 'utf-8',
                'authtoken': '[object Undefined]',
                'sessionid': '[object Undefined]',
                'reqdeviceid': 'mini',
                'Referer': 'https://servicewechat.com/wx14c173b908e54313/84/page-frame.html'
            },
            data: data
        };
        let { data: result } = await this.request(options);
        if (result.code == 1) {
            $.log(`账号[${this.index}]【${this.name}】 登录成功`);
            this.token = result.data.user.token

        } else {
            $.log(`账号[${this.index}]【${this.name}】 登录失败`);
        }
    }
    async getPik() {
        let options = {
            method: "GET",
            url: `https://admin.tanshouxia.com/api2/getPick`,
            headers: {
                "accept": "text/json",
                "accept-language": "zh-CN,zh;q=0.9",
                "authorization": "" + this.token,
                "content-type": "application/json;charset=UTF-8",
                "reqdeviceid": "mini",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "xweb_xhr": "1",
                "referrer": "https://servicewechat.com/wx14c173b908e54313/84/page-frame.html"
            }


        }
        let { data: res } = await this.request(options);

        if (res?.code == 1) {
            for (let i of res.data) {
                let pikId = i.id
                let pikAnhao = i.text3
                let pikStatus = i.shifouyiling
                let receiveTime = i.receiveTime
                if (receiveTime == 0) {

                    await $.wait(Math.floor(Math.random() * (30 - 15 + 1) + 15) * 1000)
                    await this.setPik(pikId, pikAnhao)
                }
            }
        }
    }
    async getCategoryGameData(type) {
        //每轮游戏4次 40分 一共280分 + 暗号120分
        //垃圾分类游戏

        let path = ''
        if (type == 2) {
            path = 'getCategoryGameData'
        }
        if (type == 3) {
            path = 'getDatiGameData'
        }
        if (type == 4) {
            path = 'getCarGameData'
        }
        if (type == 5) {
            path = 'getDatiGameKuaiDa'
        }
        if (type == 6) {
            path = 'getAssemblyLine'
        }
        if (type == 7) {
            path = 'getDatiGameKuaiDa'
        }
        if (type == 8) {
            path = 'getLianLianKan'
        }
        let options = {
            method: "GET",
            url: `https://admin.tanshouxia.com/api2/${path}?type=${type}&token=${this.token}&reqDeviceId=mini`,
            headers: {
                "accept": "*/*",
                "accept-language": "zh-CN,zh;q=0.9",
                //"authtoken": "",
                "content-type": "application/x-www-form-urlencoded",
                "reqdeviceid": "mini",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "sessionid": "",
                "token": "" + this.token,
                "xweb_xhr": "1",
            }
        }
        let { data: res } = await this.request(options);

        if (res?.code == 1) {
            let level = res.data.level
            //15-30s 随机
            await $.wait(Math.floor(Math.random() * (30 - 15 + 1) + 15) * 1000)
            let data
            if (type == 2 || type == 4) {
                data = `type=${type}&token=${this.token}&reqDeviceId=mini`
            }
            if (type == 3) {
                data = `type=${type}&answer=5&incorrectly=0&token=${this.token}&reqDeviceId=mini`
            }
            if (type == 5) {
                data = `type=${type}&answer=10&incorrectly=0&token=${this.token}&reqDeviceId=mini`
            }
            if (type == 6) {
                data = `type=${type}&fraction=100&answer=20&incorrectly=0&token=${this.token}&reqDeviceId=mini`
            }
            if (type == 7) {
                data = `type=${type}&answer=0&incorrectly=0&token=${this.token}&reqDeviceId=mini`
            }
            if (type == 8) {
                data = `type=${type}&token=${this.token}&reqDeviceId=mini`
            }

            await this.gamePointsReward(data)

            await this.updataCetCategoryGameData(type, level + 1)



        }
    }
    async updataCetCategoryGameData(type, level) {
        let options = {
            method: "POST",
            url: `https://admin.tanshouxia.com/api2/updataCetCategoryGameData`,
            headers: {
                "accept": "text/json",
                "accept-language": "zh-CN,zh;q=0.9",
                "authorization": "" + this.token,
                "content-type": "application/x-www-form-urlencoded",
                "reqdeviceid": "mini",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "xweb_xhr": "1",
                "referrer": "https://servicewechat.com/wx14c173b908e54313/84/page-frame.html"
            },
            data: `type=${type}&level=${level}&token=${this.token}&reqDeviceId=mini`

        }
        let { data: res } = await this.request(options);
        if (res?.code == 1) {
            $.log(`账号[${this.index}]【${this.name}】 垃圾分类游戏成功`);
        }
    }
    async gamePointsReward(data) {
        let options = {
            method: "POST",
            url: `https://admin.tanshouxia.com/api2/gamePointsReward`,
            headers: {
                "accept": "text/json",
                "accept-language": "zh-CN,zh;q=0.9",
                "authorization": "" + this.token,
                "content-type": "application/x-www-form-urlencoded",
                "reqdeviceid": "mini",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "xweb_xhr": "1",
                "referrer": "https://servicewechat.com/wx14c173b908e54313/84/page-frame.html"
            },
            data: data

        }
        let { data: res } = await this.request(options);
        if (res?.code == 1) {
            $.log(`账号[${this.index}]【${this.name}】 垃圾分类游戏奖励领取成功`);
        }
    }
    async setPik(id, anhao) {
        let options = {
            method: "POST",
            url: `https://admin.tanshouxia.com/api2/setPick`,
            headers: {
                "accept": "text/json",
                "accept-language": "zh-CN,zh;q=0.9",
                "authorization": "" + this.token,
                "content-type": "application/json;charset=UTF-8",
                "reqdeviceid": "mini",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "xweb_xhr": "1",
                "referrer": "https://servicewechat.com/wx14c173b908e54313/84/page-frame.html"
            },
            data: { id: id, anhao: anhao }

        }
        let { data: res } = await this.request(options);
        if (res?.code == 1) {
            $.log(`账号[${this.index}]【${this.name}】 答暗号成功`);
        }
        return res
    }
    async userInfo() {

        let options = {
            method: "GET",
            url: `https://admin.tanshouxia.com/api/getUser?token=${this.token}&reqDeviceId=mini`,
            headers: {
                "accept": "*/*",
                "accept-language": "zh-CN,zh;q=0.9",
                "authtoken": "401bmRq6D+iIhCsPqqgRRThTwPRGChXFtY1isfFgz/B2Ywd343m+gL0",
                "content-type": "application/x-www-form-urlencoded",
                "reqdeviceid": "mini",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "sessionid": "",
                "token": "" + this.token,
                "xweb_xhr": "1",
                "referrer": "https://servicewechat.com/wx14c173b908e54313/84/page-frame.html",
            }
        }
        let { data: res } = await this.request(options);
        if (res?.code == 1) {
            this.name = res.data[0].name
            $.log(`账号[${this.index}] 积分[${res.data[0].jifen}] [${res.data[0].name}] [${res.data[0].mr_phone}]`)
        }

    }
    async run() {
        //随机延迟5-10分钟
        let time = Math.floor(Math.random() * 5 + 5) * 60000
        $.log(`账号[${this.index}] 随机延迟${time / 60000}分钟`);
        await $.wait(time * 60000)
        await this.userInfo()
        await this.getPik()
        for (let i of [2, 3, 4, 5, 6, 7, 8]) {
            await this.getCategoryGameData(i)
            for (let j = 0; j < 3; j++) {
                await $.wait(5000)
                //await this.getCategoryGameData(i)
            }
        }
    }
}


!(async () => {
    await getNotice()
    $.checkEnv(ckName);

    for (let user of $.userList) {
        //

        await new Task(user).run();

    }


})()
    .catch((e) => console.log(e))
    .finally(() => $.done());

async function getNotice() {
    let options = {
        url: `https://ghproxy.net/https://raw.githubusercontent.com/smallfawn/Note/refs/heads/main/Notice.json`,
        headers: {
            "User-Agent": defaultUserAgent,
        }
    }
    let { data: res } = await new Public().request(options);
    $.log(res)
    return res
}


// prettier-ignore
function Env(t, s) {
    return new (class {
        constructor(t, s) {
            this.userIdx = 1;
            this.userList = [];
            this.userCount = 0;
            this.name = t;
            this.notifyStr = [];
            this.logSeparator = "\n";
            this.startTime = new Date().getTime();
            Object.assign(this, s);
            this.log(`\ud83d\udd14${this.name},\u5f00\u59cb!`);
        }
        checkEnv(ckName) {
            let userCookie = (this.isNode() ? process.env[ckName] : "") || "";
            this.userList = userCookie.split(envSplitor.find((o) => userCookie.includes(o)) || "&").filter((n) => n);
            this.userCount = this.userList.length;
            this.log(`共找到${this.userCount}个账号`);
        }
        async sendMsg() {
            this.log("==============📣Center 通知📣==============")
            for (let i = 0; i < this.notifyStr.length; i++) {
                if (Object.prototype.toString.call(this.notifyStr[i]) === '[object Object]' ||
                    Object.prototype.toString.call(this.notifyStr[i]) === '[object Array]') {
                    this.notifyStr[i] = JSON.stringify(this.notifyStr[i]);
                }
            }
            let message = this.notifyStr.join(this.logSeparator);
            if (this.isNode()) {
                await notify.sendNotify(this.name, message);
            } else {
            }
        }
        isNode() {
            return "undefined" != typeof module && !!module.exports;
        }

        queryStr(options) {
            return Object.entries(options)
                .map(
                    ([key, value]) =>
                        `${key}=${typeof value === "object" ? JSON.stringify(value) : value
                        }`
                )
                .join("&");
        }
        getURLParams(url) {
            const params = {};
            const queryString = url.split("?")[1];
            if (queryString) {
                const paramPairs = queryString.split("&");
                paramPairs.forEach((pair) => {
                    const [key, value] = pair.split("=");
                    params[key] = value;
                });
            }
            return params;
        }
        isJSONString(str) {
            try {
                return JSON.parse(str) && typeof JSON.parse(str) === "object";
            } catch (e) {
                return false;
            }
        }
        isJson(obj) {
            var isjson =
                typeof obj == "object" &&
                Object.prototype.toString.call(obj).toLowerCase() ==
                "[object object]" &&
                !obj.length;
            return isjson;
        }

        randomNumber(length) {
            const characters = "0123456789";
            return Array.from(
                { length },
                () => characters[Math.floor(Math.random() * characters.length)]
            ).join("");
        }
        randomString(length) {
            const characters = "abcdefghijklmnopqrstuvwxyz0123456789";
            return Array.from(
                { length },
                () => characters[Math.floor(Math.random() * characters.length)]
            ).join("");
        }
        uuid() {
            return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(
                /[xy]/g,
                function (c) {
                    var r = (Math.random() * 16) | 0,
                        v = c == "x" ? r : (r & 0x3) | 0x8;
                    return v.toString(16);
                }
            );
        }
        time(t) {
            let s = {
                "M+": new Date().getMonth() + 1,
                "d+": new Date().getDate(),
                "H+": new Date().getHours(),
                "m+": new Date().getMinutes(),
                "s+": new Date().getSeconds(),
                "q+": Math.floor((new Date().getMonth() + 3) / 3),
                S: new Date().getMilliseconds(),
            };
            /(y+)/.test(t) &&
                (t = t.replace(
                    RegExp.$1,
                    (new Date().getFullYear() + "").substr(4 - RegExp.$1.length)
                ));
            for (let e in s) {
                new RegExp("(" + e + ")").test(t) &&
                    (t = t.replace(
                        RegExp.$1,
                        1 == RegExp.$1.length
                            ? s[e]
                            : ("00" + s[e]).substr(("" + s[e]).length)
                    ));
            }
            return t;
        }

        log(content) {
            this.notifyStr.push(content)
            console.log(content)
        }
        wait(t) {
            return new Promise((s) => setTimeout(s, t));
        }
        async done(t = {}) {
            await this.sendMsg();
            const s = new Date().getTime(),
                e = (s - this.startTime) / 1e3;
            this.log(
                `\ud83d\udd14${this.name},\u7ed3\u675f!\ud83d\udd5b ${e}\u79d2`
            );
            if (this.isNode()) {
                process.exit(1);
            }
        }
    })(t, s);
}
