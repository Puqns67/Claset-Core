# -*- coding: utf-8 -*-
"""游戏启动器"""

from logging import getLogger
from re import compile as reCompile
from typing import Any
from subprocess import Popen, DEVNULL
from uuid import uuid4

from Claset import __fullversion__, __productname__, LaunchedGames
from Claset.Accounts import AccountManager, Account
from Claset.Game.Utils import ResolveRule, getClassPath, processNatives, getLog4j2Infos
from Claset.Utils import Configs, pathAdder, loadFile, dfCheck, path, getValueFromDict
from Claset.Utils.JavaHelper import autoPickJava, fixJavaPath, getJavaInfoList, JavaInfo

from .Exceptions import *

Logger = getLogger(__name__)


class GameLauncher():
    """游戏启动器"""
    MatchRunCodeKey = reCompile(r"^(.*)\$\{(.+)\}(.*)$")
    Features: dict[str, bool] = {"is_demo_user": False, "has_custom_resolution": True}
    ClasetJvmHeader: list[str] = ["-XX:+UnlockExperimentalVMOptions", "-XX:+UseG1GC", "-XX:G1NewSizePercent=20", "-XX:G1ReservePercent=20", "-XX:MaxGCPauseMillis=50", "-XX:G1HeapRegionSize=16m", "-XX:-UseAdaptiveSizePolicy", "-XX:-OmitStackTraceInFastThrow", "-XX:-DontCompileHugeMethods"]

    def __init__(self, VersionName: str, Account: Account | None = None):
        self.VersionName = VersionName
        if Account == None:
            self.AccountObject = AccountManager().getAccountObject()
        else:
            self.AccountObject = Account

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


    def launchGame(self, PrintToTerminal: bool = True) -> None:
        """启动游戏"""
        RunArgs = self.getRunArgs()
        self.PickedJava = self.getJavaPathAndInfo()

        processNatives(VersionJson=self.VersionJson, ExtractTo=self.NativesPath, Features=self.Features)
        Logger.info("Launch Game: %s", self.VersionName)
        Logger.debug("Run code: %s", RunArgs)
        if PrintToTerminal:
            self.Game = Popen(args=[self.PickedJava["Path"]] + RunArgs, cwd=self.VersionDir)
        else:
            self.Game = Popen(args=[self.PickedJava["Path"]] + RunArgs, cwd=self.VersionDir, stdout=DEVNULL)
        LaunchedGames.append(self)


    def waitGame(self) -> None:
        if self.Game:
            self.Game.wait()


    def stopGame(self) -> None:
        if self.Game:
            self.Game.terminate()


    def getRunArgs(self) -> list[str]:
        return(self.processRunArgsList(self.getRunArgsList()))


    def getRunArgsList(self, Type: str | None = None) -> list[str]:
        match self.VersionJson["complianceLevel"]:
            case 0:
                return(
                    [
                        "${CLASETJVMHEADER}", "${JVMPREFIX}", "${MEMMIN}",
                        "${MEMMAX}", "${LOG4J2_CONFIG}", "${JVMEND}",
                        "-Djava.library.path=${natives_directory}",
                        "-Dminecraft.launcher.brand=${launcher_name}",
                        "-Dminecraft.launcher.version=${launcher_version}",
                        "-cp", "${classpath}",
                        "${MAINCLASS}", "${GAMEARGSPREFIX}"
                    ] + self.VersionJson["minecraftArguments"].split() + ["${GAMEARGSEND}"]
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
                        Arguments.extend(("${LOG4J2_CONFIG}", "${JVMEND}", "${MAINCLASS}", "${GAMEARGSPREFIX}",))
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
                    Output.extend(Replaced)
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
            case "LOG4J2_CONFIG": return(getLog4j2Infos(InitFile=self.VersionJson, Type="Argument"))
            case "MAINCLASS": return(self.VersionJson["mainClass"])
            case "launcher_name": return(__productname__)
            case "launcher_version": return(__fullversion__)
            case "assets_root": return(path("$ASSETS", IsPath=True))
            case "assets_index_name": return(self.VersionJson["assets"])
            case "auth_player_name": return(self.AccountObject.Name)
            case "auth_access_token": return(self.AccountObject.getAccessToken())
            case "auth_uuid": return(self.AccountObject.UUID.hex)
            case "user_type": return(self.AccountObject.Type.lower())
            case "auth_xuid": return(uuid4().hex)
            case "version_name": return(self.VersionName)
            case "version_type": return(self._replaces("launcher_name") + " " + self._replaces("launcher_version"))
            case "classpath": return(getClassPath(VersionJson=self.VersionJson, VersionJarPath=self.VersionJarPath, Features=self.Features))
            case "natives_directory": return(self.NativesPath)
            case "game_directory": return(self.VersionDir)
            case "clientid": return(uuid4().hex)
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


    def getJavaPathAndInfo(self) -> JavaInfo:
        JavaPath = self.getConfig(["JavaPath"])
        recommendJavaVersion: int = self.VersionJson["javaVersion"]["majorVersion"]
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

