#VERSION=0
#
#Claset.py
#测试函数Claset
#


import Claset

LogHeader = ["Claset/Main"]

Logger = Claset.Base.Logs.Logs()
Logger.GenLog(Perfixs=LogHeader, Text="Started!!!")
Downloader = Claset.Base.Download.downloadmanager(DoType="Start", Logger=Logger)
AssetsIndex = Claset.Game.Loadjson.AssetsIndex("./1.17.json")
Downloader.Project_join(Downloader.add(AssetsIndex))
Downloader.StopService()
Logger.GenLog(Perfixs=LogHeader, Text="Stopped!!!")
