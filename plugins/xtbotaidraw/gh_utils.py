from github import Github, Auth
import time
import os
import httpx

os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

class GITHUB_UTILS:
    def __init__(self):
        self.gh = Github(auth=Auth.Token("")) # 非公开内容
        self.repo = self.gh.get_repo("") # 非公开内容
    def createNewTask(self, user_id: str, model: str, prompt: str) -> int:
        prompt_short = prompt[0:20]
        prompt_no_endl = prompt.replace("\n",r"\n")
        t = int(time.time())
        issue_title = f"[AIDraw] {user_id}: {prompt_short}{'' if prompt_short == prompt else '...'}"
        issue_body = f"{t}\n{user_id}\n{model}\n{prompt_no_endl}"
        return self.repo.create_issue(title=issue_title, body=issue_body).number
    def endTask(self, issue_number: int, answer: str, image: bool = False) -> int:
        issue = self.repo.get_issue(issue_number)
        t = int(time.time())
        if image:
            issue.create_comment(f"{t}\n![]({answer})")
        else:
            answer_no_endl = answer.replace("\n", r"\n")
            issue.create_comment(f"{t}\n{answer_no_endl}")
        issue.edit(state="closed")
        return issue_number

class SMMS_UTILS:
    def __init__(self):
        self.headers = {'Authorization': ''} # 非公开内容
    async def upload(self, image_bytes: bytes) -> str:
        filepath = f"data/xtbotaidraw/temp.{time.time()}.png"
        open(filepath, 'wb').write(image_bytes)
        files = {'smfile': open(filepath, 'rb')}
        url = 'https://smms.app/api/v2/upload'
        async with httpx.AsyncClient() as client:
            response = await client.post(url, files= files, headers= self.headers)
        os.remove(filepath)
        return response.json()['data']['url']