# -*- coding: utf-8 -*-
"""测试"""

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

    StartTime = time()
    Claset.Logger.info("Started!!!")
    Claset.Logger.info("Running In \"%s\"", " ".join(uname()))
    Downloader = Claset.Base.Download.DownloadManager()
    DL_AssetsIndex = Claset.Game.LoadJson.AssetsIndex_DownloadList(Claset.Base.File.loadFile(ThisFilePath + "/DataSource/1.17.json", "json"))
    DL_Version = Claset.Game.LoadJson.Version_DownloadList(InitFile=Claset.Base.File.loadFile(ThisFilePath + "/DataSource/1.12.2.json", "json"), Name="Test")
    try:
        ProjectID = Downloader.addTasks(DL_AssetsIndex)
        ProjectID = Downloader.addTasks(DL_Version)
        Downloader.projectJoin(ProjectID)
    except KeyboardInterrupt:
        Downloader.stop()
    Claset.Logger.info("Stopped!!!")
    Claset.Logger.info("Used time: %s", str(time() - StartTime))


if __name__ == "__main__":
    Main()
