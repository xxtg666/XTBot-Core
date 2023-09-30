import nonebot
import os
import time
import traceback
import openai
from .gh_utils import GITHUB_UTILS, SMMS_UTILS
from .de_utils import USER_DATA_UTILS, DALLE_UTILS
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11.message import Message, MessageSegment

os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

gh = GITHUB_UTILS()
smms = SMMS_UTILS()
ud = USER_DATA_UTILS()
dalle = DALLE_UTILS()
prefix = " [XTBotAIDraw]\n"

de = nonebot.on_command("de")
@de.handle()
async def _(matcher: Matcher,
        bot: Bot,
        event: Event,
        args: Message = CommandArg()):
    args = args.extract_plain_text().strip()
    uid = event.get_user_id()
    match args.split(" ")[0]:
        case "help":
            await de.finish('''[XTBotAIDraw] 使用帮助: \n
.de help - 查看此帮助
.de error - 查看上一次报错信息
.de credit - 查看你剩余的 credit 数量
.de large <prompt> - 生成一张1024×1024的图片(消耗4credit)
.de medium <prompt> - 生成一张512×512的图片(消耗2credit)
.de small <prompt> - 生成一张256×256的图片(消耗1credit)
.de <prompt> - 生成一张256×256的图片(消耗1credit)\n
◈ 查看请求状态 https://xtbot-status.xxtg666.top/''', at_sender=True)
        case "error":
            err = ud.getUserCachedErr(uid)
            if err["last_err_time"] == 0:
                await de.finish(prefix + "最近没有发生错误", at_sender=True)
            time_info = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(err['last_err_time']))
            await de.finish(prefix + f"在 {time_info} 发生的错误详细信息:\n" + err["err_info"], at_sender=True)
        case "credit":
            user_info = ud.getUserInfo(uid)
            credits = user_info['credits']
            used_credits = user_info['used_credits']
            all_credits = credits + used_credits
            await de.finish(prefix + f"剩余 credit 查询\n"
                                     f"总量: {all_credits}\n"
                                     f"已用: {used_credits}\n"
                                     f"剩余: {credits}",
                            at_sender=True)
        case "large":
            user_info = ud.getUserInfo(uid)
            if user_info["credits"] < 4:
                await de.finish(prefix + "你的 credit 数量不足", at_sender=True)
            prompt = args.replace("large ", "", 1)
            try:
                issue_number = gh.createNewTask(uid, "DALL-E", prompt)
            except:
                ud.setUserCachedErr(uid, err := traceback.format_exc())
                await de.finish(prefix + "发生错误:\n" + err.split("\n")[-2], at_sender=True)
            try:
                r = await dalle.getDALLE(prompt, user_info, 4)
            except:
                ud.setUserCachedErr(uid, err := traceback.format_exc())
                gh.endTask(issue_number, err)
                await de.finish(prefix+"发生错误:\n"+err.split("\n")[-2],at_sender=True)
            if r[0]:
                gh.endTask(issue_number, await smms.upload(image := dalle.b64decodeImage(r[1])), True)
                user_info["credits"] -= 4
                user_info["used_credits"] += 4
                user_info["last_use_time"] = time.time()
                ud.setUserInfo(uid, user_info)
                await de.finish(Message(MessageSegment.image(image)), reply_message=True)
            else:
                await de.finish(prefix + r[1], at_sender=True)
        case "medium":
            user_info = ud.getUserInfo(uid)
            if user_info["credits"] < 2:
                await de.finish(prefix + "你的 credit 数量不足", at_sender=True)
            prompt = args.replace("medium ", "", 1)
            try:
                issue_number = gh.createNewTask(uid, "DALL-E", prompt)
            except:
                ud.setUserCachedErr(uid, err := traceback.format_exc())
                await de.finish(prefix + "发生错误:\n" + err.split("\n")[-2], at_sender=True)
            try:
                r = await dalle.getDALLE(prompt, user_info, 2)
            except:
                ud.setUserCachedErr(uid, err := traceback.format_exc())
                gh.endTask(issue_number, err)
                await de.finish(prefix + "发生错误:\n" + err.split("\n")[-2], at_sender=True)
            if r[0]:
                gh.endTask(issue_number, await smms.upload(image := dalle.b64decodeImage(r[1])), True)
                user_info["credits"] -= 2
                user_info["used_credits"] += 2
                user_info["last_use_time"] = time.time()
                ud.setUserInfo(uid, user_info)
                await de.finish(Message(MessageSegment.image(image)), reply_message=True)
            else:
                await de.finish(prefix + r[1], at_sender=True)
        case "small":
            user_info = ud.getUserInfo(uid)
            if user_info["credits"] < 1:
                await de.finish(prefix + "你的 credit 数量不足", at_sender=True)
            prompt = args.replace("small ", "", 1)
            try:
                issue_number = gh.createNewTask(uid, "DALL-E", prompt)
            except:
                ud.setUserCachedErr(uid, err := traceback.format_exc())
                await de.finish(prefix + "发生错误:\n" + err.split("\n")[-2], at_sender=True)
            try:
                r = await dalle.getDALLE(prompt, user_info, 1)
            except:
                ud.setUserCachedErr(uid, err := traceback.format_exc())
                gh.endTask(issue_number, err)
                await de.finish(prefix + "发生错误:\n" + err.split("\n")[-2], at_sender=True)
            if r[0]:
                gh.endTask(issue_number, await smms.upload(image := dalle.b64decodeImage(r[1])), True)
                user_info["credits"] -= 1
                user_info["used_credits"] += 1
                user_info["last_use_time"] = time.time()
                ud.setUserInfo(uid, user_info)
                await de.finish(Message(MessageSegment.image(image)), reply_message=True)
            else:
                await de.finish(prefix + r[1], at_sender=True)
        case "":
            await de.finish(prefix + "使用 .de help 查看命令帮助", at_sender=True)
        case _:
            user_info = ud.getUserInfo(uid)
            if user_info["credits"] < 1:
                await de.finish(prefix + "你的 credit 数量不足", at_sender=True)
            prompt = args
            try:
                issue_number = gh.createNewTask(uid, "DALL-E", prompt)
            except:
                ud.setUserCachedErr(uid, err := traceback.format_exc())
                await de.finish(prefix + "发生错误:\n" + err.split("\n")[-2], at_sender=True)
            try:
                r = await dalle.getDALLE(prompt, user_info, 1)
            except:
                ud.setUserCachedErr(uid, err := traceback.format_exc())
                gh.endTask(issue_number, err)
                await de.finish(prefix + "发生错误:\n" + err.split("\n")[-2], at_sender=True)
            if r[0]:
                gh.endTask(issue_number, await smms.upload(image := dalle.b64decodeImage(r[1])), True)
                user_info["credits"] -= 1
                user_info["used_credits"] += 1
                user_info["last_use_time"] = time.time()
                ud.setUserInfo(uid, user_info)
                await de.finish(Message(MessageSegment.image(image)), reply_message=True)
            else:
                await de.finish(prefix + r[1], at_sender=True)

