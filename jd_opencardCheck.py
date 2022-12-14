#!/usr/bin/python3
# -*- coding: utf8 -*-
"""

#（必填）填写要监控的GitHub仓库的 “用户名/仓库名/仓库分支/脚本关键词” 监控多个仓库请用 & 隔开
export GitRepoHost="KingRan/KR/main/opencard&feverrun/my_scripts/main/opencard&smiek2121/scripts/master/opencard&okyyds/yyds/master/lzdz1"
#（推荐）Github Token变量，将api请求次数提升到5000次/小时，默认60次/小时
export GitToken="GithubToken"
#（可选）http代理，针对国内机使用，访问不了github的可以填上，支持用户名密码
export GitProxy="http://username:password@127.0.0.1:8080"
#（可选）任务参数，格式和青龙的 conc、desi 一样的用法，请自行参考，不使用请留空
export opencardParam="desi JD_COOKIE 1 3-10"
#（可选）运行开卡脚本前禁用开卡脚本定时任务，不使用请留空
export opencardDisable="true"
#（可选）检测重复任务相似度阈值，默认值为50，不使用请留空
#       值过小：两个不同的开卡脚本识别为同一个
#       值过大：两个相同开卡脚本识别为两个不同脚本
export opencardSimi="50"
#（可选）死循环模式，默认为正常模式，启用此模式必须填写GitToken
#       脚本运行2小时自动停止，定时规则请设置为：0 */2 * * *
export opencardLoop="true"

cron: */1 * * * *
new Env('开卡更新自动监测')
"""

from notify import send
import requests,json,os,re,difflib,time
from functools import partial
print = partial(print, flush=True)

print("软件版本：8.26.2")

# 显示日志
def log(content):
    print(content)
    List.append(content)

# 获取青龙内部Token
def GetQLToken():
    path = '/ql/config/auth.json'
    if not os.path.exists(path):
        path = '/ql/data/config/auth.json'
    with open(path,"r",encoding="utf-8") as file:
        auth = json.load(file)
        qltoken = auth.get("token")
    try:
        url = "http://127.0.0.1:5700/api/user"
        rsp = session.get(url=url,headers={"Content-Type":"application/json","Authorization":"Bearer "+qltoken})
        if rsp.status_code != 200:
            url = "http://127.0.0.1:5700/api/user/login"
            body={"username": auth.get("username"),"password": auth.get("password")}
            qltoken = session.post(url=url,data=body).json().get("data").get("token")
    except:
        print("无法获取青龙登录token！！！")
        exit()
    return qltoken

def GetQLPath():
    if os.path.exists("/ql/data"):
        Path="/ql/data/scripts/"+Repo[0]+"_"+Repo[1]
        if not os.path.exists(Path):
            Path="/ql/data/scripts/"+Repo[0]+"_"+Repo[1]+"_"+Repo[2]
            if not os.path.exists(Path):
                print(f"找不到{GitRepo}库文件夹")
    else:
        Path="/ql/scripts/"+Repo[0]+"_"+Repo[1]
        if not os.path.exists(Path):
            Path="/ql/scripts/"+Repo[0]+"_"+Repo[1]+"_"+Repo[2]
            if not os.path.exists(Path):
                Path="/ql/scripts/"+Repo[0]+"_"+Repo[1]+"_"
                return Path
    return Path+"/"

# 禁用定时任务
def qlCronDis(TaskName,TaskID):
    url = qlHost+"/crons/disable"
    rsp = session.put(url=url,headers=qlHeader,data=json.dumps([TaskID]))
    if rsp.status_code == 200:
        log(f"禁用开卡任务成功：{TaskName}")
    else:
        log(f'禁用开卡任务失败：{TaskName}')
        if "message" in rsp.json():
            log(f"错误信息："+rsp.json()["message"])

# 更改任务命令
def qlTaskChange(jsons,TaskID):
    url = qlHost+"/crons"
    body = {"command": jsons[0]["command"]+" "+os.environ["opencardParam"], "schedule": jsons[0]["schedule"], "name": jsons[0]["name"], TaskID: jsons[0][TaskID]}
    rsp = session.put(url=url,headers=qlHeader,data=json.dumps(body))
    if rsp.status_code == 200:
        log("更改命令成功："+rsp.json().get("data").get("command"))
    else:
        log(f"更改命令失败："+jsons[0]["command"])
        if "message" in rsp.json():
            log(f"错误信息："+rsp.json()["message"])

