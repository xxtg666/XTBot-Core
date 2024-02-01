import nonebot
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11.message import Message
from nonebot.params import CommandArg
import httpx
import os
import re
import copy
import discord
import threading
import json
import random
import asyncio
import traceback
import time

os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"
TOKEN = "" # 非公开内容
CHANNEL_ID = 0 # 非公开内容
CHANNEL_ID_GH = 0 # 非公开内容
QQ_ID = 0 # 非公开内容
QQ_ID_GH = 0 # 非公开内容
already_start_discord_bot = False
intents = discord.Intents.default()
intents.message_content = True
dcclient = discord.Client(intents=intents,proxy=os.environ["HTTP_PROXY"])
qq_bind_file = "data/discord_message_bridge_qq_bind.json"
qq_bind_file_2 = "data/discord_message_bridge_qq_bind_2.json"
if not os.path.exists(qq_bind_file):
    json.dump({},open(qq_bind_file,"w"))
if not os.path.exists(qq_bind_file_2):
    json.dump({},open(qq_bind_file_2,"w"))
avatars = {
    "692732163":"<:avatar_fzsgball:1133052617979875399>",
    "3627035438":"<:avatar_fzz:1133052351180181647>",
    "824649807":"<:avatar_hsc:1133052508370120715>",
    "3370185446":"<:avatar_pmb:1133052593808085054>",
    "3489840593":"<:avatar_shirasawa:1133052438048428132>",
    "1619365833":"<:avatar_suystar:1133052564640907285>",
    "2915495930":"<:avatar_sw:1133052536891392111>",
    "1744793737":"<:avatar_xd:1133051557001318461>",
    "3457603681":"<:avatar_xdbot:1133052388438188143>",
    "3068342155":"<:avatar_xiexilin:1133052475323191398>",
    "1747433912":"<:avatar_xxtg666:1142075321500307496>",
    "2558938020":"<:avatar_yf:1133052648078192772>",
    "2991600190":"<:avatar_laman28:1133056884446871582>",
    "1951474558":"<:avatar_chun:1133056924674441327>",
    "2033614927":"<:avatar_zhao:1134437717720191017>"
}
temp_bind_qq = {} # qq:rid
temp_bind_dis = {} # rid:dis
def get_qq_bind(discord_id):
    return json.load(open(qq_bind_file,"r")).get(str(discord_id),False)
def get_qq_bind_discord(qq_id):
    return json.load(open(qq_bind_file_2,"r")).get(str(qq_id),False)
def set_qq_bind(discord_id,qq_id):
    qq_bind = json.load(open(qq_bind_file,"r"))
    qq_bind[str(discord_id)] = str(qq_id)
    qq_bind_2 = json.load(open(qq_bind_file_2,"r"))
    qq_bind_2[str(qq_id)] = str(discord_id)
    json.dump(qq_bind,open(qq_bind_file,"w"))
    json.dump(qq_bind_2,open(qq_bind_file_2,"w"))
def genRandomID(k: int = 8) -> str:
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789",k=k))
def process_xdbot_command(discord_id,command):
    discord_id = str(discord_id)
    global temp_bind_qq,temp_bind_dis
    command = command.replace("~","",1)
    if command.startswith("bind"):
        try:
            qq_id = command.split(" ")[1]
            if qq_id in temp_bind_qq:
                if temp_bind_dis[temp_bind_qq[qq_id]] == discord_id:
                    return [(f"<@{discord_id}> 你已在请求绑定QQ号,请在QQ群内发送 `.dmb bind {temp_bind_qq[qq_id]}` 进行绑定",False),
                            (f"[CQ:at,qq={qq_id}] 请发送「.dmb bind {temp_bind_qq[qq_id]}」绑定 Discord({discord_id}) 如果这不是你的操作, 请忽略本条消息",True)]
                else:
                    del temp_bind_qq[qq_id]
                    del temp_bind_dis[temp_bind_qq[qq_id]]
            rid = genRandomID(24)
            temp_bind_qq[qq_id] = rid
            temp_bind_dis[rid] = discord_id
            return [(f"<@{discord_id}> 请在QQ群内发送 `.dmb bind {rid}` 进行绑定",False),
                    (f"[CQ:at,qq={qq_id}] 请发送「.dmb bind {rid}」绑定 Discord({discord_id}) 如果这不是你的操作, 请忽略本条消息",True)]
        except:
            if qq_id := get_qq_bind(discord_id):
                return [(f"<@{discord_id}> 你已绑定QQ号 `{qq_id}`",False)]
            return [(f"<@{discord_id}> 命令格式错误,应为: `~bind <uid>`",False)]
    if not (qq_id := get_qq_bind(discord_id)):
        return [(f"<@{discord_id}> 请先使用 `~bind <uid>` 绑定QQ号",False)]
    return [(f"/sudo {qq_id} {command}",True)]
