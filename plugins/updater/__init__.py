from nonebot import on_command
from nonebot.permission import SUPERUSER
import subprocess
import time

git_update = on_command(
    "xtbotupdate", aliases={"检查更新","gitupdate","xtbotupd","xtbupd"}, permission=SUPERUSER, block=True
)
@git_update.handle()
async def _():
    await git_update.send(str(subprocess.run("git pull", shell=True, stdout=subprocess.PIPE).stdout.decode()))
    await git_update.finish

git_upload = on_command(
    "xtbotupload", aliases={"gitupload","xtbotupl","xtbupl"}, permission=SUPERUSER, block=True
)
@git_upload.handle()
async def _():
    commit_title = time.strftime("Manually uploaded at %Y-%m-%d %H:%M:%S")
    cmds = [str(subprocess.run("git pull", shell=True, stdout=subprocess.PIPE).stdout.decode()),
            str(subprocess.run("git add *", shell=True, stdout=subprocess.PIPE).stdout.decode()),
            str(subprocess.run(f"git commit -m \"{commit_title}\"", shell=True, stdout=subprocess.PIPE).stdout.decode()),
            str(subprocess.run("git push", shell=True, stdout=subprocess.PIPE).stdout.decode())]
    await git_upload.send("\n".join(cmds))
    await git_upload.finish()
