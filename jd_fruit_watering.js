/*
东东农场快速浇水
默认使用快速浇水卡，成熟了自动收取红包和种植新的水果
11 11 11 11 * jd_fruit_watering.js, tag=东东农场快速浇水, enabled=true
*/

const Env=require('./utils/Env.js');
const $ = new Env('东东农场快速浇水');
let cookiesArr = [],
  cookie = "",
  notify;
let message = "",
  subTitle = "",
  option = {},
  isFruitFinished = false;
const FRUIT_PLANT_LEVEL = process.env.FRUIT_PLANT_LEVEL ? process.env.FRUIT_PLANT_LEVEL : "2";
const JD_API_HOST = "https://api.m.jd.com/client.action";
!(async () => {
  await requireConfig();
  if (!cookiesArr[0]) {
    $.msg($.name, "【提示】请先获取京东账号一cookie\n直接使用NobyDa的京东签到获取", "https://bean.m.jd.com/bean/signIndex.action", {
      "open-url": "https://bean.m.jd.com/bean/signIndex.action"
    });
    return;
  }
  for (let _0x379fx43 = 0; _0x379fx43 < cookiesArr.length; _0x379fx43++) {
    if (cookiesArr[_0x379fx43]) {
      cookie = cookiesArr[_0x379fx43];
      $.UserName = decodeURIComponent(cookie.match(/pt_pin=([^; ]+)(?=;?)/) && cookie.match(/pt_pin=([^; ]+)(?=;?)/)[1]);
      $.index = _0x379fx43 + 1;
      $.isLogin = true;
      $.nickName = "";
      console.log("\n******开始【京东账号" + $.index + "】" + ($.nickName || $.UserName) + "*********\n");
      if (!$.isLogin) {
        $.msg($.name, "【提示】cookie已失效", "京东账号" + $.index + " " + ($.nickName || $.UserName) + "\n请重新登录获取\nhttps://bean.m.jd.com/bean/signIndex.action", {
          "open-url": "https://bean.m.jd.com/bean/signIndex.action"
        });
        if ($.isNode()) {
          await notify.sendNotify($.name + "cookie已失效 - " + $.UserName, "京东账号" + $.index + " " + $.UserName + "\n请重新登录获取cookie");
        }
        continue;
      }
      message = "";
      subTitle = "";
      option = {};
      await jdFruit();
    }
  }
})().catch(_0x379fx36 => {
  $.log("", "❌ " + $.name + ", 失败! 原因: " + _0x379fx36 + "!", "");
}).finally(() => {
  $.done();
});
async function jdFruit() {
  subTitle = "【京东账号" + $.index + "】" + ($.nickName || $.UserName);
  try {
    await initForFarm();
    if ($.farmInfo.farmUserPro) {
      if ($.farmInfo.treeState === 2 || $.farmInfo.treeState === 3) {
        const _0x379fx51 = $.farmInfo.farmUserPro.name;
        await gotCouponForFarm();
        await initForFarm();
        const _0x379fx52 = $.farmInfo.myHongBaoInfo.hongBao;
        console.log(_0x379fx51 + "已成熟并自动收获");
        console.log("获得" + _0x379fx52.discount + "元红包");
        console.log(timeFormat(_0x379fx52.endTime) + "过期，请及时使用");
        await autoPlant();
        return;
      } else {
        if ($.farmInfo.treeState === 1) {
          console.log("当前种植：" + $.farmInfo.farmUserPro.name + "（等级" + $.farmInfo.farmUserPro.prizeLevel + "）");
        } else {
          if ($.farmInfo.treeState === 0) {
            console.log("还没有种植新的水果\n");
            await autoPlant();
            return;
          }
        }
      }
      await Main();
    } else {
      console.log("初始化农场数据异常, 请登录京东 app查看农场0元水果功能是否正常,农场初始化数据: " + JSON.stringify($.farmInfo.message));
    }
  } catch (_0x30dabe) {
    console.log("任务执行异常，请检查执行日志");
    $.logErr(_0x30dabe);
  }
}
async function Main() {
  await initForFarm();
  let _0x379fx6b = $.farmInfo.farmUserPro.totalEnergy;
  console.log("目前共有 " + _0x379fx6b + "g 💧");
  await myCardInfoForFarm();
  const {
    fastCard,
    doubleCard,
    beanCard,
    signCard
  } = $.myCardInfoRes;
  console.log("快速浇水卡：" + (fastCard === -1 ? "未解锁" : fastCard + " 🎟️"));
  if (_0x379fx6b >= 100 && $.myCardInfoRes.fastCard > 0) {
    let _0x379fx6c = parseInt(_0x379fx6b / 100) > $.myCardInfoRes.fastCard ? $.myCardInfoRes.fastCard : parseInt(_0x379fx6b / 100);
    for (let _0x379fx6d = 0; _0x379fx6d < _0x379fx6c; _0x379fx6d++) {
      console.log("");
      await userMyCardForFarm("fastCard");
      if ($.userMyCardRes.code === "0") {
        _0x379fx6b -= 100;
        console.log("使用快速浇水卡 ✅");
        if ($.userMyCardRes.treeFinished) {
          isFruitFinished = true;
          break;
        } else {
          console.log("当前剩余 " + _0x379fx6b + "g 💧");
        }
        await $.wait(2000);
      } else {
        console.log("" + JSON.stringify($.userMyCardRes));
        console.log("❌ 浇水异常，可能触发风控，请稍后再试~");
        break;
      }
    }
  }
  if (isFruitFinished) {
    console.log("\n🎉 水果已可领取");
    const _0x379fx6e = $.farmInfo.farmUserPro.name;
    await gotCouponForFarm();
    await initForFarm();
    const _0x379fx6f = $.farmInfo.myHongBaoInfo.hongBao;
    console.log(_0x379fx6e + "已成熟并自动收获");
    console.log("获得" + _0x379fx6f.discount + "元红包");
    console.log(timeFormat(_0x379fx6f.endTime) + "过期，请及时使用");
    await autoPlant();
    return;
  }
  if (_0x379fx6b >= 10) {
    isFruitFinished = false;
    for (let _0x379fx70 = 0; _0x379fx70 < parseInt(_0x379fx6b / 10); _0x379fx70++) {
      console.log("");
      await waterGoodForFarm();
      if ($.waterResult.code === "0") {
        console.log("浇水10g ✅");
        if ($.waterResult.finished) {
          isFruitFinished = true;
          break;
        } else {
          await gotStageAward();
          console.log("当前剩余 " + $.waterResult.totalEnergy + "g 💧");
        }
        await $.wait(1000);
      } else {
        console.log("" + JSON.stringify($.waterResult));
        console.log("❌ 浇水异常，可能触发风控，请稍后再试~");
        break;
      }
    }
    if (isFruitFinished) {
      console.log("\n🎉 水果已可领取");
      const _0x379fx71 = $.farmInfo.farmUserPro.name;
      await gotCouponForFarm();
      await initForFarm();
      const _0x379fx6f = $.farmInfo.myHongBaoInfo.hongBao;
      console.log(_0x379fx71 + "已成熟并自动收获");
      console.log("获得" + _0x379fx6f.discount + "元红包");
      onsole.log(timeFormat(_0x379fx6f.endTime) + "过期，请及时使用");
      await autoPlant();
      return;
    }
  }
}
async function autoPlant() {
  await initForFarm();
  const _0x379fx7f = $.farmInfo.farmLevelWinGoods[FRUIT_PLANT_LEVEL];
  if (_0x379fx7f && _0x379fx7f.length) {
    const _0x379fx80 = _0x379fx7f[Math.floor(Math.random() * _0x379fx7f.length)];
    await choiceGoodsForFarm(_0x379fx80.type);
    if ($.choiceGoodsForFarmRes.code * 1 === 0) {
      console.log("【提醒⏰】您没有种植新的水果");
      console.log("已自动为您种植等级" + FRUIT_PLANT_LEVEL + "的" + $.choiceGoodsForFarmRes.farmUserPro.name);
    } else {
      console.log("【提醒⏰】您没有种植新的水果");
      onsole.log("尝试自动种植" + _0x379fx80.name + "失败，请打开京东APP手动尝试");
    }
  } else {
    console.log("【提醒⏰】您没有种植新的水果");
    console.log("指定的等级" + FRUIT_PLANT_LEVEL + "暂无水果可供选择，请打开京东APP检查");
  }
}
async function myCardInfoForFarm() {
  const _0x379fx82 = arguments.callee.name.toString();
  $.myCardInfoRes = await request(_0x379fx82, {
    "version": 5,
    "channel": 1
  });
}
async function userMyCardForFarm(_0x379fx84) {
  const _0x379fx89 = arguments.callee.name.toString();
  $.userMyCardRes = await request(_0x379fx89, {
    "cardType": _0x379fx84
  });
}
async function waterGoodForFarm() {
  await $.wait(1000);
  const _0x379fx8e = arguments.callee.name.toString();
  $.waterResult = await request(_0x379fx8e);
}
function gotStageAward() {
  return new Promise(async _0x379fx9e => {
    if ($.waterResult.waterStatus === 0 && $.waterResult.treeEnergy === 10) {
      console.log("果树发芽了，奖励30g水滴");
      await gotStageAwardForFarm("1");
      console.log("浇水阶段奖励1领取结果 " + JSON.stringify($.gotStageAwardForFarmRes));
      if ($.gotStageAwardForFarmRes.code === "0") {
        console.log("【果树发芽了】奖励" + $.gotStageAwardForFarmRes.addEnergy);
        console.log("");
      }
    } else {
      if ($.waterResult.waterStatus === 1) {
        console.log("果树开花了,奖励 40g 💧");
        await gotStageAwardForFarm("2");
        console.log("浇水阶段奖励2领取结果 " + JSON.stringify($.gotStageAwardForFarmRes));
        if ($.gotStageAwardForFarmRes.code === "0") {
          console.log("【果树开花了】奖励 " + $.gotStageAwardForFarmRes.addEnergy + "g 💧");
          console.log("");
        }
      } else {
        if ($.waterResult.waterStatus === 2) {
          console.log("果树长出小果子啦, 奖励 50g 💧");
          await gotStageAwardForFarm("3");
          console.log("浇水阶段奖励3领取结果 " + JSON.stringify($.gotStageAwardForFarmRes));
          if ($.gotStageAwardForFarmRes.code === "0") {
            console.log("【果树结果了】奖励 " + $.gotStageAwardForFarmRes.addEnergy + "g 💧");
            console.log("");
          }
        }
      }
    }
    _0x379fx9e();
  });
}
async function initForFarm() {
  const _0x379fxa4 = arguments.callee.name.toString();
  $.farmInfo = await request(_0x379fxa4, {
    "babelChannel": "121",
    "sid": "3c52b5f17ab2a42398939a27887eaf8w",
    "un_area": "17_1381_0_0",
    "version": 18,
    "channel": 1
  });
}
async function gotCouponForFarm() {
  const _0x379fxa7 = {
    "version": 11,
    "channel": 3,
    "babelChannel": 0
  };
  $.gotCouponForFarmRes = await request("gotCouponForFarm", _0x379fxa7);
}
async function choiceGoodsForFarm(_0x379fxa9) {
  const _0x379fxae = {
    "imageUrl": "",
    "nickName": "",
    "shareCode": "",
    "goodsType": _0x379fxa9,
    "type": "0",
    "version": 11,
    "channel": 3,
    "babelChannel": 0
  };
  $.choiceGoodsForFarmRes = await request("choiceGoodsForFarm", _0x379fxae);
}
function requireConfig() {
  return new Promise(_0x379fxba => {
    notify = $.isNode() ? require("./sendNotify") : "";
    const _0x379fxbb = $.isNode() ? require("./jdCookie") : "";
    if ($.isNode()) {
      Object.keys(_0x379fxbb).forEach(_0x379fxbc => {
        if (_0x379fxbb[_0x379fxbc]) {
          cookiesArr.push(_0x379fxbb[_0x379fxbc]);
        }
      });
      if (process.env.JD_DEBUG && process.env.JD_DEBUG === "false") {
        console.log = () => {};
      }
    } else {
      cookiesArr = [$.getdata("CookieJD"), $.getdata("CookieJD2"), ...jsonParse($.getdata("CookiesJD") || "[]").map(_0x379fxbe => {
        return _0x379fxbe.cookie;
      })].filter(_0x379fxbd => {
        return !!_0x379fxbd;
      });
    }
    _0x379fxba();
  });
}
function request(_0x379fxc0, _0x379fxc1 = {}, _0x379fxc2 = 1000) {
  return new Promise(_0x379fxd0 => {
    setTimeout(async () => {
      $.get(await taskUrl(_0x379fxc0, _0x379fxc1), (_0x379fxe0, _0x379fxe1, _0x379fxe2) => {
        try {
          if (_0x379fxe0) {
            console.log("\n东东农场: API查询请求失败 ‼️‼️");
            console.log(JSON.stringify(_0x379fxe0));
            console.log("function_id:" + _0x379fxc0);
            $.logErr(_0x379fxe0);
          } else {
            if (safeGet(_0x379fxe2)) {
              _0x379fxe2 = JSON.parse(_0x379fxe2);
            }
          }
        } catch (_0x5b421e) {
          $.logErr(_0x5b421e, _0x379fxe1);
        } finally {
          _0x379fxd0(_0x379fxe2);
        }
      });
    }, _0x379fxc2);
  });
}
function timeFormat(_0x379fxe4) {
  let _0x379fxf4;
  if (_0x379fxe4) {
    _0x379fxf4 = new Date(_0x379fxe4);
  } else {
    _0x379fxf4 = new Date();
  }
  return _0x379fxf4.getFullYear() + "-" + (_0x379fxf4.getMonth() + 1 >= 10 ? _0x379fxf4.getMonth() + 1 : "0" + (_0x379fxf4.getMonth() + 1)) + "-" + (_0x379fxf4.getDate() >= 10 ? _0x379fxf4.getDate() : "0" + _0x379fxf4.getDate());
}
function safeGet(_0x379fxf6) {
  if (!_0x379fxf6) {
    console.log("京东服务器返回数据为空");
    return false;
  }
  try {
    if (typeof JSON.parse(_0x379fxf6) == "object") {
      return true;
    }
  } catch (_0x501d82) {
    console.log(_0x501d82);
    return false;
  }
}
const appidMap = {
  "initForFarm": "8a2af",
  "taskInitForFarm": "fcb5a",
  "browseAdTaskForFarm": "53f09",
  "firstWaterTaskForFarm": "0cf1e",
  "waterFriendGotAwardForFarm": "d08ff",
  "ddnc_getTreasureBoxAward": "67dfc",
  "totalWaterTaskForFarm": "102f5",
  "gotThreeMealForFarm": "57b30",
  "waterGoodForFarm": "0c010",
  "choiceGoodsForFarm": "5f4ca",
  "gotCouponForFarm": "b1515",
  "gotStageAwardForFarm": "81591",
  "followVenderForBrand": "71547",
  "gotWaterGoalTaskForFarm": "c901b",
  "gotNewUserTaskForFarm": "de8f8",
  "orderTaskGotWaterForFarm": "eed5c",
  "clockInForFarm": "32b94",
  "clockInFollowForFarm": "4a0b4",
  "waterFriendForFarm": "673a0",
  "awardFirstFriendForFarm": "9b655",
  "awardInviteFriendForFarm": "2b5ca",
  "awardCallOrInviteFriendForFarm": "b0b03",
  "userMyCardForFarm": "86ba5",
  "getCallUserCardForFarm": "2ca57",
  "deleteFriendForFarm": "eaf91",
  "gotLowFreqWaterForFarm": "8172b",
  "getFullCollectionReward": "5c767",
  "getOrderPayLotteryWater": "ef089",
  "receiveStageEnergy": "15507",
  "exchangeGood": "52963",
  "farmAssistInit": "92354",
  "myCardInfoForFarm": "157b6",
  "gotPopFirstPurchaseTaskForFarm": "d432f",
  "limitWaterInitForFarm": "6bdc2",
  "ddnc_surpriseModal": "e81c1",
  "friendInitForFarm": "a5a9c",
  "clockInInitForFarm": "08dc3",
  "guideTaskAward": "59bc4"
};
async function taskUrl(_0x379fxfe, _0x379fxff = {}) {
  let _0x379fx105 = "";
  if (!appidMap[_0x379fxfe]) {
    _0x379fx105 = JD_API_HOST + "?functionId=" + _0x379fxfe + "&body=" + encodeURIComponent(JSON.stringify(_0x379fxff)) + "&appid=wh5";
  } else {
    const _0x379fx106 = {
      "appid": "signed_wh5",
      "client": "android",
      "clientVersion": "10.4.3",
      "functionId": _0x379fxfe,
      "body": _0x379fxff
    };
    const _0x379fx107 = await getH5st(appidMap[_0x379fxfe], _0x379fx106);
    _0x379fx105 = JD_API_HOST + "?functionId=" + _0x379fxfe + "&appid=signed_wh5&body=" + encodeURIComponent(JSON.stringify(_0x379fxff)) + "&client=android&clientVersion=10.4.3&h5st=" + encodeURIComponent(_0x379fx107);
  }
  return {
    "url": _0x379fx105,
    "headers": {
      "Host": "api.m.jd.com",
      "Accept": "*/*",
      "Origin": "https://carry.m.jd.com",
      "Accept-Encoding": "gzip,deflate,br",
      "User-Agent": $.isNode() ? process.env.JD_USER_AGENT ? process.env.JD_USER_AGENT : require("./USER_AGENTS").USER_AGENT : $.getdata("JDUA") ? $.getdata("JDUA") : "jdapp;iPhone;9.4.4;14.3;network/4g;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
      "Accept-Language": "zh-CN,zh-Hans;q=0.9",
      "Referer": "https://carry.m.jd.com/",
      "x-requested-with": "com.jingdong.app.mall",
      "Cookie": cookie
    },
    "timeout": 10000
  };
}
function getH5st(_0x379fx109, _0x379fx10a) {
  return new Promise(async _0x379fx114 => {
    let _0x379fx11e = {
      "url": "http://api.kingran.cf/h5st",
      "body": "businessId=" + _0x379fx109 + "&req=" + encodeURIComponent(JSON.stringify(_0x379fx10a)),
      "headers": {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/87.0.4280.88"
      },
      "timeout": 30 * 1000
    };
    $.post(_0x379fx11e, (_0x379fx11f, _0x379fx120, _0x379fx121) => {
      try {
        if (_0x379fx11f) {
          console.log(JSON.stringify(_0x379fx11f));
        } else {}
      } catch (_0x33d0eb) {
        $.logErr(_0x33d0eb, _0x379fx120);
      } finally {
        _0x379fx114(_0x379fx121);
      }
    });
  });
}
function jsonParse(_0x379fx123) {
  if (typeof _0x379fx123 == "string") {
    try {
      return JSON.parse(_0x379fx123);
    } catch (_0xbd649b) {
      console.log(_0xbd649b);
      $.msg($.name, "", "请勿随意在BoxJs输入框修改内容\n建议通过脚本去获取cookie");
      return [];
    }
  }
}
