# -*- coding: utf-8 -*-
"""游戏启动器"""

from logging import getLogger

from Claset.Utils.Path import path as Pathmd, pathAdder
from Claset.Utils.File import loadFile, dfCheck
from Claset.Utils.Configs import Configs

from .Exceptions import Launcher as Ex_Launcher

Logger = getLogger(__name__)


class GameLauncher():
    """游戏启动器"""
    def __init__(self, VersionName: str, **OthersSettings: dict[str, str]):
        self.VersionName = VersionName
        self.OthersSettings = OthersSettings
        self.VersionDir = pathAdder("$VERSION", VersionName)

        # 检查版本是否存在
        if ((VersionName == str()) or (dfCheck(self.VersionDir, Type="d") == False)):
            raise Ex_Launcher.VersionNotFound

        self.VersionConfigFilePath = pathAdder(self.VersionDir, "ClasetVersionConfig.json")
        self.VersionConfig = Configs().getConfig(ID="Game", TargetVersion=0, FilePath=self.VersionConfigFilePath)

        if self.VersionConfig["UseGlobalConfig"] == True:
            self.GlobalConfig = Configs().getConfig(ID="Settings", TargetVersion=0)
        else: self.GlobalConfig = None


    def launchGame():
        pass


    def getLaunchCommand(self):
        pass


    def _replaces(self, Key: str) -> str:
        """替换"""
        """
        [
            '-XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump',
            '-Dos.name=Windows 10',
            '-Dos.version=10.0',
            '-Djava.library.path=${natives_directory}',
            '-Dminecraft.launcher.brand=${launcher_name}',
            '-Dminecraft.launcher.version=${launcher_version}',
            '-cp', '${classpath}',
            '--username', '${auth_player_name}',
            '--version', '${version_name}',
            '--gameDir', '${game_directory}',
            '--assetsDir', '${assets_root}',
            '--assetIndex', '${assets_index_name}',
            '--uuid', '${auth_uuid}',
            '--accessToken', '${auth_access_token}',
            '--userType', '${user_type}',
            '--versionType', '${version_type}'
        ]
        """
        match Key:
            case "launcher_name": return("Claset")
            case "launcher_version": return("21")
            case "assetsDir": return("$ASSETS")
            case "assets_index_name": return("")
            case "auth_player_name": return("WIP")
            case "user_type": return("WIP")
            case "version_type": return("WIP")
            case "classpath": return("WIP")
            case "natives_directory": return("WIP")
            case "game_directory": return("WIP")