async def send_message(content,channel):
    async with httpx.AsyncClient() as client:
        await client.post(
            url=f"https://discord.com/api/channels/{channel}/messages",
            headers={
                "Authorization": f"Bot {TOKEN}",
                "User-Agent": "DiscordBot"
            },
            data={
                "content": content
            }
        )
async def send_list_message(content_list,channel,qqid):
    for i in content_list:
        if not i[1]:
            await send_message(i[0],channel)
        else:
            await gbot.send_group_msg(group_id=qqid, message=i[0])
def avatar(uid):
    return avatars.get(str(uid),"")
def process_text(text: str):
    return text.replace("&amp;#93;","]").replace("&amp;#91;","[")

bot_restart_time = 0
def startDiscordBot():
    global bot_restart_time
    global dcclient
    time_1 = time.time()
    if bot_restart_time > 3:
        asyncio.run(gbot.send_group_msg(group_id=QQ_ID, message=f"[Discord] 转发 Bot 短时间启动失败次数过多,已停止"))
        return
    if bot_restart_time != 0:
        asyncio.run(gbot.send_group_msg(group_id=QQ_ID, message=f"[Discord] 转发 Bot 正在重启 ({bot_restart_time}次)"))
    try:
        dcclient = discord.Client(intents=intents,proxy=os.environ["HTTP_PROXY"])
        @dcclient.event
        async def on_message(message):
            if message.author.id == dcclient.user.id:
                return
            ms = f'[Discord] <{message.author.name}> {message.content}'
            if message.channel.id == CHANNEL_ID:
                if str(message.content).strip().startswith("~"):
                    r = process_xdbot_command(message.author.id,str(message.content).strip())
                    await send_list_message(r,CHANNEL_ID,QQ_ID)
                    return
                await gbot.send_group_msg(group_id=QQ_ID, message=replace_ids_with_cq_at(ms))
            elif message.channel.id == CHANNEL_ID_GH:
                if str(message.content).strip().startswith("~"):
                    r = process_xdbot_command(message.author.id,str(message.content).strip())
                    await send_list_message(r,CHANNEL_ID_GH,QQ_ID_GH)
                    return
                await gbot.send_group_msg(group_id=QQ_ID_GH, message=replace_ids_with_cq_at(ms))
            elif message.channel.id == 1133053561408860191: # DEV
                await gbot.send_group_msg(group_id=1007654102, message=ms)
        dcclient.run(TOKEN)
    except:
        del dcclient
        time_2 = time.time()
        asyncio.run(gbot.send_group_msg(group_id=QQ_ID, message=f"[Discord] 转发 Bot 异常断开连接 (已运行{int(time_2-time_1)}秒)\n" +
                                                                traceback.format_exc().split("\n")[-2]))
        if time_2 - time_1 <= 90:
            bot_restart_time += 1
            startDiscordBot()
        else:
            bot_restart_time = 1
            startDiscordBot()

def get_url(string):
    url = re.findall(r'url=([^);]+)', string)
    return url
def get_cq_images(string):
    cq_images = re.findall(r'\[CQ:image.*?\]', string)
    return cq_images
async def send_message_with_files(file_paths,name,content,channel,uid):
    async with httpx.AsyncClient() as client:
        files = []
        ix = 0
        for f in file_paths:
            files.append((f"file{ix}",(f"image{ix}.jpg", (await client.get( url = f )).content, "image/jpeg")))
            ix += 1
        await client.post(
            url = f"https://discord.com/api/v10/channels/{channel}/messages",
            headers = {
                "Authorization": f"Bot {TOKEN}"
            },
            data = {
                "content": f"{avatar(uid)}<{name}> {content}"
            },
            files = files
        )

