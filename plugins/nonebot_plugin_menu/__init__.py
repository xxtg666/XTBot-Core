import nonebot

answer = f"""命令列表 —— XTBot

[√]    命令列表              (menu)          
[√]    随机图片              (setu)          
[*]    群文件直链           (link)
[√]    投骰子                (rd)
[√]    插件列表              (help)
[√]    系统信息              (status)
[√]    wolfram计算器         (calc)
[√]    拉格朗日插值计算      (li)
[√]    ChatGPT              (cg)

* 为部分群可用
"""

help_ = nonebot.on_command("help",aliases={"menu"})
@help_.handle()
async def _():
    await help_.finish(answer)
