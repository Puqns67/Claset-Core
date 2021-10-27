#VERSION=0
#
#Claset/Tools/Tests/Main.py
#测试类Claset
#

from sys import path
from os.path import abspath
from time import time
from re import search
from platform import uname

path.append(abspath("./"))

import Claset

def Main():
    # 获得当前路径
    ThisFilePath = search(r"(.+)[\\/]+.+", __file__).groups()[0]
    LogHeader = ["Claset/Main"]

    StartTime = time()
    Logger = Claset.Base.Logs.Logs(LogHeader=LogHeader)
    Logger.genLog(Perfixs=LogHeader, Text="Started!!!")
    Logger.genLog(Perfixs=LogHeader, Text=["Running In \"", " ".join(uname()), "\""])
    Downloader = Claset.Base.Download.DownloadManager(Logger=Logger)
    DL_AssetsIndex = Claset.Game.LoadJson.getDL_AssetsIndex(Claset.Base.File.loadFile(ThisFilePath + "/DataSource/1.17.json", "json"))
    try:
        ProjectID = Downloader.addTasks(DL_AssetsIndex)
        Downloader.projectJoin(ProjectID)
    except KeyboardInterrupt:
        Downloader.stop()
    Logger.genLog(Perfixs=LogHeader, Text="Stopped!!!")
    Logger.genLog(Perfixs=LogHeader, Text=["Used time: ", time() - StartTime])


if __name__ == "__main__":
    Main()
