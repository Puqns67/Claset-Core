# -*- coding: utf-8 -*-
"""游戏启动器"""

from logging import getLogger
from re import compile as reCompile
from typing import Any
from subprocess import run

from Claset import __version__, __productname__
from Claset.Utils import Configs, JavaHelper, pathAdder, loadFile, dfCheck, path, getValueFromDict

from ..Utils import ResolveRule, getClassPath, processNatives

from .Exceptions import *

Logger = getLogger(__name__)


class GameLauncher():
    """游戏启动器"""
    MatchRunCodeKey = reCompile(r"^(.*)\$\{(.+)\}(.*)$")
    Features: dict[str, bool] = {"is_demo_user": False, "has_custom_resolution": True}
    ClasetJvmHeader: list[str] = ["-XX:+UnlockExperimentalVMOptions", "-XX:+UseG1GC", "-XX:G1NewSizePercent=20", "-XX:G1ReservePercent=20", "-XX:MaxGCPauseMillis=50", "-XX:G1HeapRegionSize=16m", "-XX:-UseAdaptiveSizePolicy", "-XX:-OmitStackTraceInFastThrow", "-XX:-DontCompileHugeMethods"]

    def __init__(self, VersionName: str):
        self.VersionName = VersionName
        self.VersionDir = pathAdder("$VERSION", VersionName)
        self.VersionJarPath = pathAdder(self.VersionDir, self.VersionName + ".jar")

        # 检查版本是否存在
        if ((VersionName == str()) or (dfCheck(self.VersionDir, Type="d") == False)):
            raise VersionNotFound(VersionName)

        # 配置文件相关处理
        self.VersionConfigFilePath = pathAdder(self.VersionDir, "ClasetVersionConfig.json")
        self.VersionConfig = Configs(ID="Game", FilePath=self.VersionConfigFilePath)
        self.GlobalConfig = Configs(ID="Settings")

        # 版本 Json
        self.VersionJsonPath = pathAdder(self.VersionDir, VersionName + ".json")
        self.VersionJson = loadFile(Path=self.VersionJsonPath, Type="json")

        if self.VersionJson["minimumLauncherVersion"] > 21:
            raise LauncherVersionError(self.VersionJson["minimumLauncherVersion"])

        # Natives
        self.NativesPath = pathAdder(self.VersionDir, self.getConfig(["NativesDir"]))
        print(self.NativesPath)

        self.JavaPath, self.JavaInfo = self.setJava()
        self.RunCode = self.getRunCode()


    def launchGame(self) -> None:
        """启动游戏"""
        Logger.debug("Run code: %s", self.RunCode)
        processNatives(VersionJson=self.VersionJson, ExtractTo=self.NativesPath, Features=self.Features)
        run(args=[self.JavaPath] + self.RunCode)


    def getRunCode(self) -> dict:
        return(self.processRunArgsList(self.getRunArgsList()))


    def getRunArgsList(self, Type: str | None = None) -> list[str]:
        match self.VersionJson["complianceLevel"]:
            case 0:
                return(
                    ["${CLASETJVMHEADER}", "${JVMPREFIX}", "${MEMMIN}", "${MEMMAX}", "${JVMEND}", "${MAINCLASS}", "${GAMEARGSPREFIX}"] + self.VersionJson["minecraftArguments"].split() + ["${GAMEARGSEND}"]
                )
            case 1:
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

                Output = ["${CLASETJVMHEADER}", "${JVMPREFIX}", "${MEMMIN}", "${MEMMAX}"]
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
            case _:
                raise UnsupportComplianceLevel(self.VersionConfig["complianceLevel"])


    def processRunArgsList(self, RunCodeList: list[str] = list()) -> list[str]:
        Output = list()
        for RunCode in RunCodeList:
            Matched = self.MatchRunCodeKey.match(RunCode)
            if Matched == None:
                Output.append(RunCode)
                continue
            MatchedGroups = list(Matched.groups())
            Replaced = self._replaces(MatchedGroups[1])
            if type(Replaced) == type(None):
                continue
            elif type(Replaced) == type(str()):
                MatchedGroups[1] = Replaced
                Output.append(str().join(MatchedGroups))
            elif type(Replaced) in (type(tuple()), type(list()),):
                if len(Replaced) != 0:
                    for i in Replaced: Output.append(i)
            elif type(Replaced) in (type(int()), type(float()),):
                Output.append(str(Replaced))
        return(Output)


    def _replaces(self, Key: str) -> str | tuple | list | None:
        """替换"""
        match Key:
            case "CLASETJVMHEADER": return(self.ClasetJvmHeader)
            case "JVMPREFIX": return(self.VersionConfig["UnableGlobal"]["PrefixAndEnds"]["JvmPrefix"])
            case "JVMEND": return(self.VersionConfig["UnableGlobal"]["PrefixAndEnds"]["JvmEnd"])
            case "GAMEARGSPREFIX": return(self.VersionConfig["UnableGlobal"]["PrefixAndEnds"]["GamePrefix"])
            case "GAMEARGSEND": return(self.VersionConfig["UnableGlobal"]["PrefixAndEnds"]["GameEnd"])
            case "MEMMIN": return("-Xms" + str(self.getConfig(["MemoryMin"])) + "M")
            case "MEMMAX": return("-Xmx" + str(self.getConfig(["MemoryMax"])) + "M")
            case "MAINCLASS": return(self.VersionJson["mainClass"])
            case "launcher_name": return(__productname__)
            case "launcher_version": return(__version__)
            case "assets_root": return(path("$ASSETS", IsPath=True))
            case "assets_index_name": return(self.VersionJson["assets"])
            case "auth_player_name": return("WIP")
            case "auth_access_token": return("WIP")
            case "auth_uuid": return("WIP")
            case "user_type": return("WIP")
            case "auth_xuid": return("WIP")
            case "version_name": return(self.VersionName)
            case "version_type": return(self._replaces("launcher_name") + " " + self._replaces("launcher_version"))
            case "classpath": return(getClassPath(VersionJson=self.VersionJson, VersionJarPath=self.VersionJarPath, Features=self.Features))
            case "natives_directory": return(self.NativesPath)
            case "game_directory": return(self.VersionDir)
            case "clientid": return("WIP")
            case "resolution_width": return(self.getConfig(["WindowWidth"]))
            case "resolution_height": return(self.getConfig(["WindowHeight"]))
            case _: raise ValueError(Key)


    def getConfig(self, Keys: list[str] | str) -> Any:
        if type(Keys) == type(str()): Keys = [Keys]
        if Keys[0] in self.VersionConfig["Global"].keys():
            if self.VersionConfig.get(["UseGlobalConfig"]):
                return(getValueFromDict(Keys=Keys, Dict=self.GlobalConfig["GlobalConfig"]))
            else:
                Return = getValueFromDict(Keys=Keys, Dict=self.VersionConfig["Global"])
                if Return != None: return(Return)
                return(getValueFromDict(Keys=Keys, Dict=self.GlobalConfig["GlobalConfig"]))
        else: return(getValueFromDict(Keys=Keys, Dict=self.VersionConfig["UnableGlobal"]))


    def setJava(self) -> tuple[str]:
        JavaPath = self.getConfig(["JavaPath"])
        JavaInfo = JavaHelper.getJavaInfoList(PathList=[JavaPath])[0]
        recommendJavaVersion = self.VersionJson["javaVersion"]["majorVersion"]
        if recommendJavaVersion > JavaInfo["Version"][0]:
            Logger.warning("Java version (%s) too old, recommend Java Version is \"%s\"", JavaInfo["Version"], recommendJavaVersion)
        elif recommendJavaVersion < JavaInfo["Version"][0]:
            Logger.warning("Java version (%s) too new, recommend Java Version is \"%s\"", JavaInfo["Version"], recommendJavaVersion)
        return((JavaPath,JavaInfo,))

