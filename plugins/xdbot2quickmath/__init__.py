import asyncio
import os.path

import nonebot
import httpx
import base64
import re
import json
import random
from sympy import Symbol, solve, sympify
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.log import logger
from nonebot import require
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11.event import MessageEvent
require("nonebot_plugin_apscheduler")
xdbot2quickmath_on = True
xdbot2quickmath_image_on = False
prefix = "XDBOT2 QUICK MATH | "
rec = "XDBOT2 QUICK MATH | OCR [{x}]\n识别结果: {a}\n处理算式: {b}\n计算答案: {c}"
ocrinfojson = "data/ocrinfo.json"
if not os.path.exists(ocrinfojson):
    json.dump({},open(ocrinfojson,"w"))
def getOcrInfo(_id: str) -> str:
    ocrinfo: dict = json.load(open(ocrinfojson,"r"))
    return str(ocrinfo.get(_id,"数据不存在"))
def setOcrInfo(_id: str, info: str):
    ocrinfo: dict = json.load(open(ocrinfojson,"r"))
    ocrinfo[_id] = info
    json.dump(ocrinfo,open(ocrinfojson,"w"))
def genRandomID(k: int = 8) -> str:
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789",k=k))

async def getImageApi(string):
    async with httpx.AsyncClient() as client:
        url = 'https://api.setbug.com/tools/text2image/?text='+string
        response = await client.get(url)
        return response.read()
async def xtapi_post(res,data) -> dict:
    async with httpx.AsyncClient() as client:
        url = "http://127.0.0.1:6789/"+res # 非公开内容
        response = await client.post(url,data=data)
        return response.json()
async def getImageBase64(message: str):
    if not message.startswith("[CQ:image"):
        return False
    cqStart = message.find("[CQ:image")
    url = message[message.find("url=", cqStart) +
                  4: message.find("]", cqStart)]
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    content = response.read()
    if not content:
        return False
    return base64.b64encode(content).decode()
def process_eq(eq: str) -> str:
    if eq[-1] != "=" and "x" not in eq:
        eq = eq.split("=")[0]+"="
    eq = eq.replace("Z", "7").replace("J","9").replace("O","0").replace("I","1").replace("S","5").replace("B","8")
    eq = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', eq)
    return eq
def get_answer(eq: str) -> str:
    x = Symbol('x')
    eq = eq.replace("=","-")
    ans = solve(eq,x)
    logger.info("[QUICK MATH] origin answer is "+str(ans))
    return str(ans[0])

x2q = nonebot.on_command("xdbot2quickmath",)
@x2q.handle()
async def _(matcher: Matcher,
        bot: Bot,
        event: Event,
        args: Message = CommandArg()):
    global xdbot2quickmath_on
    global xdbot2quickmath_image_on
    global prefix
    args=args.extract_plain_text()
    if "=" in args:
        if not xdbot2quickmath_on:
            await x2q.finish()
        args=args.split(" ")
        if not xdbot2quickmath_image_on:
            match args[1]:
                case "+":
                    await x2q.finish(prefix+str(int(args[0])+int(args[2])))
                case "-":
                    await x2q.finish(prefix+str(int(args[0])-int(args[2])))
                case "*":
                    await x2q.finish(prefix+str(int(args[0])*int(args[2])))
        else:
            match args[1]:
                case "+":
                    await x2q.finish(MessageSegment.image(await getImageApi(prefix+str(int(args[0])+int(args[2])))))
                case "-":
                    await x2q.finish(MessageSegment.image(await getImageApi(prefix+str(int(args[0])-int(args[2])))))
                case "*":
                    await x2q.finish(MessageSegment.image(await getImageApi(prefix+str(int(args[0])*int(args[2])))))
    else:
        if args == "on" or args == "启用":
            xdbot2quickmath_on=True
            await x2q.finish("xdbot2quickmath on")
        elif args == "off" or args == "禁用":
            xdbot2quickmath_on=False
            await x2q.finish("xdbot2quickmath off")
        elif args == "prefixoff":
            prefix=""
            await x2q.finish("xdbot2quickmath prefix off")
        elif args == "prefixon":
            prefix="XDBOT2 QUICK MATH 答案 | "
            await x2q.finish("xdbot2quickmath prefix on")
        elif args == "imageoff":
            xdbot2quickmath_image_on=False
            await x2q.finish("xdbot2quickmath image off")
        elif args == "imageon":
            xdbot2quickmath_image_on=True
            await x2q.finish("xdbot2quickmath image on")

x2qn = nonebot.on_regex(r"^\[CQ:image")
@x2qn.handle()
async def _n(matcher: Matcher,
        bot: Bot,
        event: GroupMessageEvent):
    logger.info("[QUICK MATH] Try to process quickmath")
    if event.get_user_id() not in []: # 非公开内容
        logger.warning("[QUICK MATH] User ID not match")
        return
    if not xdbot2quickmath_on:
        logger.warning("[QUICK MATH] Not enabled")
        return
    ib = await getImageBase64(str(event.get_message()))
    if ib:
        text_list = (await xtapi_post("ocr", {"img_base64": ib}))["text"]
    try:
        logger.info("[QUICK MATH] OCR result: "+str(text_list))
    except:
        pass
    setOcrInfo(ocr_id := genRandomID(), str(text_list))
    matched_text = ["QUICK","MATH","QUTCK"]
    for t in matched_text:
        if t in text_list[0]:
            logger.info("[QUICK MATH] 「" + t + "」 in 「" + text_list[0] + " 」 continue")
            break
        if t == matched_text[-1]:
            logger.warning("[QUICK MATH] 「"+t+"」 not in 「"+text_list[0]+" 」 return")
            logger.warning("[QUICK MATH] Not quick math image")
            return
    question : str = text_list[1].replace(" ","").replace("?","").replace("X","x")
    eq = process_eq(question)
    reply = rec.replace("{a}", text_list[1]).replace("{b}",eq).replace("{x}",ocr_id)
    try:
        if "x" in eq: # 方程
            reply = reply.replace("{c}",get_answer(eq))
        elif eq.endswith("="): # 计算
            reply = reply.replace("{c}", str(int(sympify(eq.replace("=","")).evalf())))
        else:
            reply = reply.replace("{c}", "无法计算")
    except:
        reply = reply.replace("{c}", "无法计算")
    if xdbot2quickmath_image_on:
        reply = MessageSegment.image(await getImageApi(reply))
    else:
        reply = Message(reply)
    msg_id = (await bot.send_group_msg(
        group_id=event.group_id,
        message=reply))["message_id"]
    await asyncio.sleep(18)
    await bot.delete_msg(message_id=msg_id)
@nonebot.on_message(rule=to_me()).handle()
async def _(m: Matcher, event: MessageEvent):
    if (event.reply is None) or (event.get_plaintext() not in ["info","ocrinfo","infoocr","ocr","data"]):
        return
    if not (msg := event.reply.message.extract_plain_text()).startswith("XDBOT2 QUICK MATH"):
        return
    if len(ocr_id := msg.split("\n")[0].replace("XDBOT2 QUICK MATH | OCR [","").replace("]","")) != 8:
        return
    await m.finish(getOcrInfo(ocr_id),at_sender=True)