import os
import json
from openai import OpenAI
import tiktoken
import httpx
import time
import datetime
import pandas

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""

class USER_DATA_UTILS:
    def __init__(self):
        self._makeDir("data/chatgpt2")
        self._makeDir("data/chatgpt2/chat_history")
        self._makeDir("data/chatgpt2/user_info")
        self._makeDir("data/chatgpt2/cached_err")
        self._makeDir("data/chatgpt2/user_sign")
        if not os.path.exists("data/chatgpt2/config.json"):
            json.dump({
                "api_key":"6666666666",
                "api_base":"https://example.com",
                "api_key_4":"6666666666",
                "api_base_4":"https://example.com",
                "free": "false"
            },open("data/chatgpt2/config.json","w"))
    def _makeDir(self,dir_name: str) -> bool:
        try:
            os.mkdir(dir_name)
            return True
        except:
            return False
    def _checkUser(self, user_id: str, setup_init_token: int = 1000) -> bool:
        if os.path.exists(f"data/chatgpt2/user_sign/{user_id}.json"):
            return True
        self._setupUserData(user_id, setup_init_token)
        return False
    def _setupUserData(self, user_id: str, init_token: int = 1000) -> str:
        if not os.path.exists(f"data/chatgpt2/chat_history/{user_id}.json"):
            json.dump([],open(f"data/chatgpt2/chat_history/{user_id}.json","w"))
        if not os.path.exists(f"data/chatgpt2/user_info/{user_id}.json"):
            json.dump({
                "user_id":user_id,
                "tokens":init_token,
                "used_tokens":0,
                "last_use_time":0,
                "banned":False,
                "allow_gpt4":False,
                "need_review":False
            }, open(f"data/chatgpt2/user_info/{user_id}.json", "w"))
        if not os.path.exists(f"data/chatgpt2/cached_err/{user_id}.json"):
            json.dump({
                "last_err_time":0,
                "err_info":""
            }, open(f"data/chatgpt2/cached_err/{user_id}.json", "w"))
        if not os.path.exists(f"data/chatgpt2/user_sign/{user_id}.json"):
            json.dump({
                "sign_day_list": [],
                "sign_days": 0,
                "last_sign_day": "",
                "continuous_sign_days": 0,
                "tokens_get_by_sign": 0
            }, open(f"data/chatgpt2/user_sign/{user_id}.json", "w"))
        return user_id
    def getUserChatHistory(self, user_id: str) -> list:
        self._checkUser(user_id)
        return json.load(open(f"data/chatgpt2/chat_history/{user_id}.json","r"))
    def getUserInfo(self, user_id: str) -> dict:
        self._checkUser(user_id)
        return json.load(open(f"data/chatgpt2/user_info/{user_id}.json", "r"))
    def getUserCachedErr(self, user_id: str) -> dict:
        self._checkUser(user_id)
        return json.load(open(f"data/chatgpt2/cached_err/{user_id}.json", "r"))
    def setUserChatHistory(self, user_id: str, chat_history: list) -> list:
        json.dump(chat_history, open(f"data/chatgpt2/chat_history/{user_id}.json", "w"))
        return chat_history
    def appendUserChatHistory(self, user_id: str, chat_history: list) -> list:
        origin_chat_history = self.getUserChatHistory(user_id)
        origin_chat_history.extend(chat_history)
        return self.setUserChatHistory(user_id, origin_chat_history)
    def setUserInfo(self, user_id: str, user_info: dict) -> dict:
        json.dump(user_info,open(f"data/chatgpt2/user_info/{user_id}.json", "w"))
        return user_info
    def modifyUserInfo(self, user_id: str, key: str, value: any) -> dict:
        origin_user_info = self.getUserInfo(user_id)
        origin_user_info[key] = value
        return self.setUserInfo(user_id, origin_user_info)
    def setUserCachedErr(self, user_id: str , err: str) -> dict:
        json.dump(cached_err := {
            "last_err_time": time.time(),
            "err_info": err
        }, open(f"data/chatgpt2/cached_err/{user_id}.json", "w"))
        return cached_err
    def getConfig(self) -> dict:
        return json.load(open("data/chatgpt2/config.json", "r"))
    def setConfig(self, config: dict) -> dict:
        json.dump(config, open("data/chatgpt2/config.json", "w"))
        return config
    def modifyConfig(self, key: str, value: str) -> dict:
        origin_config = self.getConfig()
        origin_config[key] = value
        return self.setConfig(origin_config)
    def getUserSign(self, user_id: str) -> dict:
        self._checkUser(user_id)
        return json.load(open(f"data/chatgpt2/user_sign/{user_id}.json", "r"))
    def setUserSign(self, user_id: str, user_sign: dict) -> dict:
        json.dump(user_sign, open(f"data/chatgpt2/user_sign/{user_id}.json", "w"))
        return user_sign
    def modifyUserSign(self, user_id: str, key: str, value: any) -> dict:
        origin_user_sign = self.getUserSign(user_id)
        origin_user_sign[key] = value
        return self.setUserSign(user_id, origin_user_sign)
