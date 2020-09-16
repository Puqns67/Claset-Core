#
#ui.py
#主操作函数
#

#必要包
import os
import os.path
import time

#函数
def basecheck():       #基础检测
    check = os.path.exists("CPML")
    if check == False:
        print("Error: CPML folder not found!")
        print("       Program will to Stop!")
        time.sleep(5)
        exit()
    check = os.path.exists("CPML.json")
    if check == False:
        import json
        DefaultConfig = {'FileVersion': 3, 'Settings': {'VersionSeparation': False, 'Memory': 2048, 'CheckUpdate': True, 'DefaultPath': {'Cache': 'CPML/Cache', 'Minecraft': '.minecraft', 'Assets': '.minecraft/assets', 'Libraries': '.minecraft/libraries', 'Version': '.minecraft/versions'}}, 'User': [], 'DEBUG': True}
        jsonConfig = json.dumps(DefaultConfig, indent=4, ensure_ascii=False)
        with open("CPML.json", mode="w+") as w:
            w.write(jsonConfig)


#UI_Terminal
#启动前执行
basecheck()
UIVeesio = 0

#基础包
import CPML.Tools
import CPML.User
import platform


#基础命值
Config = CPML.Tools.loadjson("CPML.json")
PlatformOS = platform.system()
SetupCwd = os.getcwd()

#user
#CPML.User.list(Config)
#Config["User"] = CPML.User.create(usertype, name, Config, password)
#Config["User"] = CPML.User.remove(name, Config)
users = CPML.User.listt(Config)
print(users)
exit()

if Config["Settings"]["DefaultPath"]["Minecraft"][0] == True:
    MinecraftDir = SetupCwd + "/" + Config["Settings"]["DefaultPath"]["Minecraft"][1]
else:
    MinecraftDir = Config["Settings"]["DefaultPath"]["Minecraft"][1]
CPML.Tools.dfcheck("objects_dir", MinecraftDir, None)
loadeddict = CPML.Tools.loadjson("1.12.2.json", "MCver", PlatformOS)
from queue import Queue
loadedqueue = Queue(maxsize=0)
for ii in range(len(loadeddict)):
    loadedqueue.put(loadeddict[ii])


##Downloads
#import CPML.Downloads
#import queue
#import urllib

exit()


