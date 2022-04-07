# -*- coding: utf-8 -*-
"""游戏启动器"""

from logging import getLogger
from types import NoneType
from typing import Any
from uuid import uuid4
from subprocess import Popen, DEVNULL

from Claset import __fullversion__, __productname__, LaunchedGames
from Claset.Accounts import AccountManager, Account
from Claset.Game.Utils import VersionInfos, ResolveRule, getClassPath, extractNatives, getLog4j2Infos
from Claset.Utils import Configs, path, getValueFromDict, OriginalSystem
from Claset.Utils.Others import ReMatchFormatDollar
from Claset.Utils.JavaHelper import autoPickJava, getJavaInfo, JavaInfo

from .Exceptions import *

if OriginalSystem == "Windows":
    from subprocess import (
        REALTIME_PRIORITY_CLASS, HIGH_PRIORITY_CLASS, ABOVE_NORMAL_PRIORITY_CLASS,
        NORMAL_PRIORITY_CLASS, BELOW_NORMAL_PRIORITY_CLASS, IDLE_PRIORITY_CLASS
    )
    SubProcessPriorityClasses = {"REALTIME": REALTIME_PRIORITY_CLASS, "HIGH": HIGH_PRIORITY_CLASS, "ABOVE_NORMAL": ABOVE_NORMAL_PRIORITY_CLASS, "NORMAL": NORMAL_PRIORITY_CLASS, "BELOW_NORMAL": BELOW_NORMAL_PRIORITY_CLASS, "IDLE": IDLE_PRIORITY_CLASS}

__all__ = ("Features", "ClasetJvmHeader", "GameStatus", "GameLauncher",)
Logger = getLogger(__name__)
Features: dict[str, bool] = {"is_demo_user": False, "has_custom_resolution": True}
ClasetJvmHeader: list[str] = ["-XX:+UnlockExperimentalVMOptions", "-XX:+UseG1GC", "-XX:G1NewSizePercent=20", "-XX:G1ReservePercent=20", "-XX:MaxGCPauseMillis=50", "-XX:G1HeapRegionSize=16m", "-XX:-UseAdaptiveSizePolicy", "-XX:-OmitStackTraceInFastThrow", "-XX:-DontCompileHugeMethods"]
GameStatus: tuple[str] = ("UNRUNNING", "STOPPED", "STARTING", "RUNNING")


