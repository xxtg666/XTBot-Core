from nonebot.adapters import Bot, Event, Message
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot import logger
from nonebot.typing import T_State
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from nonebot.exception import FinishedException
from nonebot import on_command
import traceback
import asyncio
import httpx

lr = on_command("lr")
API_KEY = "6666666666"

@lr.handle()
async def _(bot: Bot, event: Event, matcher: Matcher, state: T_State, arg: Message = CommandArg()):
    arg = arg.extract_plain_text().strip()
    if not arg:
        await lr.finish("[错误] 请输出要朗读的文本", at_sender=True)
    try:
        async with httpx.AsyncClient() as client:
            header = {"Authorization": "Bearer "+API_KEY}
            task = await client.post("https://v1.reecho.cn/api/tts/generate",
                              headers=header,
                              json={
                                  "contents": [
                                      {
                                          "voiceId": "6e2463c6-ccff-4d12-b6bf-d5ab9ec65573",
                                          "text": i,
                                      } for i in arg.split("\n")
                                  ]
                              })
            if task.status_code != 200:
                await lr.finish(f"[错误] 生成失败, 状态码: {task.status_code}", reply=True)
            task = task.json()
            logger.info(task)
            task_id = task["data"]["id"]
            task_status = task["data"]["status"]
            while task_status != "generated":
                if task_status == "failed":
                    await lr.finish(f"[错误] 生成失败", reply=True)
                await asyncio.sleep(5)
                task = await client.get(f"https://v1.reecho.cn/api/tts/generate/{task_id}", headers=header)
                if task.status_code != 200:
                        await lr.finish(f"[错误] 生成失败, 状态码: {task.status_code}", reply=True)
                task = task.json()
                logger.info(task)
                task_status = task["data"]["status"]
            record_url = task["data"]["metadata"]["audio"]
            record = (await client.get(record_url)).read()
    except FinishedException:
        pass
    except Exception as e:
        exc = traceback.format_exc().split('\n')[-2]
        logger.error(traceback.format_exc())
        await lr.finish(f"[未知错误] {exc}", reply=True)
    await lr.send(MessageSegment.record(record))