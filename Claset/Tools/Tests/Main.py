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
    Claset.Logger.info("Started!!!")
    Claset.Logger.info("Running In \"%s\"", " ".join(uname()))

    try:
        Claset.Game.Install.GameInstaller(Name="Test", Version="1.17.1")
    except KeyboardInterrupt:
        Claset.Downloader.stop()

    Claset.Logger.info("Stopped!!!")
    Claset.Logger.info("Used time: %s", str(time() - StartTime))


if __name__ == "__main__":
    Main()