# 检查重复任务
def qlCronCheck(name):
    print("开始检查重复任务")
    Check = True
    with open('./nameCron.json',"r",encoding='UTF-8') as f:
        TaskStr = json.load(f)
    nameSplit = re.split(' |,|，',name)[::-1]
    taskName = nameSplit[0]
    if len(taskName)==0:
        taskName = nameSplit[1]
    for i in TaskStr:
        for x in TaskStr[i]:
            point = round(difflib.SequenceMatcher(None,taskName,x).quick_ratio()*100)
            if point>=int(os.environ["opencardSimi"]):
                log(f"任务名高度相似：{name}/{x}={point}%")
                log(f"放弃运行任务：{name}")
                Check = False;break
        if not Check:
            break
    if Repo[0] not in TaskStr:
        TaskStr[Repo[0]]=[]
    if taskName not in TaskStr[Repo[0]]:
        TaskStr[Repo[0]].append(taskName)
        with open(f"./nameCron.json","w",encoding='UTF-8') as f:
            json.dump(TaskStr,f,ensure_ascii=False)
            print(f"保存任务名到nameCron.json文件")
    return Check

# 运行青龙订阅任务
def qlSub(name):
    url = qlHost+"/subscriptions?searchValue="+name
    rsp = session.get(url=url, headers=qlHeader)
    if rsp.status_code == 200:
        jsons = rsp.json().get("data")
        if len(jsons)==0:
            log(f"没有找到相关订阅：{name}")
            return False
    else:
        log(f'搜索订阅失败：{str(rsp.status_code)}')
        if "message" in rsp.json():
            log(f"错误信息："+rsp.json()["message"])
        return False
    url = qlHost+"/subscriptions/run"
    rsp = session.put(url=url,headers=qlHeader,data=json.dumps([jsons[0].get("_id")]))
    if rsp.status_code == 200:
        log(f"运行订阅成功："+jsons[0].get("name"))
        return True
    else:
        log(f"运行订阅失败："+jsons[0].get("name"))
        if "message" in rsp.json():
            log(f"错误信息："+rsp.json()["message"])
        return False

# 运行青龙任务
def qlCron(name,cmd,state):
    url = qlHost+"/crons?searchValue="+name
    rsp = session.get(url=url,headers=qlHeader)
    if rsp.status_code == 200:
        jsons = rsp.json().get("data")
        if len(jsons):
            if "id" in jsons[0]:
                TaskID = "id"
            elif "_id" in jsons[0]:
                TaskID = "_id"
            else:
                log("获取任务ID失败："+jsons[0]["name"])
                return False
        else:
            log(f"没有找到相关任务：{name}")
            return False
    else:
        log("搜索任务失败："+str(rsp.status_code))
        if "message" in rsp.json():
            log(f"错误信息："+rsp.json()["message"])
        return False
    if state:
        # 禁用定时任务
        if os.environ.get('opencardDisable')=="true":
            qlCronDis(jsons[0]["name"],jsons[0].get(TaskID))
        # 更改任务命令
        if os.environ.get('opencardParam')!=None and os.environ.get('opencardParam')!="" and "desi" not in jsons[0]["command"]:
            qlTaskChange(jsons,TaskID)
        # 检查重复任务
        if os.environ.get('opencardSimi')!=None and os.environ.get('opencardSimi')!="":
            if not qlCronCheck(jsons[0]["name"]):
                return True
    # 运行定时任务
    url = qlHost+"/crons/"+cmd
    rsp = session.put(url=url,headers=qlHeader,data=json.dumps([jsons[0].get(TaskID)]))
    if rsp.status_code == 200:
        log(f"执行操作成功：{cmd} "+jsons[0]["name"])
        return True
    else:
        log(f"执行操作失败：{cmd} "+jsons[0]["name"])
        if "message" in rsp.json():
            log(f"错误信息："+rsp.json()["message"])
        return False

# 获取开卡脚本目录树
def OpenCardTree():
    print("")
    log(f"监控仓库：{GitRepo}")
    GitAPI = f'https://api.github.com/repos/{GitRepo}/git/trees/{Repo[2]}'
    try:
        rsp = session.get(url=GitAPI,headers=GitHeader,proxies=GitProxy)
        if rsp.status_code == 200:
            tree = []
            for x in rsp.json()["tree"]:
                if Repo[3] in x["path"]:
                     tree.append(x["path"])
            return tree
        else:
            log(f'请求失败：{GitAPI}')
            if "message" in rsp.json():
                log(f'错误信息：{rsp.json()["message"]}')
            return False
    except:
        log(f'请求URL失败：{GitAPI}')
        return False

