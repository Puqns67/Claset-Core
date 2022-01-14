# -*- coding: utf-8 -*-
"""测试"""

from time import time
from platform import uname

import Claset


def testInstallAndRun():
    Downloader = Claset.Utils.DownloadManager()

    try:
        Claset.Game.Install.GameInstaller(Downloader=Downloader, VersionName="Test", MinecraftVersion="1.18.1")
    except KeyboardInterrupt:
        Downloader.stop()
        exit()

    GameLauncher = Claset.Game.Launch.GameLauncher(VersionName="Test")
    GameLauncher.launchGame()
    try:
        GameLauncher.waitGame()
    except KeyboardInterrupt:
        GameLauncher.stopGame()
        exit()


def testMicrosoftOAuth():
    Logger = Claset.getLogger()
    OAuth = Claset.Accounts.Auth.MicrosoftOAuth()
    OAuth.auth()
    Logger.info("Microsoft Account Keys: \"%s\", \"%s\"", OAuth.AccessToken, OAuth.RefreshToken)


def Main():
    StartTime = time()
    Logger = Claset.getLogger()
    Logger.info("Started!!!")
    Logger.info("Running In \"%s\"", " ".join(uname()))

    testInstallAndRun()

    Logger.info("Stopped!!!")
    Logger.info("Used time: %s", str(time() - StartTime))

