# -*- coding: utf-8 -*-

from zipfile import ZipFile, is_zipfile
from subprocess import Popen, run
from hashlib import sha1

from Claset.Utils import (
    DownloadTask,
    FileTypes,
    System,
    autoPickJava,
    path,
    dfCheck,
    loadFile,
    saveFile,
)
from Claset.Utils.Exceptions.File import UnsupportType

from .Exceptions import UnsupportedModLoaderType
from .Instance import InstanceInfos
from .Others import parseLibraryName

__all__ = (
    "Processor",
    "InstallProfileLoader",
)


class Processor:
    def __init__(
        self,
        RawProcessor: dict[str, str | list[str] | dict[str, str]],
        Formats: dict,
        JavaExecutablePath: str | None = None,
    ) -> None:
        self.JavaExecutablePath = JavaExecutablePath
        self.JarPath = parseLibraryName(RawProcessor["jar"])

        self.Args = list()
        for i in RawProcessor["args"]:
            if i[0] == "[" and i[-1] == "]":
                self.Args.append(parseLibraryName(i[1:-1]))
            else:
                self.Args.append(i.format_map(Formats))

        self.Classpath = list()
        for i in RawProcessor["classpath"]:
            self.Classpath.append(parseLibraryName(i))

        self.Outputs = dict()
        if "outputs" in RawProcessor:
            for i in RawProcessor["outputs"]:
                self.Outputs[i.format_map(Formats)] = RawProcessor["outputs"][i].format_map(
                    Formats
                )

    def genRunArgs(self) -> list:
        """生成命令"""
        splitBy = System().get(Format={"Windows": ";", "Other": ":"})
        return ["-cp", splitBy.join(self.Classpath), "-jar", self.JarPath] + self.Args

    def excute(self) -> None:
        """执行本操作器"""
        JavaExecutablePath = (
            self.JavaExecutablePath if self.JavaExecutablePath else autoPickJava()["Path"]
        )
        self.Return = run(args=[JavaExecutablePath] + self.genRunArgs())
        for i in self.Outputs:
            if not (
                sha1(loadFile(Path=i, Type=FileTypes.Bytes)).hexdigest() == self.Outputs[i]
            ):
                raise


class InstallProfileLoader:
    ProfileType = None

    def __init__(self, InstallerPath: str) -> None:
        self.InstallerPath = path(InstallerPath, IsPath=True)
        if not dfCheck(InstallerPath, Type="d", NotFormat=True):
            raise FileNotFoundError(InstallerPath)
        if not is_zipfile(str(InstallerPath)):
            raise UnsupportType(InstallerPath)

        self.Installer = ZipFile(InstallerPath, mode="r")

    def __del__(self) -> None:
        """释放函数"""
        self.Installer.close()

    def extractFromInstaller(self, Path: str) -> str:
        """从 Installer 中提取文件"""
        ExtractTo = path(f"$CACHE/ForgeInstaller/{Path}", IsPath=True)
        saveFile(
            Path=ExtractTo,
            FileContent=self.Installer.read(Path[1:] if Path[0] in ("/", "\\") else Path),
            Type=FileTypes.Bytes,
            NotFormat=True,
        )
        return ExtractTo

    def loadForgeInstallProfile(self):
        self.InstallProfile: dict = loadFile(
            Path=self.extractFromInstaller("install_profile.json"),
            Type=FileTypes.Json,
            NotFormat=True,
        )

        self.RawProcessors = self.InstallProfile["processors"]

        self.Spec = self.InstallProfile.get("spec", 0)
        self.ProfileType = self.InstallProfile["profile"]
        self.Version = self.InstallProfile["version"]
        self.MinecraftVersion = self.InstallProfile["minecraft"]
        self.Libraries = self.InstallProfile["libraries"]
        self.JsonPath = self.extractFromInstaller(self.InstallProfile["json"])

    def loadNext(self, InstanceInfo: InstanceInfos) -> None:
        """下一步加载"""
        match self.ProfileType:
            case "forge":
                InstanceType = InstanceInfo.InstanceType.lower()
                OldData: dict | None = self.InstallProfile.get("data")
                self.Data = dict()

                if OldData is not None:
                    for Keys in OldData.keys():
                        content = OldData[Keys][InstanceType]
                        if content[0] == "[" and content[-1] == "]":
                            self.Data[Keys] = parseLibraryName(content[1:-1])
                        elif content[0] == "'" and content[-1] == "'":
                            self.Data[Keys] = content[1:-1]
                        else:
                            self.Data[Keys] = self.extractFromInstaller(content)

                self.Data["SIDE"] = InstanceType
                self.Data["MINECRAFT_JAR"] = InstanceInfo.JarPath
                self.Data["MINECRAFT_VERSION"] = self.MinecraftVersion
                self.Data["ROOT"] = path("$MINECRFT", IsPath=True)
                self.Data["INSTALLER"] = self.InstallerPath
                self.Data["LIBRARY_DIR"] = path("$LIBRERIES", IsPath=True)

                # 使用实例信息中的实例类型获取需要执行的 processers
                PickedJava = autoPickJava()
                self.Processors: list[Processor] = list()
                for i in self.RawProcessors:
                    if "sides" in i:
                        if InstanceType not in i["sides"]:
                            continue

                    # 处理其中的数据
                    self.Processors.append(
                        Processor(
                            RawProcessor=i,
                            Formats=self.Data,
                            JavaExecutablePath=PickedJava["Path"],
                        )
                    )
            case _:
                raise UnsupportedModLoaderType(self.ProfileType)

    def getLibrariesDownloadTasks(self) -> list[DownloadTask]:
        """获取库的 DownloadTask 列表"""
        Output = list()
        for i in self.Libraries:
            Artifact = i["downloads"]["artifact"]
            Output.append(
                DownloadTask(
                    URL=Artifact["url"],
                    Size=Artifact["size"],
                    Sha1=Artifact["sha1"],
                    OutputPaths=parseLibraryName(i["name"]),
                    Overwrite=False,
                )
            )

        return Output