def CheckChange():
    with open(f"./nameScripts.json",'r') as file:
        scriptsJson = json.load(file)
        if Repo[0] not in scriptsJson:
            scriptsJson[Repo[0]]=tree
            with open('./nameScripts.json',"w") as f:
                json.dump(scriptsJson,f)
            # log("nameScripts.json中未找到KEY："+Repo[0])
    
    ScriptDel = False
    for scriptsName in scriptsJson[Repo[0]]:
        if scriptsName not in tree:
            log("停止运行被删除的开卡："+scriptsName)
            try:
                qlHeader["Authorization"]="Bearer "+GetQLToken()
                ScriptDel = qlCron(scriptsName,"stop",False)
            except:
                log("停止运行开卡脚本失败："+scriptsName)

    ScriptNew = False
    for scriptsName in tree:
        if scriptsName not in scriptsJson[Repo[0]]:
            log(f"新增开卡脚本：{scriptsName}")
            try:
                qlHeader["Authorization"]="Bearer "+GetQLToken()
                if "/ql/data" in qlPath:
                    rsp = session.get(url=qlHost+"/subscriptions",headers=qlHeader)
                    if rsp.status_code==200:
                        print("订阅管理可用")
                        status = qlSub(GitRepo)
                    else:
                        print("订阅管理不可用")
                        status = qlCron(GitRepo,"run",False)
                else:
                    status = qlCron(GitRepo,"run",False)
                if status:
                    ii = 0
                    print("拉库检测文件中\n"+qlPath+scriptsName)
                    while not os.path.exists(qlPath+scriptsName):
                        if ii>300:
                            log(f"等待{scriptsName}添加到文件夹超时>>{str(ii)}秒");break
                        time.sleep(1);ii+=1
                    url = qlHost+"/crons?searchValue="+scriptsName
                    rsp = session.get(url=url,headers=qlHeader).json().get("data")
                    xx = 0
                    while len(rsp)==0 and ii<300:
                        if xx>120:
                            log(f"等待{scriptsName}添加到定时任务超时>>{str(xx)}秒");break
                        time.sleep(1);xx+=1
                        rsp = session.get(url=url,headers=qlHeader).json().get("data")
                    print(f"拉库成功：耗时{str(xx+ii)}秒")
                    if ii<300 and xx<120:
                        ScriptNew = qlCron(scriptsName,"run",True)
            except:
                log("青龙任务运行失败")

    if ScriptNew or ScriptDel:
        with open(f"./nameScripts.json","w") as f:
            scriptsJson[Repo[0]]=tree
            json.dump(scriptsJson,f)
        print("运行时间："+time.strftime('%H:%M:%S',time.localtime()))
        send("开卡更新检测",'\n'.join(List))
    else:
        log("没有增删开卡脚本")

if not os.path.exists(f"./nameScripts.json"):
    with open(f"./nameScripts.json","w") as f:
        json.dump({},f)
    print(f"没有找到nameScripts.json文件！将自动生成")
if not os.path.exists(f"./nameCron.json"):
    with open(f"./nameCron.json","w") as f:
        json.dump({},f,ensure_ascii=False)
    print(f"没有找到nameCron.json文件！将自动生成")
if 'GitRepoHost' in os.environ:
    session = requests.session()
    # 青龙全局变量
    qlHost = "http://127.0.0.1:5700/api"
    qlHeader = {"Content-Type":"application/json"}
    # 获取要监控的Github仓库
    RepoHost = os.environ['GitRepoHost'].split("&")
    # 获取Github Token
    GitHeader = {"Content-Type":"application/json"}
    if os.environ.get('GitToken')!=None and os.environ.get('GitToken')!="":
        GitHeader["Authorization"]="Bearer "+os.environ['GitToken']
        print("已设置Github Token")
    # 获取Github代理
    GitProxy = {}
    if os.environ.get('GitProxy')!=None and os.environ.get('GitProxy')!="":
        GitProxy['http'] = os.environ['GitProxy']
        GitProxy['https'] = os.environ['GitProxy']
        print("已设置HTTP代理，将通过代理访问api.github.com")
    # 为true则开启死循环模式
    if os.environ.get("opencardLoop")=="true":
        print("当前模式：死循环模式")
        start = time.time()
        end = time.time()
        Delay = 30/len(RepoHost)
        times = 7200-30-Delay
        while (end-start)<times:
            for Data in RepoHost:
                List=[]
                Repo = Data.split("/")
                GitRepo = Repo[0]+"/"+Repo[1]
                tree = OpenCardTree()
                if tree != False:
                    qlPath = GetQLPath()
                    CheckChange()
                time.sleep(Delay)
            end = time.time()
    else:
        print("当前模式：正常模式")
        for Data in RepoHost:
            List=[]
            Repo = Data.split("/")
            GitRepo = Repo[0]+"/"+Repo[1]
            tree = OpenCardTree()
            if tree != False:
                qlPath = GetQLPath()
                CheckChange()
else:
    print("请查看脚本注释后设置相关变量")
