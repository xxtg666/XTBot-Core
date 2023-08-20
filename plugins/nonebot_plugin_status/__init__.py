import nonebot
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, Arg
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
import psutil
import os
import getpass

status = nonebot.on_command("status",
        priority = 1,
        aliases = {"状态"}
)
status.__help_name__ = ".status"
status.__help_name__ = "获取服务器状态"
@status.handle()
async def handle_first_receive(matcher: Matcher,
        event: Event,
        args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    at = MessageSegment.at(event.get_user_id())
    
    _cpu = psutil.cpu_percent(interval = 1, percpu = True)
    cpu = [0,0]
    for c in _cpu:
        cpu[0] += c
    cpu[1] = _cpu.__len__() * 100
    _mem = psutil.virtual_memory()
    mem = [int(_mem.used / 1024 / 1024 / 1024 * 100) / 100,
            int(_mem.total / 1024 / 1024 / 1024 * 100) / 100
    ]
    _swp = psutil.swap_memory()
    swp = [
            int(_swp.used / 1024 / 1024 / 1024 * 100 ) / 100,
            int(_swp.total / 1024 / 1024 / 1024 * 100 ) /100
    ]

    answer = f"""运行状态：
CPU：{cpu[0]} / {cpu[1]}%
内存：{mem[0]} / {mem[1]}GB ({psutil.virtual_memory().percent}%)
SWAP：{swp[0]} / {swp[1]}GB
OS：{os.name}
登录用户：{getpass.getuser()}\n
查询XTBotChatGPTv2状态: 
https://xtbot-status.xxtg666.top/
"""

    await matcher.finish(Message(at + "\n" + answer))


