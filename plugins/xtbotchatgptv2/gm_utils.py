import json
import os

class GROUP_MESSAGE_UTILS:
    def __init__(self):
        self.prompt = '''你将得到一串聊天记录.你需要做3件事:
1.对这些记录进行摘要.要求简明扼要,以一段话的形式输出,且不与下面的要点重复.
2.提取这些记录中的要点,尽可能详细,数量为4~10条,尽可能多,逐条输出.
3.提取这些记录中的精华消息,逐条输出,每条格式为:`用户名:用户的消息原文`,输出时不带引号.

聊天记录格式如下:
```
{用户名1}({用户ID1}):
{用户1的消息内容,一行一条}

{用户名2}({用户ID2}):
{用户2的消息内容,一行一条}

```
以此类推

你的输出格式如下:
```
# 摘要
{摘要内容}
# 要点
{用无序列表列出记录中的要点}
# 精华
{用无序列表列出记录中的精华消息}
```

摘要内容、要点、精华消息之间用空行分隔.无需输出三引号.'''
        self.prompt_en = '''You'll get a bunch of chat logs. You need to do 3 things.
1. Summarize these transcripts. It should be concise, in the form of a paragraph, and not repeat the points below.
2. Extract the key points in these records, as detailed as possible, the number of 4 to 10, as many as possible, one by one output.
3. Extract the essence messages in these records and output them one by one, each in the format of `Username:User's message`, without quotation marks.

The format of the chat logs is as follows:
```
{username1}({userid1}):
{user1's messages, one line at a time}

{username2}({userid2}):
{User2's message, one line at a time}

```
and so on.

You should output in the following format:
```
# 摘要
{summary content}
# 要点
{list the key points in an list}
# 精华
{listing the essence messages in an list}
```

Separate 摘要(summary), 要点(key points), and 精华消息(essence messages) with a blank line. There is no need to output triple quotes.
Reply me in Chinese.'''
        self._makeDir("data/cg_group_message_history")
    def _makeDir(self,dir_name: str) -> bool:
        try:
            os.mkdir(dir_name)
            return True
        except:
            return False
    def getMessageHistory(self, gid: str) -> list:
        if os.path.exists(f"data/cg_group_message_history/{gid}.json"):
            return json.load(open(f"data/cg_group_message_history/{gid}.json","r"))
        return []
    def setMessageHistory(self, gid: str, message_history: list) -> list:
        json.dump(message_history, open(f"data/cg_group_message_history/{gid}.json", "w"))
        return message_history
    def appendMessageHistory(self, gid: str, uid: str, nickname: str, content: str) -> list:
        message_history = self.getMessageHistory(gid)
        if not message_history:
            message_history = [[[uid,nickname],[content]]]
            self.setMessageHistory(gid, message_history)
            return message_history
        if self.calcMessageHistoryLength(message_history) >= 300:
            message_history[0][1].pop(0)
            if not message_history[0][1]:
                message_history.pop(0)
        if message_history[-1][0][0] == uid:
            message_history[-1][1].append(content)
            self.setMessageHistory(gid, message_history)
            return message_history
        else:
            message_history.append([[uid,nickname],[content]])
            self.setMessageHistory(gid, message_history)
            return message_history
    def calcMessageHistoryLength(self, message_history: list) -> int:
        length = 0
        for message in message_history:
            length += len(message[1])
        return length
    def tempDelMessageHistory(self, message_history: list, to_num: int) -> list:
        origin_num = self.calcMessageHistoryLength(message_history)
        del_num = origin_num - to_num
        if del_num <= 0:
            return message_history
        for i in range(del_num):
            message_history[0][1].pop(0)
            if not message_history[0][1]:
                message_history.pop(0)
        return message_history