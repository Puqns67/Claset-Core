#VERSION=0
#
#Claset.py
#测试函数Claset
#

import Claset, time
nowtime = time.time()
Logger = Claset.Base.Logs.Logs()
dm = Claset.Base.Download.downloadmanager(DoType="Start", Logger=Logger)
asstets = Claset.Game.Loadjson.AssetsIndex("$PREFIX\\1.16.json")
ass = dm.add(asstets)
while True:
    time.sleep(1)
    print(dm.Threads)
    print(dm.Projects)
