#VERSION=0
#
#Claset.py
#测试函数Claset
#


import Claset, time

LogHeader = ["Claset/Main"]

StartTime = time.time()
Logger = Claset.Base.Logs.Logs()
Logger.GenLog(Perfixs=LogHeader, Text="Started!!!")
Downloader = Claset.Base.Download.DownloadManager(Logger=Logger)
AssetsIndex = Claset.Game.Loadjson.AssetsIndex("./1.17.json")
try:
    Downloader.Project_join(Downloader.Add_tasks(AssetsIndex))
except KeyboardInterrupt:
    Downloader.Stop()
Logger.GenLog(Perfixs=LogHeader, Text="Stopped!!!")
Logger.GenLog(Perfixs=LogHeader, Text="Used time: " + str(time.time() - StartTime))
