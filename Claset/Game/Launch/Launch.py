# -*- coding: utf-8 -*-
"""游戏启动器"""

from logging import getLogger
from re import compile as reCompile
from types import NoneType
from typing import Any
from uuid import uuid4
from platform import system
from subprocess import (
    Popen, REALTIME_PRIORITY_CLASS, HIGH_PRIORITY_CLASS, ABOVE_NORMAL_PRIORITY_CLASS,
    NORMAL_PRIORITY_CLASS, BELOW_NORMAL_PRIORITY_CLASS, IDLE_PRIORITY_CLASS, DEVNULL
)

from Claset import __fullversion__, __productname__, LaunchedGames
from Claset.Accounts import AccountManager, Account
from Claset.Game.Utils import VersionInfos, ResolveRule, getClassPath, processNatives, getLog4j2Infos
from Claset.Utils import Configs, path, getValueFromDict
from Claset.Utils.JavaHelper import autoPickJava, fixJavaPath, getJavaInfoList, JavaInfo

from .Exceptions import *

Logger = getLogger(__name__)
ReMatchRunCodeKey = reCompile(r"^(.*)\$\{(.+)\}(.*)$")
Features: dict[str, bool] = {"is_demo_user": False, "has_custom_resolution": True}
SubProcessPriorityClasses = {"REALTIME": REALTIME_PRIORITY_CLASS, "HIGH": HIGH_PRIORITY_CLASS, "ABOVE_NORMAL": ABOVE_NORMAL_PRIORITY_CLASS, "NORMAL": NORMAL_PRIORITY_CLASS, "BELOW_NORMAL": BELOW_NORMAL_PRIORITY_CLASS, "IDLE": IDLE_PRIORITY_CLASS}
ClasetJvmHeader: list[str] = ["-XX:+UnlockExperimentalVMOptions", "-XX:+UseG1GC", "-XX:G1NewSizePercent=20", "-XX:G1ReservePercent=20", "-XX:MaxGCPauseMillis=50", "-XX:G1HeapRegionSize=16m", "-XX:-UseAdaptiveSizePolicy", "-XX:-OmitStackTraceInFastThrow", "-XX:-DontCompileHugeMethods"]