class WEB_API_UTILS:
    async def getImageBase64(self, html: str) -> str:
        url = "http://example.com"
        try:
            response = httpx.post(url, data = {"html": html, "github-markdown": True, "timeout": 1000})
        except:
            response = httpx.post(url, data = {"html": html, "github-markdown": True, "timeout": 1000})
        return response.json()["image_base64"]
    async def getGithubMarkdown(self, text: str) -> str:
        text = text.replace("\\","\\\\")
        async with httpx.AsyncClient() as client:
            url = "https://api.github.com/markdown"
            response = await client.post(url, json = {"text": text})
            return response.text
    async def getEditorData(self, data_id: str) -> str:
        async with httpx.AsyncClient() as client:
            url = "https://example.com"+data_id
            response = await client.get(url)
            return response.text
    async def uploadEditorData(self, chat_history: list) -> str:
        async with httpx.AsyncClient() as client:
            url = "https://example.com"
            response = await client.post(url, json = chat_history)
            return response.text

class GPT_UTILS:
    def __init__(self):
        self.tiktoken_encoding = tiktoken.get_encoding("cl100k_base")
        self.config = json.load(open("data/chatgpt2/config.json","r"))
    def refreshConfig(self):
        self.config = json.load(open("data/chatgpt2/config.json","r"))
    def countTokens(self, text):
        return len(self.tiktoken_encoding.encode(text))
    def getDefaultModel(self):
        return "glm-4-air" if time.time() >= 6666666666 else "glm-4-plus"
    async def getChatGPT(self, chat_history: list, prompt: str, user_info: dict, model: str = "-", token_multiplier: float = 1.0) -> list:
        if user_info["banned"]:
            return [0,0,[{"role":"XTBot","content":"错误: 你已被禁止使用XTBotChatGPTv2"}]]
        if model == "-":
            model = self.getDefaultModel()
        chat_history.append({"role": "user", "content": prompt})
        message = dict(OpenAI(
            api_key=self.config["api_key"],
            base_url=self.config["api_base"]
        ).chat.completions.create(
            model = model,
            messages = chat_history
        ).choices[0].message)
        # async with httpx.AsyncClient() as client:
        #     data = {
        #         "model": "gpt-3.5-turbo",
        #         "messages": chat_history
        #     }
        #     header = {
        #         "Authorization": f"Bearer {openai.api_key}",
        #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
        #         " Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.69",
        #     }
        #     message = (await client.post(f"{openai.api_base}/chat/completions", json=data, headers=header)).json()
        #     try:
        #         message = message["choices"][0]["message"]
        #     except:
        #         raise openai.error.APIError(message["error"]["message"])
        tokens = len(chat_history)*3
        for m in chat_history:
            tokens += self.countTokens(m["content"])
        chat_history.append(message)
        return [
            int(token_multiplier * (tokens + 3)),
            int(token_multiplier * self.countTokens(message["content"])),
            chat_history
        ]
    async def getGPT4(self, prompt: str, user_info: dict, model: str) -> str:
        if user_info["banned"] or not user_info["allow_gpt4"]:
            return "错误: 无权限"
        return OpenAI(
            api_key=self.config["api_key_4"],
            base_url=self.config["api_base_4"]
        ).chat.completions.create(
            model = model,
            messages = [{"role": "user", "content": prompt}]
        ).choices[0].message.content
        # async with httpx.AsyncClient() as client:
        #     data = {
        #         "model": "gpt-4",
        #         "messages": [{"role": "user", "content": prompt}]
        #     }
        #     header = {
        #         "Authorization": f"Bearer {openai.api_key}",
        #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
        #         " Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.69",
        #     }
        #     message = (await client.post(f"{openai.api_base}/chat/completions", json=data, headers=header)).json()
        #     try:
        #         message = message["choices"][0]["message"]["content"]
        #     except:
        #         raise openai.error.APIError(message["error"]["message"])
        # return message

class DATE_UTILS:
    def getTodayDate(self) -> str:
        return datetime.datetime.now().strftime('%Y-%m-%d')
    def getDateList(self, day_num: int) -> list[str]:
        return pandas.date_range(end=self.getTodayDate().replace("-",""), periods=day_num).strftime("%Y-%m-%d").tolist()
    def getYesterdayDate(self) -> str:
        return self.getDateList(2)[0]
