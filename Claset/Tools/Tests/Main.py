# -*- coding: utf-8 -*-
"""测试"""

from sys import path
from os import getcwd
from time import time
from platform import uname

path.append(getcwd())

import Claset

def Main():
    StartTime = time()
    Logger = Claset.getLogger()
    Logger.info("Started!!!")
    Logger.info("Running In \"%s\"", " ".join(uname()))
    Downloader = Claset.Utils.Download.DownloadManager()

    try:
        Claset.Game.Install.GameInstaller(Downloader=Downloader, Name="Test", Version="1.18")
    except KeyboardInterrupt:
        Downloader.stop()

    Logger.info("Stopped!!!")
    Logger.info("Used time: %s", str(time() - StartTime))


if __name__ == "__main__":
    Main()