def replace_cq_at_with_ids(msg):
    pattern = r"\[CQ:at,qq=(\d+)\]"
    ids = json.load(open(qq_bind_file_2,"r"))
    def replace_id(match):
        id_str = match.group(1)
        if id_str in ids:
            return f"<@{ids[id_str]}>"
        else:
            return match.group(0)
    replaced_msg = re.sub(pattern, replace_id, msg)
    return replaced_msg
def replace_ids_with_cq_at(msg):
    pattern = r'<@(\d+)>'
    ids = json.load(open(qq_bind_file,"r"))
    def replace_id(match):
        id_to_replace = match.group(1)
        return f'[CQ:at,qq={ids.get(id_to_replace, id_to_replace)}]'
    replaced_msg = re.sub(pattern, replace_id, msg)
    return replaced_msg
@nonebot.on_message().handle()
async def _(matcher: Matcher,
        bot: Bot,
        event: GroupMessageEvent):
    try:
        if event.group_id == QQ_ID:
            channel = CHANNEL_ID
        elif event.group_id == QQ_ID_GH:
            channel = CHANNEL_ID_GH
        else:
            return
    except:
        return
    msg = replace_cq_at_with_ids(process_text(str(event.get_message())))
    uid = event.get_user_id()
    msg_nocq = copy.deepcopy(msg)
    for i in get_cq_images(msg):
        msg_nocq = msg_nocq.replace(i,"[图片]")
    images = get_url(msg)
    if len(images) == 0:
        await send_message(f"{avatar(uid)}<{event.sender.nickname}> {msg_nocq}",channel)
    else:
        await send_message_with_files(images,event.sender.nickname,msg_nocq,channel,uid)
@nonebot.on_message().handle()
async def _(matcher: Matcher, bot: Bot):
    global already_start_discord_bot
    if not already_start_discord_bot:
        global gbot
        gbot = bot
        already_start_discord_bot = True
        threading.Thread(target=startDiscordBot).start()
        matcher.destroy()
@nonebot.on_command("dmb").handle()
async def _(matcher: Matcher,
        bot: Bot,
        event: GroupMessageEvent,
        args: Message = CommandArg()):
    global temp_bind_qq, temp_bind_dis, bot_restart_time, dcclient
    try:
        if event.group_id == QQ_ID:
            channel = CHANNEL_ID
        elif event.group_id == QQ_ID_GH:
            channel = CHANNEL_ID_GH
        else:
            return
    except:
        return
    args = args.extract_plain_text().strip().split(" ")
    if args[0] == "bind":
        try:
            token = args[1]
        except:
            if dis_id := get_qq_bind_discord(event.get_user_id()):
                await matcher.finish(f"你已绑定 Discord({dis_id})",at_sender=True)
            await matcher.finish(f"你还未绑定 Discord, 请到消息转发频道下发送「~bind <uid>」进行绑定", at_sender=True)
        if token in temp_bind_dis and temp_bind_qq[event.get_user_id()] == token:
            set_qq_bind(temp_bind_dis[token],event.get_user_id())
            await send_message(f"<@{temp_bind_dis[token]}> QQ `{event.get_user_id()}` 绑定成功",channel)
            del temp_bind_qq[event.get_user_id()]
            del temp_bind_dis[token]
            await matcher.finish(f"Discord 绑定成功",at_sender=True)
        else:
            await matcher.finish("绑定 token 无效", at_sender=True)
    elif args[0] == "restart":
        if bot_restart_time >= 3:
            bot_restart_time = 0
            threading.Thread(target=startDiscordBot).start()
            await matcher.finish("正在尝试重启转发 Bot",at_sender=True)
        else:
            await matcher.finish("转发 Bot 正常运行中",at_sender=True)
    await matcher.finish("IT Craft Development Team Discord Message Bridge 命令帮助"
                         "\n.dmb bind <token> - 绑定 Discord 账户"
                         "\n.dmb restart - 手动重启转发 Bot (仅在自动重启失败后可用)",at_sender=True)