class GameLauncher():
    """游戏启动器"""
    def __init__(self, VersionName: str, Account: Account | None = None):
        # 获取版本相关信息
        self.VersionInfos = VersionInfos(VersionName=VersionName)
        if not self.VersionInfos.check():
            raise VersionNotFound(VersionName)
        self.VersionInfos.full()

        # 获取账户相关信息
        if Account is None:
            self.AccountObject = AccountManager().getAccountObject()
        else:
            self.AccountObject = Account

        self.GlobalConfig = Configs(ID="Settings")

        if self.VersionInfos.MinimumLauncherVersion > 21:
            raise LauncherVersionError(self.VersionInfos.MinimumLauncherVersion)

        self.Status: str = "UNRUNNING"


    def launchGame(self, PrintToTerminal: bool = True) -> None:
        """启动游戏"""
        self.checkStatus(("STOPPED", "UNRUNNING",), Raise=True)
        self.setStatus("STARTING")
        if not self.getConfig("NotCheckGame"):
            self.VersionInfos.checkFull()

        self.PickedJava = self.getJavaPathAndInfo(NotCheck=self.getConfig("NotCheckJvm"))

        # 解析 Natives
        extractNatives(VersionJson=self.VersionInfos.Json, ExtractTo=self.VersionInfos.NativesPath, Features=Features)

        # 获取启动命令行参数
        self.RunArgs = self.getRunArgs()
        # 获取工作目录
        if self.getConfig("VersionIndependent"): self.RunCwd = self.VersionInfos.Dir
        else: self.RunCwd = path("$MINECRFT", IsPath=True)
        if PrintToTerminal: Stdout = None
        else: Stdout = DEVNULL
        if OriginalSystem == "Windows": WindowsCreationFlags = SubProcessPriorityClasses[self.getConfig("WindowsPriority")]
        else: WindowsCreationFlags = 0

        Logger.info("Launch Game: %s", self.VersionInfos.Name)
        Logger.debug("Run code: %s", self.RunArgs)

        self.Game = Popen(args=[self.PickedJava["Path"]] + self.RunArgs, cwd=self.RunCwd, stdout=Stdout, creationflags=WindowsCreationFlags)

        LaunchedGames.append(self)
        self.setStatus("RUNNING")


    def waitGame(self) -> None:
        """等待游戏结束(阻塞线程至游戏结束)"""
        if self.checkStatus("RUNNING"):
            self.Game.wait()


    def stopGame(self) -> None:
        """向游戏进程发送 "停止" 命令"""
        if self.checkStatus("RUNNING"):
            self.Game.terminate()
            self.setStatus("STOPPED")


    def killGame(self) -> None:
        """向游戏进程发送 "杀死" 命令"""
        if self.checkStatus("RUNNING"):
            self.Game.kill()
            self.setStatus("STOPPED")


    def getRunArgs(self) -> list[str]:
        """获取启动命令行参数"""
        return(self.processRunArgsList(self.getRunArgsList()))


    def getRunArgsList(self) -> list[str]:
        """获取启动命令行参数"""
        match self.VersionInfos.ComplianceLevel:
            case 0:
                return(
                    [
                        "${CLASETJVMHEADER}", "${JVMPREFIX}", "${MEMMIN}",
                        "${MEMMAX}", "${LOG4J2CONFIG}", "${JVMSUFFIX}",
                        "-Djava.library.path=${natives_directory}",
                        "-Dminecraft.launcher.brand=${launcher_name}",
                        "-Dminecraft.launcher.version=${launcher_version}",
                        "-cp", "${classpath}",
                        "${MAINCLASS}", "${GAMEARGSPREFIX}"
                    ] + self.VersionInfos.Json["minecraftArguments"].split() + ["${GAMEARGSSUFFIX}"]
                )
            case 1:
                Arguments = ["${CLASETJVMHEADER}", "${JVMPREFIX}", "${MEMMIN}", "${MEMMAX}"]
                Arguments.extend(self.VersionInfos.Json["arguments"]["jvm"])
                Arguments.extend(("${LOG4J2CONFIG}", "${JVMSUFFIX}", "${MAINCLASS}", "${GAMEARGSPREFIX}",))
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
                Output.append("${GAMEARGSSUFFIX}")

                return(Output)
            case _:
                raise UnsupportComplianceLevel(self.VersionInfos.ComplianceLevel)


    def processRunArgsList(self, RunCodeList: list[str] = list()) -> list[str]:
        """处理获取到的启动命令行参数"""
        Output = list()
        for RunCode in RunCodeList:
            Matched = ReMatchFormatDollar.match(RunCode)
            if Matched is None:
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
            case "JVMPREFIX": return(self.VersionInfos.Configs["UnableGlobal"]["PrefixAndSuffix"]["JvmPrefix"])
            case "JVMSUFFIX": return(self.VersionInfos.Configs["UnableGlobal"]["PrefixAndSuffix"]["JvmSuffix"])
            case "GAMEARGSPREFIX": return(self.VersionInfos.Configs["UnableGlobal"]["PrefixAndSuffix"]["GamePrefix"])
            case "GAMEARGSSUFFIX": return(self.VersionInfos.Configs["UnableGlobal"]["PrefixAndSuffix"]["GameSuffix"])
            case "MEMMIN": return("-Xms" + str(self.getConfig("MemoryMin")) + "M")
            case "MEMMAX": return("-Xmx" + str(self.getConfig("MemoryMax")) + "M")
            case "LOG4J2CONFIG": return(getLog4j2Infos(InitFile=self.VersionInfos.Json, Type="Argument"))
            case "MAINCLASS": return(self.VersionInfos.MainClass)
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
            case "game_directory": return({True: self.VersionInfos.Dir, False: path("$MINECRFT", IsPath=True)}[self.getConfig("VersionIndependent")])
            case "clientid": return(uuid4().hex)
            case "resolution_width": return(self.getConfig("WindowWidth"))
            case "resolution_height": return(self.getConfig("WindowHeight"))
            case "library_directory": return(path("$LIBRERIES", IsPath=True))
            case _: raise ValueError(Key)


    def getConfig(self, Keys: str) -> Any:
        if Keys in self.VersionInfos.Configs["Global"]:
            if self.VersionInfos.Configs["UseGlobalConfig"]:
                return(getValueFromDict(Keys=Keys, Dict=self.GlobalConfig["GlobalConfig"]))
            else:
                Return = getValueFromDict(Keys=Keys, Dict=self.VersionInfos.Configs["Global"])
                if Return is not None: return(Return)
                return(getValueFromDict(Keys=Keys, Dict=self.GlobalConfig["GlobalConfig"]))
        else: return(getValueFromDict(Keys=Keys, Dict=self.VersionInfos.Configs["UnableGlobal"]))


    def getJavaPathAndInfo(self, NotCheck: bool = False) -> JavaInfo:
        JavaPath = self.getConfig("JavaPath")
        recommendJavaVersion: int = self.VersionInfos.Json["javaVersion"]["majorVersion"]
        if JavaPath == "AUTOPICK":
            return(autoPickJava(recommendVersion=recommendJavaVersion))
        else:
            if not NotCheck:
                JavaInfo = getJavaInfo(Path=JavaPath)
                if recommendJavaVersion > JavaInfo["Version"][0]:
                    Logger.warning("Java version %s too old, recommend Java Version is [%s, 0, 0]", JavaInfo["Version"], recommendJavaVersion)
                elif recommendJavaVersion < JavaInfo["Version"][0]:
                    Logger.warning("Java version %s too new, recommend Java Version is [%s, 0, 0]", JavaInfo["Version"], recommendJavaVersion)
                return(JavaInfo)
            else:
                return({"Path": JavaPath})


    def setStatus(self, Status: str | int) -> None:
        """设置游戏状态"""
        if Status in GameStatus:
            self.Status = Status
        else:
            raise UndefinedGameStatus(Status)


    def checkStatus(self, Status: tuple[str] | str, Reverse: bool = False, Raise: Any | None = None) -> bool:
        """检查游戏状态"""
        if isinstance(Status, str): Status = (Status,)

        # 检查状态是否存在
        for OneStatus in Status:
            if OneStatus not in GameStatus:
                raise UndefinedGameStatus(OneStatus)

        if self.getStatus(Update=False) in Status:
            if not Reverse: return(True)
        else:
            if Reverse: return(True)

        if Raise not in (None, False,):
            if issubclass(Raise, Exception):
                raise Raise
            else:
                if isinstance(Raise, bool): Raise = None
                raise GameStatusError(Raise)
        else:
            return(False)


    def updateStatus(self) -> None:
        """更新游戏状态"""
        if self.checkStatus("RUNNING"):
            if self.Game.poll() is not None:
                self.setStatus("STOPPED")


    def getStatus(self, Update: bool = True) -> str:
        """获取当前游戏状态"""
        if Update:
            self.updateStatus()
        return(self.Status)

