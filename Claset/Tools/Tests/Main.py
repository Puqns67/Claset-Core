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

    Claset.Game.Install.GameInstaller(Name="Test", Version="1.17.1")

    Claset.Logger.info("Stopped!!!")
    Claset.Logger.info("Used time: %s", str(time() - StartTime))


if __name__ == "__main__":
    Main()
