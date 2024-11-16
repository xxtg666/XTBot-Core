import nonebot
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from .utils import *
import httpx
import json

c = nonebot.on_command("c", aliases={"chat", "cg"})


async def chat_help() -> str:
    return '''[XTBotChatGPTv3] 使用帮助:\n
.c help - 显示帮助信息
.c reset - 重置对话
.c editor - 编辑对话
.c retry - 重试
.c model - 切换模型
.c <message> - 发送消息\n
◈ 查看请求状态 https://xtbot-status.xxtg666.top/
'''


async def chat_editor(uid: str, arg: list) -> str:
    async with httpx.AsyncClient() as client:
        if len(arg) == 1:
            url = "https://xtbot-editor-api.xxtg666.top/upload"
            response = await client.post(url, json=get_chat_history(uid))
            data = response.text
            if data.startswith("ERR"):
                return data
            return "聊天记录已上传至网页编辑器\nhttps://xtbot-editor.xxtg666.top/?id=" + data
        if len(arg) == 2:
            url = "https://xtbot-editor-api.xxtg666.top/get/" + arg[1]
            response = await client.get(url)
            data = response.text
            if data.startswith("ERR"):
                return data
            set_chat_history(uid, json.loads(data))
            return "聊天记录已更新"
    return "参数错误"


async def chat_reset(uid: str, arg: str) -> str:
    arg = arg.replace("reset", "", 1).strip()
    if not arg:
        set_chat_history(uid, [])
    else:
        set_chat_history(uid, [{"role": "system", "content": arg}])
    return "对话已重置"


async def chat_send(uid: str, arg: str) -> str:
    model = get_user_model(uid)
    answer = send_message(uid, arg, model)
    return f"◈ {model} | {len(get_chat_history(uid))}\n\n{answer}"


async def chat_retry(uid: str) -> str:
    messages = get_chat_history(uid)
    if len(messages) <= 1:
        return "请先发送消息"
    messages.pop(-1)
    message = messages.pop(-1)
    set_chat_history(uid, messages)
    model = get_user_model(uid)
    answer = send_message(uid, message["content"], model)
    return f"◈ {model} | {len(get_chat_history(uid))}\n\n{answer}"


async def chat_model(uid: str, arg: list) -> str:
    if len(arg) == 1:
        reply = f"当前模型: {get_user_model(uid)}\n\n"
        used = get_used_model()["models"]
        for model in CONFIG["public_models"]:
            reply += f"{model} ({used.get(model, 0)}/{CONFIG['public_models'][model]['limit']})\n"
        if uid in USERS["advance"]:
            for model in CONFIG["advanced_models"]:
                reply += f"{model} ({used.get(model, 0)}/{CONFIG['advanced_models'][model]['limit']})\n"
        reply += "\n切换模型: .c model <name>"
        return reply
    if len(arg) == 2:
        model = arg[1]
        if model in CONFIG["public_models"]:
            return "模型已切换至 " + set_user_model(uid, model)
        if model in CONFIG["advanced_models"] and uid in USERS["advance"]:
            return "模型已切换至 " + set_user_model(uid, model)
        return "模型不存在"
    return "参数错误"

@c.handle()
async def _(matcher: Matcher,
            bot: Bot,
            event: Event,
            args: Message = CommandArg()):
    args = args.extract_plain_text().strip()
    parsed = args.split(" ")
    uid = event.get_user_id()
    if not args:
        await c.finish(await chat_help(), at_sender=True)
    match parsed[0]:
        case "help":
            await c.finish(await chat_help(), at_sender=True)
        case "editor":
            await c.finish(await chat_editor(uid, parsed), at_sender=True)
        case "reset":
            await c.finish(await chat_reset(uid, args), at_sender=True)
        case "retry":
            await c.finish(await chat_retry(uid), at_sender=True)
        case "model":
            await c.finish(await chat_model(uid, parsed), at_sender=True)
        case _:
            await c.finish(await chat_send(uid, args), at_sender=True)
