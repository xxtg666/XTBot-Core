import os
import time

def backup():
    commit_title = time.strftime("Automatically uploaded at %Y-%m-%d %H:%M:%S")
    os.system("git pull")
    os.system("git add *")
    os.system(f"git commit -m \"{commit_title}\"")
    os.system("git push")

if __name__ == "__main__":
    while True:
        backup()
        time.sleep(7200)