de_ = nonebot.on_command("de*")
@de_.handle()
async def _(matcher: Matcher,
        bot: Bot,
        event: Event,
        args: Message = CommandArg()):
    args = args.extract_plain_text().strip().split(" ")
    if event.get_user_id() != "1747433912":
        await de_.finish(prefix+"无权限使用管理员命令",at_sender=True)
    match args[0]:
        case "help":
            await de_.finish('''[XTBotAIDraw] 管理员命令使用帮助: \n
.de* help - 查看此帮助
.de* initall <credit> - 为本群所有用户初始化数据
.de* time <uid> - 查看用户最后一次使用时间
.de* error <uid> - 查看用户的上一次报错信息
.de* credit <uid> - 查看用户剩余的 credit 数量
.de* addcredit <uid> <credit> - 为用户添加 credit
.de* ban <uid> - 封禁用户
.de* pardon <uid> - 解封用户
.de* apikey <apikey> - 设置 api key
.de* apibase <apibase> - 设置 api base''', at_sender=True)
        case "initall":
            init_credit = int(args[1])
            user_list = await bot.get_group_member_list(group_id=event.group_id)
            reply = [f"正在初始化群聊 {event.group_id} 用户数据\n初始 Credits 为 {init_credit}"]
            for user in user_list:
                user_id = str(user["user_id"])
                if ud._checkUser(user_id, init_credit):
                    reply.append(user_id + " 数据已存在")
                else:
                    reply.append(user_id + " 数据初始化完成")
            await de_.finish(prefix + "\n".join(reply), at_sender=True)
        case "time":
            user_info = ud.getUserInfo(uid := args[1])
            last_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(user_info["last_use_time"]))
            await de_.finish(prefix + uid + " 最后一次使用时间: " + last_time, at_sender=True)
        case "error":
            err = ud.getUserCachedErr(uid := args[1])
            if err["last_err_time"] == 0:
                await de_.finish(prefix + uid + " 最近没有发生错误", at_sender=True)
            time_info = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(err['last_err_time']))
            await de_.finish(prefix + uid + f" 在 {time_info} 发生的错误详细信息:\n" + err["err_info"], at_sender=True)
        case "credit":
            user_info = ud.getUserInfo(uid := args[1])
            credits = user_info['credits']
            used_credits = user_info['used_credits']
            all_credits = credits + used_credits
            await de_.finish(prefix + uid + f" 剩余 credit 查询\n"
                                           f"总量: {all_credits}\n"
                                           f"已用: {used_credits}\n"
                                           f"剩余: {credits}",
                            at_sender=True)
        case "addcredit":
            user_info = ud.getUserInfo(uid := args[1])
            user_info["credits"] += (added := int(args[2]))
            ud.setUserInfo(uid, user_info)
            credits = user_info['credits']
            used_credits = user_info['used_credits']
            all_credits = credits + used_credits
            await de_.finish(prefix + f"已为用户 {uid} 添加 {added} credits\n"
                                     f"总量: {all_credits}\n"
                                     f"已用: {used_credits}\n"
                                     f"剩余: {credits}",
                            at_sender=True)
        case "ban":
            ud.modifyUserInfo(uid := args[1], "banned", True)
            await de_.finish(prefix + "已封禁用户 " + uid, at_sender=True)
        case "pardon":
            ud.modifyUserInfo(uid := args[1], "banned", False)
            await de_.finish(prefix + "已解封用户 " + uid, at_sender=True)
        case "apikey":
            ud.modifyConfig("api_key", args[1])
            dalle.refreshConfig()
            await de_.finish(prefix + "完成", at_sender=True)
        case "apibase":
            ud.modifyConfig("api_base", args[1])
            dalle.refreshConfig()
            await de_.finish(prefix + "完成", at_sender=True)