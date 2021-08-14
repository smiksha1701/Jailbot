import shutil
import os
safelist=["lib",'bot.py','clearup.py','.git',"README.md"]
path=os.path.abspath(os.getcwd())
for i in os.listdir():
    if i not in safelist:
        try:
            shutil.rmtree(i)
        except: os.remove(i)