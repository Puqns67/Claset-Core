# -*- coding: utf-8 -*-
"""游戏实例"""

from logging import getLogger
from types import NoneType
from typing import Iterable, Any
from uuid import uuid4
from subprocess import Popen, DEVNULL
from time import strftime, localtime

from Claset import __fullversion__, __productname__, LaunchedInstance
from Claset.Accounts import AccountManager, Account
from Claset.Instance.Utils import (
    InstanceInfos,
    ResolveRule,
    getClassPath,
    extractNatives,
    getLog4j2Infos,
)
from Claset.Utils import (
    System,
    FileTypes,
    path,
    pathAdder,
    safetyPath,
    dfCheck,
    saveFile,
    autoPickJava,
    getJavaInfo,
    getDownloader,
    JavaInfo,
    ReMatchFormatDollar,
)

from .Instance import InstanceBase, InstanceStatus
from .Exceptions import *

if System().get() == "Windows":
    from subprocess import (
        REALTIME_PRIORITY_CLASS,
        HIGH_PRIORITY_CLASS,
        ABOVE_NORMAL_PRIORITY_CLASS,
        NORMAL_PRIORITY_CLASS,
        BELOW_NORMAL_PRIORITY_CLASS,
        IDLE_PRIORITY_CLASS,
    )

    SubProcessPriorityClasses = {
        "REALTIME": REALTIME_PRIORITY_CLASS,
        "HIGH": HIGH_PRIORITY_CLASS,
        "ABOVE_NORMAL": ABOVE_NORMAL_PRIORITY_CLASS,
        "NORMAL": NORMAL_PRIORITY_CLASS,
        "BELOW_NORMAL": BELOW_NORMAL_PRIORITY_CLASS,
        "IDLE": IDLE_PRIORITY_CLASS,
    }

__all__ = (
    "Features",
    "ClasetJvmHeader",
    "InstanceStatus",
    "GameLauncher",
)
Logger = getLogger(__name__)
Features: dict[str, bool] = {"is_demo_user": False, "has_custom_resolution": True}
ClasetJvmHeader: tuple[str] = (
    "-XX:+UnlockExperimentalVMOptions",
    "-XX:+UseG1GC",
    "-XX:G1NewSizePercent=20",
    "-XX:G1ReservePercent=20",
    "-XX:MaxGCPauseMillis=50",
    "-XX:G1HeapRegionSize=16m",
    "-XX:-UseAdaptiveSizePolicy",
    "-XX:-OmitStackTraceInFastThrow",
    "-XX:-DontCompileHugeMethods",
)


