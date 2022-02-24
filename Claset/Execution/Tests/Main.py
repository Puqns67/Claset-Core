# -*- coding: utf-8 -*-
"""测试"""

from time import time
from platform import uname
from sys import exit

import Claset


def testInstallAndRun():
    GameInstaller = Claset.Game.Install.Installer(VersionName="Test")
    try:
        GameInstaller.InstallVanilla()
    except KeyboardInterrupt:
        Claset.stopALLDownloader()
        exit()

    GameLauncher = Claset.Game.Launch.GameLauncher(VersionName="Test")
    GameLauncher.launchGame()
    try:
        GameLauncher.waitGame()
    except KeyboardInterrupt:
        Claset.stopALLDownloader()
        GameLauncher.stopGame()
        exit()


def testMicrosoftOAuth():
    Logger = Claset.getLogger()
    OAuth = Claset.Accounts.Auth()
    OAuth.auth()
    Logger.info("Microsoft Account Keys: \"%s\", \"%s\"", OAuth.MicrosoftAccountAccessToken, OAuth.MicrosoftAccountRefreshToken)
    OAuth.getMinecraftAccountInfos()
    Logger.info("Account Infos: \n%s", OAuth.MinecraftAccessToken)


def Main():
    StartTime = time()
    Logger = Claset.getLogger()
    Logger.info("Started!!!")
    Logger.info("Running In \"%s\"", " ".join(uname()))

    testInstallAndRun()

    Logger.info("Stopped!!!")
    Logger.info("Used time: %s", str(time() - StartTime))

