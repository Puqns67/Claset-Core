#VERSION=0
#
#Main.py
#测试类Claset
#

from sys import path
from os.path import abspath
from time import time
from re import search

path.append(abspath("./"))

import Claset

# 获得当前路径
Cwd = search(r"(.+)[\\/]+.+", __file__).groups()[0]
LogHeader = ["Claset/Main"]

StartTime = time()
Logger = Claset.Base.Logs.Logs(LogHeader=LogHeader)
Logger.genLog(Perfixs=LogHeader, Text="Started!!!")
Downloader = Claset.Base.Download.DownloadManager(Logger=Logger)
AssetsIndex = Claset.Game.Loadjson.AssetsIndex(Cwd + "/DataSource/1.17.json")
try:
    ProjectID = Downloader.addTasks(AssetsIndex)
    Downloader.projectJoin(ProjectID)
except KeyboardInterrupt:
    Downloader.stop()
Logger.genLog(Perfixs=LogHeader, Text="Stopped!!!")
Logger.genLog(Perfixs=LogHeader, Text=["Used time: ", time() - StartTime])