class GameLauncher():
    """游戏启动器"""
    def __init__(self, VersionName: str, Account: Account | None = None):
        # 获取版本相关信息
        self.VersionInfos = VersionInfos(VersionName=VersionName)
        if not self.VersionInfos.check():
            raise VersionNotFound(VersionName)
        self.VersionInfos.full()

        # 获取账户相关信息
        if Account == None:
            self.AccountObject = AccountManager().getAccountObject()
        else:
            self.AccountObject = Account

        self.GlobalConfig = Configs(ID="Settings")

        if self.VersionInfos.Json["minimumLauncherVersion"] > 21:
            raise LauncherVersionError(self.VersionInfos.Json["minimumLauncherVersion"])


    def launchGame(self, PrintToTerminal: bool = True) -> None:
        """启动游戏"""
        RunArgs = self.getRunArgs()
        self.PickedJava = self.getJavaPathAndInfo()

        processNatives(VersionJson=self.VersionInfos.Json, ExtractTo=self.VersionInfos.NativesPath, Features=Features)
        Logger.info("Launch Game: %s", self.VersionInfos.Name)
        Logger.debug("Run code: %s", RunArgs)
        match system():
            case "Windows":
                Priority = SubProcessPriorityClasses[self.getConfig("WindowsPriority")]
                if PrintToTerminal:
                    self.Game = Popen(args=[self.PickedJava["Path"]] + RunArgs, cwd=self.VersionInfos.Dir, creationflags=Priority)
                else:
                    self.Game = Popen(args=[self.PickedJava["Path"]] + RunArgs, cwd=self.VersionInfos.Dir, stdout=DEVNULL, creationflags=Priority)
            case "Darwin" | "Linux":
                if PrintToTerminal:
                    self.Game = Popen(args=[self.PickedJava["Path"]] + RunArgs, cwd=self.VersionInfos.Dir)
                else:
                    self.Game = Popen(args=[self.PickedJava["Path"]] + RunArgs, cwd=self.VersionInfos.Dir, stdout=DEVNULL)
        LaunchedGames.append(self)


    def waitGame(self) -> None:
        if self.Game:
            self.Game.wait()


    def stopGame(self) -> None:
        if self.Game:
            self.Game.terminate()


    def getRunArgs(self) -> list[str]:
        return(self.processRunArgsList(self.getRunArgsList()))


    def getRunArgsList(self) -> list[str]:
        match self.VersionInfos.ComplianceLevel:
            case 0:
                return(
                    [
                        "${CLASETJVMHEADER}", "${JVMPREFIX}", "${MEMMIN}",
                        "${MEMMAX}", "${LOG4J2CONFIG}", "${JVMEND}",
                        "-Djava.library.path=${natives_directory}",
                        "-Dminecraft.launcher.brand=${launcher_name}",
                        "-Dminecraft.launcher.version=${launcher_version}",
                        "-cp", "${classpath}",
                        "${MAINCLASS}", "${GAMEARGSPREFIX}"
                    ] + self.VersionInfos.Json["minecraftArguments"].split() + ["${GAMEARGSEND}"]
                )
            case 1:
                Arguments = ["${CLASETJVMHEADER}", "${JVMPREFIX}", "${MEMMIN}", "${MEMMAX}"]
                Arguments.extend(self.VersionInfos.Json["arguments"]["jvm"])
                Arguments.extend(("${LOG4J2CONFIG}", "${JVMEND}", "${MAINCLASS}", "${GAMEARGSPREFIX}",))
                Arguments.extend(self.VersionInfos.Json["arguments"]["game"])

                Output = list()
                for Argument in Arguments:
                    if isinstance(Argument, dict):
                        if (ResolveRule(Items=Argument["rules"], Features=Features)):
                            if isinstance(Argument["value"], str):
                                Output.append(Argument["value"])
                            elif isinstance(Argument["value"], list):
                                Output.extend(Argument["value"])
                            else:
                                raise(ValueError("Argument[\"value\"] type error"))
                    elif isinstance(Argument, str):
                        Output.append(Argument)
                    else:
                        raise(ValueError("Argument type error"))
                Output.append("${GAMEARGSEND}")

                return(Output)
            case _:
                raise UnsupportComplianceLevel(self.VersionInfos.ComplianceLevel)


    def processRunArgsList(self, RunCodeList: list[str] = list()) -> list[str]:
        Output = list()
        for RunCode in RunCodeList:
            Matched = ReMatchRunCodeKey.match(RunCode)
            if Matched == None:
                Output.append(RunCode)
                continue
            MatchedGroups = list(Matched.groups())
            Replaced = self._replaces(MatchedGroups[1])
            if isinstance(Replaced, NoneType):
                continue
            elif isinstance(Replaced, str):
                MatchedGroups[1] = Replaced
                Output.append(str().join(MatchedGroups))
            elif isinstance(Replaced, (tuple, list,)):
                if len(Replaced) != 0:
                    Output.extend(Replaced)
            elif isinstance(Replaced, (int, float)):
                Output.append(str(Replaced))
        return(Output)


    def _replaces(self, Key: str) -> str | tuple | list | None:
        """替换"""
        match Key:
            case "CLASETJVMHEADER": return(ClasetJvmHeader)
            case "JVMPREFIX": return(self.VersionInfos.Configs["UnableGlobal"]["PrefixAndEnds"]["JvmPrefix"])
            case "JVMEND": return(self.VersionInfos.Configs["UnableGlobal"]["PrefixAndEnds"]["JvmEnd"])
            case "GAMEARGSPREFIX": return(self.VersionInfos.Configs["UnableGlobal"]["PrefixAndEnds"]["GamePrefix"])
            case "GAMEARGSEND": return(self.VersionInfos.Configs["UnableGlobal"]["PrefixAndEnds"]["GameEnd"])
            case "MEMMIN": return("-Xms" + str(self.getConfig("MemoryMin")) + "M")
            case "MEMMAX": return("-Xmx" + str(self.getConfig("MemoryMax")) + "M")
            case "LOG4J2CONFIG": return(getLog4j2Infos(InitFile=self.VersionInfos.Json, Type="Argument"))
            case "MAINCLASS": return(self.VersionInfos.Json["mainClass"])
            case "launcher_name": return(__productname__)
            case "launcher_version": return(__fullversion__)
            case "assets_root": return(path("$ASSETS", IsPath=True))
            case "assets_index_name": return(self.VersionInfos.AssetsVersion)
            case "auth_xuid": return(uuid4().hex)
            case "auth_uuid": return(self.AccountObject.UUID.hex)
            case "auth_player_name": return(self.AccountObject.Name)
            case "auth_access_token": return(self.AccountObject.getAccessToken())
            case "user_type": return(self.AccountObject.getShortType())
            case "version_name": return(self.VersionInfos.Name)
            case "version_type": return(self._replaces("launcher_name") + " " + self._replaces("launcher_version"))
            case "classpath": return(getClassPath(VersionJson=self.VersionInfos.Json, VersionJarPath=self.VersionInfos.JarPath, Features=Features))
            case "natives_directory": return(self.VersionInfos.NativesPath)
            case "game_directory": return(self.VersionInfos.Dir)
            case "clientid": return(uuid4().hex)
            case "resolution_width": return(self.getConfig("WindowWidth"))
            case "resolution_height": return(self.getConfig("WindowHeight"))
            case _: raise ValueError(Key)


    def getConfig(self, Keys: str) -> Any:
        if Keys in self.VersionInfos.Configs["Global"]:
            if self.VersionInfos.Configs["UseGlobalConfig"]:
                return(getValueFromDict(Keys=Keys, Dict=self.GlobalConfig["GlobalConfig"]))
            else:
                Return = getValueFromDict(Keys=Keys, Dict=self.VersionInfos.Configs["Global"])
                if Return != None: return(Return)
                return(getValueFromDict(Keys=Keys, Dict=self.GlobalConfig["GlobalConfig"]))
        else: return(getValueFromDict(Keys=Keys, Dict=self.VersionInfos.Configs["UnableGlobal"]))


    def getJavaPathAndInfo(self) -> JavaInfo:
        JavaPath = self.getConfig("JavaPath")
        recommendJavaVersion: int = self.VersionInfos.Json["javaVersion"]["majorVersion"]
        if JavaPath == "AUTOPICK":
            return(autoPickJava(recommendVersion=recommendJavaVersion))
        else:
            JavaPath = fixJavaPath(JavaPath)
            JavaInfo = getJavaInfoList(PathList=[JavaPath])[0]
            if recommendJavaVersion > JavaInfo["Version"][0]:
                Logger.warning("Java version %s too old, recommend Java Version is [%s, 0, 0]", JavaInfo["Version"], recommendJavaVersion)
            elif recommendJavaVersion < JavaInfo["Version"][0]:
                Logger.warning("Java version %s too new, recommend Java Version is [%s, 0, 0]", JavaInfo["Version"], recommendJavaVersion)
            return(JavaInfo)

