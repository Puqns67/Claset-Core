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

    try:
        Claset.Game.Install.GameInstaller(Name="Test", Version="1.18")
    except KeyboardInterrupt:
        Claset._Downloader.stop()

    Logger.info("Stopped!!!")
    Logger.info("Used time: %s", str(time() - StartTime))


if __name__ == "__main__":
    Main()
