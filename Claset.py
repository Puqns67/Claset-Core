#VERSION=0
#
#Claset.py
#测试函数Claset
#

import Claset
Logger = Claset.Base.Logs.Logs()
dm = Claset.Base.Download.downloadmanager(DoType="Start", Logger=Logger)
asstets = Claset.Game.Loadjson.AssetsIndex("$PREFIX\\1.16.json")
ass = dm.add(asstets)
if dm.Project_join(ass) != 0:
    dm.Project_join(dm.Retry())
