#VERSION=0
#
#Claset_Test.py
#测试类Claset
#

import Claset, time

LogHeader = ["Claset/Main"]

StartTime = time.time()
Logger = Claset.Base.Logs.Logs(LogHeader=LogHeader)
Logger.genLog(Perfixs=LogHeader, Text="Started!!!")
Downloader = Claset.Base.Download.DownloadManager(Logger=Logger)
AssetsIndex = Claset.Game.Loadjson.AssetsIndex("./1.17.json")
try:
    Downloader.projectJoin(Downloader.addTasks(AssetsIndex))
except KeyboardInterrupt:
    Downloader.stop()
Logger.genLog(Perfixs=LogHeader, Text="Stopped!!!")
Logger.genLog(Perfixs=LogHeader, Text=["Used time: ", time.time() - StartTime])
