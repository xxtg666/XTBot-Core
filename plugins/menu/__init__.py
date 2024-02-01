import nonebot
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.adapters.onebot.v11 import Bot

answer = f"""命令列表 —— XTBot
[√]    命令列表              (menu)          
[√]    随机图片              (setu)          
[*]    群文件直链           (link)
[√]    投骰子                (rd)
[√]    插件列表              (help)
[√]    系统信息              (status)
[√]    wolfram计算器         (calc)
[√]    ChatGPT              (cg)
* 为部分群可用
开源地址: https://github.com/xxtg666/XTBot-Core
"""

help_ = nonebot.on_command("help",aliases={"menu"})
@help_.handle()
async def _(matcher: Matcher,
        bot: Bot,
        event: Event,
        args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        await help_.finish(answer)
    else:
        await help_.finish()