import nonebot
import traceback
import base64
import httpx
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.message import Message, MessageSegment

def get_image_base64(text):
    text = text.replace("\\","\\\\")
    response = httpx.post("https://api.github.com/markdown", json = {"text": text})
    text = response.text
    try:
        response = httpx.post("http://127.0.0.1:6789/html/img", data = {"html": text, "github-markdown": True, "timeout": 1000}) # 非公开内容(xxtg666/XT-api 服务器地址)
    except:
        response = httpx.post("http://127.0.0.1:6789/html/img", data = {"html": text, "github-markdown": True, "timeout": 1000}) # 非公开内容(xxtg666/XT-api 服务器地址)
    return response.json()["image_base64"]

md = nonebot.on_command("md")
@md.handle()
async def _(matcher: Matcher,
        bot: Bot,
        event: Event,
        args: Message = CommandArg()):
    try:
        image_base64 = get_image_base64(args.extract_plain_text().strip())
        msg = Message(MessageSegment.image(base64.b64decode(image_base64)))
        await md.finish(msg,at_sender=True)
    except:
        e = traceback.format_exc()
        if "FinishedException" not in e:
            await md.finish("图片渲染失败!\n"+e,at_sender=True)