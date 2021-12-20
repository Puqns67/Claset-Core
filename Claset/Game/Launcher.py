# -*- coding: utf-8 -*-
"""游戏启动器"""

from logging import getLogger
from re import compile as reCompile

from Claset import __version__
from Claset.Utils.Path import pathAdder
from Claset.Utils.File import loadFile, dfCheck
from Claset.Utils.Configs import Configs

from .LoadJson import ResolveRule
from .Exceptions import Launcher as Ex_Launcher

Logger = getLogger(__name__)


class GameLauncher():
    """游戏启动器"""
    MatchRunCodeKey = reCompile(r"^(.*)\$\{(.+)\}(.*)$")
    Features: dict[str, bool] = {"is_demo_user": False, "has_custom_resolution": True}
    JvmHeader: tuple[str] = ()
    def __init__(self, VersionName: str, **OthersSettings: dict[str, str]):
        self.VersionName = VersionName
        self.OthersSettings = OthersSettings
        self.VersionDir = pathAdder("$VERSION", VersionName)

        # 检查版本是否存在
        if ((VersionName == str()) or (dfCheck(self.VersionDir, Type="d") == False)):
            raise Ex_Launcher.VersionNotFound

        # 配置文件相关处理
        self.VersionConfigFilePath = pathAdder(self.VersionDir, "ClasetVersionConfig.json")
        self.VersionConfig = Configs().getConfig(ID="Game", TargetVersion=0, FilePath=self.VersionConfigFilePath)

        if self.VersionConfig["UseGlobalConfig"] == True:
            self.GlobalConfig = Configs().getConfig(ID="Settings", TargetVersion=0)
        else: self.GlobalConfig = None

        # 版本 Json
        self.VersionJsonPath = pathAdder(self.VersionDir, VersionName + ".json")
        self.VersionJson = loadFile(Path=self.VersionJsonPath, Type="json")

        # Natives
        self.NativesPath = pathAdder(self.VersionDir, "natives")


    def launchGame():
        pass


    def getLaunchCommand(self):
        pass


    def getRunCodeList(self, Type: str | None = None) -> list[str]:
        Arguments = list()
        match Type:
            case "JVM":
                Arguments.extend(self.VersionJson["arguments"]["jvm"])
            case "Game":
                Arguments.extend(self.VersionJson["arguments"]["game"])
            case None:
                Arguments.extend(self.VersionJson["arguments"]["jvm"])
                Arguments.extend(("${JVMEND}", "${MAINCLASS}", "${GAMEARGSPREFIX}",))
                Arguments.extend(self.VersionJson["arguments"]["game"])
            case _: ValueError(Type)

        Output = ["${JVMPREFIX}"]
        for Argument in Arguments:
            if (type(Argument) == type(dict())):
                if (ResolveRule(Items=Argument["rules"], Features=self.Features)):
                    if (type(Argument["value"]) == type(str())):
                        Output.append(Argument["value"])
                    elif (type(Argument["value"]) == type(list())):
                        Output.extend(Argument["value"])
                    else:
                        raise(ValueError("Argument[\"value\"] type error"))
            elif (type(Argument) == type(str())):
                Output.append(Argument)
            else:
                raise(ValueError("Argument type error"))
        Output.append("${GAMEARGSEND}")
        return(Output)


    def processRunCode(self, RunCodeList: list[str] = list()) -> list[str]:
        Output = list()
        for RunCode in RunCodeList:
            Matched = self.MatchRunCodeKey.match(RunCode)
            while Matched != None:
                MatchedGroups = list(Matched.groups())
                MatchedGroups[1] = self._replaces(MatchedGroups[1])
                RunCode = str().join(MatchedGroups)
                Matched = self.MatchRunCodeKey.match(RunCode)
            Output.append(RunCode)
        return(Output)


    def _replaces(self, Key: str) -> str:
        """替换"""
        match Key:
            case "JVMPREFIX": return(Key)
            case "JVMEND": return(Key)
            case "GAMEARGSPREFIX": return(Key)
            case "GAMEARGSEND": return(Key)
            case "MAINCLASS": return(self.VersionJson["mainClass"])
            case "launcher_name": return("Claset")
            case "launcher_version": return(__version__)
            case "assetsDir": return("$ASSETS")
            case "assets_index_name": return("WIP")
            case "assets_root": return("WIP")
            case "auth_player_name": return("WIP")
            case "auth_access_token": return("WIP")
            case "auth_uuid": return("WIP")
            case "user_type": return("WIP")
            case "auth_xuid": return("WIP")
            case "version_name": return(self.VersionName)
            case "version_type": return(self._replaces("launcher_name") + " " + self._replaces("launcher_version"))
            case "classpath": return("WIP")
            case "natives_directory": return(self.NativesPath)
            case "game_directory": return("WIP")
            case "clientid": return("WIP")
            case "resolution_width": return("WIP")
            case "resolution_height": return("WIP")
            case _: raise ValueError(Key)

