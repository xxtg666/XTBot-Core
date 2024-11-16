from github import Github, Auth
import time
import os

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""

class GITHUB_UTILS:
    def __init__(self):
        self.gh = Github(auth=Auth.Token("6666666666"))
        self.repo = self.gh.get_repo("6666666666/6666666666")
    def createNewTask(self, user_id: str, model: str, chat_history: list[dict], prompt: str) -> int:
        prompt_short = prompt[0:20]
        prompt_no_endl = prompt.replace("\n",r"\n")
        t = int(time.time())
        issue_title = f"[ChatGPTv2] {user_id}: {prompt_short}{'' if prompt_short == prompt else '...'}"
        issue_body = f"{t}\n{user_id}\n{model}\n{prompt_no_endl}\n{chat_history}"
        return self.repo.create_issue(title=issue_title, body=issue_body).number
    def endTask(self, issue_number: int, answer: str, tokens: list[int]) -> int:
        issue = self.repo.get_issue(issue_number)
        answer_no_endl = answer.replace("\n",r"\n")
        t = int(time.time())
        issue.create_comment(f"{t}\n{tokens}\n{answer_no_endl}")
        issue.edit(state="closed")
        return issue_number