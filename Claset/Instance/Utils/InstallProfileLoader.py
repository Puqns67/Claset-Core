# -*- coding: utf-8 -*-

from zipfile import ZipFile, is_zipfile

from Claset.Utils import (
    FileTypes,
    path,
    dfCheck,
    loadFile,
    saveFile,
)
from Claset.Utils.Exceptions.File import UnsupportType

from .Exceptions import UnsupportedModLoaderType
from .Instance import InstanceInfos

__all__ = ("InstallProfile",)


class InstallProfile:
    def __init__(self, InstallerPath: str):
        self.InstallerPath = path(InstallerPath, IsPath=True)
        if not dfCheck(InstallerPath, Type="d", NotFormat=True):
            raise FileNotFoundError(InstallerPath)
        if not is_zipfile(str(InstallerPath)):
            raise UnsupportType(InstallerPath)

        self.Installer = ZipFile(InstallerPath, mode="r")

    def __del__(self):
        """释放函数"""
        self.Installer.close()

    def extractFromInstaller(self, Path: str) -> str:
        """从 Installer 中提取文件"""
        ExtractTo = path(f"$CACHE/ForgeInstaller/{Path}", IsPath=True)
        saveFile(
            Path=ExtractTo,
            FileContent=self.Installer.read(
                Path[1:] if Path[0] in ("/", "\\") else Path
            ),
            Type=FileTypes.Bytes,
            NotFormat=True,
        )
        return ExtractTo

    def loadForgeInstallProfile(self):
        self.InstallProfile = loadFile(
            Path=self.extractFromInstaller("install_profile.json"),
            Type=FileTypes.Json,
            NotFormat=True,
        )

        self.Spec = self.InstallProfile.get("spec", 0)
        self.ProfileType = self.InstallProfile["profile"]
        self.Version = self.InstallProfile["version"]
        self.MinecraftVersion = self.InstallProfile["minecraft"]
        self.Libraries = self.InstallProfile["libraries"]
        self.Processors = self.InstallProfile["processors"]
        self.JsonPath = self.extractFromInstaller(self.InstallProfile["json"])

    def loadNext(self, InstanceInfo: InstanceInfos) -> None:
        """下一步加载"""
        match self.ProfileType:
            case "forge":
                OldData: dict | None = self.InstallProfile.get("data")
                self.Data = dict()

                if OldData is not None:
                    for Keys in OldData.keys():
                        content = OldData[Keys][InstanceInfo.InstanceType.lower()]
                        if content[0] == "[" and content[-1] == "]":
                            self.Data[Keys] = "WIP"
                        elif content[0] == "'" and content[-1] == "'":
                            self.Data[Keys] = content[1:-1]
                        else:
                            self.Data[Keys] = self.extractFromInstaller(content)

                self.Data["SIDE"] = InstanceInfo.InstanceType.lower()
                self.Data["MINECRAFT_JAR"] = InstanceInfo.JarPath
                self.Data["MINECRAFT_VERSION"] = self.MinecraftVersion
                self.Data["ROOT"] = path("$MINECRFT", IsPath=True)
                self.Data["INSTALLER"] = self.InstallerPath
                self.Data["LIBRARY_DIR"] = path("$LIBRERIES", IsPath=True)
            case _:
                raise UnsupportedModLoaderType(self.ProfileType)
