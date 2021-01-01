#VERSION=0
#
#Claset.py
#测试函数Claset
#

import Claset, time
nowtime = time.time()
dm = Claset.Base.Download.downloadmanager("Start")
asstets = Claset.Game.Loadjson.AssetsIndex("$PREFIX\\1.16.json")
ass = dm.add(asstets)
dm.Project_join(ass)
print(dm.Projects, time.time() - nowtime)