class GameLauncher(InstanceBase):
    """游戏启动器"""

    def __init__(self, VersionName: str, Account: Account | None = None):
        # 获取版本相关信息
        self.VersionInfos = InstanceInfos(VersionName=VersionName)
        if not self.VersionInfos.check():
            raise VersionNotFound(VersionName)
        self.VersionInfos.full()

        # 获取账户相关信息
        if Account is None:
            self.AccountObject = AccountManager().getAccountObject()
        else:
            self.AccountObject = Account

        if self.VersionInfos.MinimumLauncherVersion is not None:
            if self.VersionInfos.MinimumLauncherVersion > 21:
                raise LauncherVersionError(self.VersionInfos.MinimumLauncherVersion)
        else:
            Logger.warning(
                'Version ("%s")\'s "MinimumLauncherVersion" is Null, please check file:'
                ' "%s"',
                self.VersionInfos.Name,
                self.VersionInfos.VersionJsonPath,
            )

        self.Status = InstanceStatus.UnRunning

    def launchGame(
        self,
        Type: str = "SUBPROCESS",
        PrintToTerminal: bool = True,
        SaveTo: str | None = None,
    ) -> None:
        """
        启动游戏
        * Type: 启动模式, 默认为 "SUBPROCESS"

        启动模式：
        * SUBPROCESS: 使用 Python 子进程 (subprocess) 库启动游戏, 支持对游戏进行管理
            1. PrintToTerminal: 在终端中显示游戏日志输出, 默认为 True
        * SAVESCRIPT: 将对应版本的启动脚本保存为文件
            1. SaveTo: 保存至文件时的文件位置, 默认为 None, 为 None 时将以 {Name}-{DateAndTime}.[sh|bat] 格式的文件名保存至当前工作目录下
        """
        if Type != "SAVESCRIPT":
            self.checkStatus(
                (
                    InstanceStatus.Stopped,
                    InstanceStatus.UnRunning,
                ),
                Raise=True,
            )
            self.setStatus(InstanceStatus.Starting)
        if not self.VersionInfos.getConfig("NotCheckGame"):
            DownloadTasks = self.VersionInfos.checkFull()
            if len(DownloadTasks) >= 1:
                if not hasattr(self, "Downloader"):
                    self.Downloader = getDownloader()
                self.Downloader.waitProject(self.Downloader.addTask(DownloadTasks))

        if not hasattr(self, "PickedJava"):
            self.PickedJava = self.getJavaPathAndInfo(
                NotCheck=self.VersionInfos.getConfig("NotCheckJvm")
            )

        # 提取 Natives
        extractNatives(
            VersionJson=self.VersionInfos.VersionJson,
            ExtractTo=self.VersionInfos.NativesPath,
            Features=Features,
        )

        # 获取启动命令行参数
        self.RunArgs = self.getRunArgs()

        # 获取工作目录
        self.RunCwd = (
            self.VersionInfos.Dir
            if self.VersionInfos.getConfig("VersionIndependent")
            else path("$MINECRFT", IsPath=True)
        )

        Logger.info(
            'Using Java "%s" to launch game "%s"',
            self.PickedJava["Path"],
            self.VersionInfos.Name,
        )
        Logger.debug("Run code: %s", self.RunArgs)

        match Type:
            case "SUBPROCESS":
                Stdout = None if PrintToTerminal else DEVNULL
                WindowsCreationFlags = (
                    SubProcessPriorityClasses[self.VersionInfos.getConfig("WindowsPriority")]
                    if System().get() == "Windows"
                    else 0
                )
                self.Instance = Popen(
                    args=[self.PickedJava["Path"]] + self.RunArgs,
                    cwd=self.RunCwd,
                    stdout=Stdout,
                    creationflags=WindowsCreationFlags,
                )
                LaunchedInstance.append(self)
                self.setStatus(InstanceStatus.Running)
            case "SAVESCRIPT":
                SafetyRunCwd = safetyPath(self.RunCwd)
                SafetyJavaPath = safetyPath(self.PickedJava["Path"])
                SafetyRunCommand = str()
                if SaveTo is None:
                    NowTime = strftime("%Y-%m-%d-%H-%M-%S", localtime())
                    FormatName = System().get(Format={"Windows": "bat", "Other": "sh"})
                    SaveTo = pathAdder(
                        "$PREFIX", f"{self.VersionInfos.Name}-{NowTime}.{FormatName}"
                    )
                for i in self.RunArgs:
                    SafetyRunCommand += " " + safetyPath(i)
                saveFile(
                    Path=SaveTo,
                    Type=FileTypes.Text,
                    FileContent=(f"cd {SafetyRunCwd}\n{SafetyJavaPath}{SafetyRunCommand}"),
                )
                self.setStatus(InstanceStatus.UnRunning)
            case _:
                TypeError(Type)

    def getRunArgs(self) -> list[str]:
        """获取启动命令行参数"""
        return self.processRunArgsList(self.getRunArgsList())

    def getRunArgsList(self) -> list[str]:
        """获取启动命令行参数(不包含 Java 可执行项目)"""
        Output = list()
        if self.VersionInfos.VersionJson.get("arguments") is None:
            Output.extend(
                [
                    "${CLASETJVMHEADER}",
                    "${JVMPREFIX}",
                    "${MEMMIN}",
                    "${MEMMAX}",
                    "${LOG4J2CONFIG}",
                    "${JVMSUFFIX}",
                    "-Djava.library.path=${natives_directory}",
                    "-Dminecraft.launcher.brand=${launcher_name}",
                    "-Dminecraft.launcher.version=${launcher_version}",
                    "-cp",
                    "${classpath}",
                    "${MAINCLASS}",
                    "${GAMEARGSPREFIX}",
                ]
            )
            try:
                Output.extend(self.VersionInfos.VersionJson["minecraftArguments"].split())
            except KeyError:
                raise UnsupportVersion(self.VersionInfos.Name)
            Output.append("${GAMEARGSSUFFIX}")
        else:
            try:
                Arguments = [
                    "${CLASETJVMHEADER}",
                    "${JVMPREFIX}",
                    "${MEMMIN}",
                    "${MEMMAX}",
                    "${LOG4J2CONFIG}",
                ]
                Arguments.extend(self.VersionInfos.VersionJson["arguments"]["jvm"])
                Arguments.extend(
                    (
                        "${JVMSUFFIX}",
                        "${MAINCLASS}",
                        "${GAMEARGSPREFIX}",
                    )
                )
                Arguments.extend(self.VersionInfos.VersionJson["arguments"]["game"])
            except KeyError:
                raise UnsupportVersion(self.VersionInfos.Name)

            for Argument in Arguments:
                if isinstance(Argument, dict):
                    if ResolveRule(Items=Argument["rules"], Features=Features):
                        if isinstance(Argument["value"], str):
                            Output.append(Argument["value"])
                        elif isinstance(Argument["value"], list):
                            Output.extend(Argument["value"])
                        else:
                            raise (ValueError('Argument["value"] type error'))
                elif isinstance(Argument, str):
                    Output.append(Argument)
                else:
                    raise (ValueError("Argument type error"))
            Output.append("${GAMEARGSSUFFIX}")
        return Output

    def processRunArgsList(self, RunCodeList: Iterable[str] = tuple()) -> list[str]:
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
            elif isinstance(Replaced, Iterable):
                if len(Replaced) != 0:
                    Output.extend(Replaced)
            elif isinstance(Replaced, int | float):
                Output.append(str(Replaced))
        return Output

    def _replaces(self, Key: str) -> Any:
        """替换"""
        match Key:
            case "CLASETJVMHEADER":
                return ClasetJvmHeader
            case "JVMPREFIX":
                return self.VersionInfos.getConfig(
                    (
                        "PrefixAndSuffix",
                        "JvmPrefix",
                    )
                )
            case "JVMSUFFIX":
                return self.VersionInfos.getConfig(
                    (
                        "PrefixAndSuffix",
                        "JvmSuffix",
                    )
                )
            case "GAMEARGSPREFIX":
                return self.VersionInfos.getConfig(
                    (
                        "PrefixAndSuffix",
                        "ExecPrefix",
                    )
                )
            case "GAMEARGSSUFFIX":
                return self.VersionInfos.getConfig(
                    (
                        "PrefixAndSuffix",
                        "ExecSuffix",
                    )
                )
            case "MEMMIN":
                return f"-Xms{self.VersionInfos.getConfig('MemoryMin')}M"
            case "MEMMAX":
                return f"-Xmx{self.VersionInfos.getConfig('MemoryMax')}M"
            case "LOG4J2CONFIG":
                return getLog4j2Infos(InitFile=self.VersionInfos.VersionJson, Type="Argument")
            case "MAINCLASS":
                return self.VersionInfos.MainClass
            case "launcher_name":
                return __productname__
            case "launcher_version":
                return __fullversion__
            case "assets_root":
                return path("$ASSETS", IsPath=True)
            case "assets_index_name":
                return self.VersionInfos.AssetIndexVersion
            case "auth_xuid":
                return uuid4().hex
            case "auth_uuid":
                return self.AccountObject.UUID.hex
            case "auth_player_name":
                return self.AccountObject.Name
            case "auth_access_token":
                return self.AccountObject.getAccessToken()
            case "user_type":
                return self.AccountObject.getShortType()
            case "version_name":
                return self.VersionInfos.Name
            case "version_type":
                return (
                    f"{self._replaces('launcher_name')}-{self._replaces('launcher_version')}"
                )
            case "classpath":
                return getClassPath(
                    VersionJson=self.VersionInfos.VersionJson,
                    VersionJarPath=self.VersionInfos.JarPath,
                    Features=Features,
                )
            case "classpath_separator":
                return System.get(Format={"Windows": ""}) # TODO: ???
            case "natives_directory":
                return self.VersionInfos.NativesPath
            case "game_directory":
                return (
                    self.VersionInfos.Dir
                    if self.VersionInfos.getConfig("VersionIndependent")
                    else path("$MINECRFT", IsPath=True)
                )
            case "clientid":
                return uuid4().hex
            case "resolution_width":
                return self.VersionInfos.getConfig("WindowWidth")
            case "resolution_height":
                return self.VersionInfos.getConfig("WindowHeight")
            case "library_directory":
                return path("$LIBRERIES", IsPath=True)
            case "user_properties":
                return "{}"
            case _:
                raise KeyError(Key)

    def getJavaPathAndInfo(self, NotCheck: bool = False) -> JavaInfo:
        JavaPath = self.VersionInfos.getConfig("JavaPath")
        recommendJavaVersion: int | None = self.VersionInfos.VersionJson["javaVersion"][
            "majorVersion"
        ]
        if JavaPath == "AUTOPICK":
            return autoPickJava(recommendJavaVersion)
        else:
            if not NotCheck:
                if not dfCheck(Path=JavaPath, Type="f"):
                    self.VersionInfos.setConfig(Keys="JavaPath", Value="AUTOPICK")
                    return self.getJavaPathAndInfo()
                JavaInfo = getJavaInfo(Path=JavaPath)
                if isinstance(recommendJavaVersion, int):
                    if recommendJavaVersion > JavaInfo["Version"][0]:
                        Logger.warning(
                            "Java version %s too old, recommend Java Version is [%s," " 0, 0]",
                            JavaInfo["Version"],
                            recommendJavaVersion,
                        )
                    elif recommendJavaVersion < JavaInfo["Version"][0]:
                        Logger.warning(
                            "Java version %s too new, recommend Java Version is [%s," " 0, 0]",
                            JavaInfo["Version"],
                            recommendJavaVersion,
                        )
                return JavaInfo
            else:
                return {"Path": JavaPath}
