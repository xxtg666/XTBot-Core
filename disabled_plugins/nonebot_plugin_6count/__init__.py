import json
import os
import time
import copy
import traceback
import base64
import httpx
import nonebot
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.adapters.onebot.v11 import Bot
from nonebot.exception import *
from pyecharts import options as opts
from pyecharts.charts import Pie
from pyecharts.charts import Bar
async def xtapi_post(res,data):
    async with httpx.AsyncClient() as client:
        url = "http://127.0.0.1:6789/"+res # 非公开内容
        response = await client.post(url,data=data)
        return response.json()
datasrc="."+os.sep+"data"+os.sep
countfile="."+os.sep+"data"+os.sep+"6count.json"
if not os.path.exists(countfile):
    with open(countfile,"w") as f:
        json.dump({"time":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())},f)
def getcount():
    with open(countfile,"r") as f:
        count=json.load(f)
    return count
def setcount(count):
    with open(countfile,"w") as f:
        json.dump(count,f)

c6 = nonebot.on_command("6-count",)
@c6.handle()
async def handle_first_receive(matcher: Matcher,
        bot: Bot,
        event: Event,
        args: Message = CommandArg()):
    global count
    arg=args.extract_plain_text()
    if arg.startswith("add"):
        usrid=event.get_user_id()
        try:
            count=getcount()
            count[usrid]+=1
            setcount(count)
        except:
            count=getcount()
            count[usrid]=1
            setcount(count)
    elif arg == "data":
        await c6.finish(str(getcount()))
    elif arg == "reset":
        if not event.get_user_id() == "1747433912":
            await c6.finish("无权限")
        setcount({"time":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
    elif arg.startswith("modify"):
        if not event.get_user_id() == "1747433912":
            await c6.finish("无权限")
        arg=arg.split(" ")
        count=getcount()
        count[arg[1]]=int(arg[2])
        setcount(count)
    elif arg.startswith("show"):
        try:
            count=getcount()
            t=copy.deepcopy(count["time"])
            count["time"]="time"
            qqs=list(count.keys())
            qqs.remove("time")
            numbers=list(count.values())
            numbers.remove("time")
            names=[]
            for q in qqs:
                names.append((await bot.get_stranger_info(user_id=q))['nickname'])
            if arg=="show":
                showtype="Pie"
            else:
                showtype=arg.split(" ")[1]
            if showtype=="Pie":
                data=[]
                for i in range(len(qqs)):
                    data.append((names[i],count[qqs[i]]))
                c = Pie(init_opts=opts.InitOpts(bg_color='rgba(255,255,255,1)')).add("", data).set_global_opts(title_opts=opts.TitleOpts(title="6",subtitle=t+" 至今")).set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}")).render(datasrc+"6count.html")
            elif showtype=="Bar":
                c = Bar(init_opts=opts.InitOpts(bg_color='rgba(255,255,255,1)')).add_xaxis(names).add_yaxis("", numbers).set_global_opts(xaxis_opts=opts.AxisOpts(axislabel_opts={"interval":"0"}),title_opts=opts.TitleOpts(title="6", subtitle=t+" 至今")).render(datasrc+"6count.html")
            else:
                await c6.finish("未知图表类型")
            img_bytes=base64.b64decode((await xtapi_post("html/img",{"html":open(c,"r").read(),"timeout":"5000"}))["image_base64"])
            await c6.finish(MessageSegment.image(img_bytes))
        except FinishedException:
            pass
        except:
            await c6.finish(traceback.format_exc())
