import json
import os
import time
from openai import OpenAI
from datetime import datetime
import traceback
from .gh_utils import GithubUtils

DATA_DIR = "data/chatgpt3"
CONFIG = json.load(open(os.path.join(DATA_DIR, "config.json"), "r"))
USERS = json.load(open(os.path.join(DATA_DIR, "users.json"), "r"))
gh = GithubUtils()

def gen_data_file_path(uid: str) -> str:
    return os.path.join(DATA_DIR, "chat_history", f"{uid}.json")


def set_chat_history(uid: str, messages: list) -> list:
    data_file_path = gen_data_file_path(uid)
    json.dump(messages, open(data_file_path, "w"))
    return messages


def get_chat_history(uid: str) -> list:
    data_file_path = gen_data_file_path(uid)
    if os.path.exists(data_file_path):
        return json.load(open(data_file_path, "r"))
    else:
        return set_chat_history(uid, [])


def append_chat_history(uid: str, message: dict) -> list:
    messages = get_chat_history(uid)
    messages.append(message)
    return set_chat_history(uid, messages)


def get_model(uid: str, model: str) -> dict:
    model_json = CONFIG["public_models"].get(model, None)
    if (model_json is None) and (uid in USERS["advance"]):
        model_json = CONFIG["advanced_models"].get(model, None)
    return model_json


USER_MODEL = {}


def set_user_model(uid: str, model: str) -> str:
    USER_MODEL[uid] = {"model": model, "expire": int(time.time()) + 1800}
    return model


def get_user_model(uid: str) -> str:
    if uid not in USER_MODEL:
        return CONFIG["default_model"]
    if USER_MODEL[uid]["expire"] < time.time():
        del USER_MODEL[uid]
        return CONFIG["default_model"]
    return set_user_model(uid, USER_MODEL[uid]["model"])


def get_used_model() -> dict:
    used_model = json.load(open(os.path.join(DATA_DIR, "used.json"), "r"))
    if datetime.now().strftime("%Y-%m-%d") != used_model["date"]:
        used_model["date"] = datetime.now().strftime("%Y-%m-%d")
        used_model["models"] = {}
        json.dump(used_model, open(os.path.join(DATA_DIR, "used.json"), "w"))
    return used_model


def update_used_model(model: str) -> dict:
    used_model = get_used_model()
    if model not in used_model["models"]:
        used_model["models"][model] = 0
    used_model["models"][model] += 1
    json.dump(used_model, open(os.path.join(DATA_DIR, "used.json"), "w"))
    return used_model


def send_message(uid: str, message: str, model: str) -> str:
    if uid in USERS["banned"]:
        return "您已被封禁"
    model_json = get_model(uid, model)
    client = OpenAI(
        base_url=CONFIG["endpoints"][model_json["endpoint"]]["url"],
        api_key=CONFIG["endpoints"][model_json["endpoint"]]["key"],
    )

    messages = append_chat_history(uid, {"role": "user", "content": message})
    issue_num = gh.create_new_task(uid, model, messages[:-1], message)
    try:
        response = client.chat.completions.create(
            messages=messages,
            model=model
        )
        append_chat_history(uid, {"role": "assistant", "content": response.choices[0].message.content})
        update_used_model(model)
        gh.end_task(issue_num, response.choices[0].message.content)
    except:
        gh.end_task(issue_num, traceback.format_exc().split("\n")[-2])
        return "请求失败: " + traceback.format_exc().split("\n")[-2]
    return response.choices[0].message.content