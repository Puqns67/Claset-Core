# -*- coding: utf-8 -*-

from ast import For
from platform import system, machine, version
from typing import Any

from .Exceptions.Claset import UnsupportSystemHost

__all__ = (
    "System",
    "Arch",
    "Version",
    "OriginalSystem",
    "OriginalArch",
    "OriginalVersion",
    "formatPlatform",
)
SystemFormats = {"Minecraft": {"Windows": "windows", "Darwin": "osx", "Linux": "linux"}}
ArchFormats = {
    "Minecraft": {
        "amd64": "x64",
        "x86_64": "x64",
        "x64": "x64",
        "i386": "x86",
        "x86": "x86",
        "i686": "x86",
    }
}
OriginalSystem = system()
OriginalArch = machine()
OriginalVersion = version()


class Base:
    """用于获取各类风格的 Platform 字符串基类"""

    Source = str()

    def formats(self, format: str, Raise: Exception | None = None) -> str:
        """格式化方法"""
        return self.Source

    def get(
        self, Format: str | dict = "Python", Raise: Exception | None = None
    ) -> str | Any:
        """用于获取各类风格的 Platform 字符串"""
        if isinstance(Format, str):
            return self.formats(format=Format, Raise=Raise)
        elif isinstance(Format, dict):
            try:
                return Format[self.Source]
            except KeyError:
                if "Other" in Format:
                    return Format["Other"]
                raise Raise(self.Source) if Raise else KeyError(self.Source)

        else:
            raise TypeError(Format)

    def getLower(self, Format: str = "Python") -> str:
        return self.get(Format=Format).lower()

    def getUpper(self, Format: str = "Python") -> str:
        return self.get(Format=Format).upper()


class System(Base):
    """用于获取各类风格的 System 字符串"""

    Source = OriginalSystem

    def formats(self, format: str, Raise: Exception | None = None) -> str:
        """格式化方法"""
        match format:
            case "Minecraft":
                try:
                    return SystemFormats["Minecraft"][OriginalSystem]
                except KeyError:
                    raise UnsupportSystemHost(system())
            case "Python":
                return OriginalSystem
            case _:
                raise ValueError(format) if Raise is not None else Exception(format)


class Arch(Base):
    """用于获取各类风格的 Arch 字符串"""

    Source = OriginalArch

    def formats(self, format: str, Raise: Exception | None = None) -> str:
        """格式化方法"""
        match format:
            case "Minecraft":
                return ArchFormats["Minecraft"][OriginalArch.lower()]
            case "PureNumbers":
                return self.get(Format="Minecraft").replace("x", str())
            case "Python":
                return OriginalArch
            case _:
                raise ValueError(format) if Raise is not None else Exception(format)


class Version(Base):
    """用于获取各类风格的 Version 字符串"""

    Source = OriginalVersion

    def formats(self, format: str, Raise: Exception | None = None) -> str:
        """格式化方法"""
        match format:
            case "Python":
                return OriginalVersion
            case _:
                raise ValueError(format) if Raise is not None else Exception(format)


def formatPlatform(
    String: str,
    Formats: dict = {
        "System": {"Type": "System"},
        "Arch": {"Type": "Arch"},
        "Version": {"Type": "Version"},
    },
) -> str:
    """
    使用各异的格式格式化字符串
    * String: 格式字符串, 以 {KEYNAME} 格式输入
    * Formats: 格式形如 {"KEYNAME": {"Type": "Type name", "Format": "Format name"}, ...}
    """
    Formated = dict()

    """获取格式化后的对应字符串"""
    for Key in Formats:
        Formater = {"System": System, "Arch": Arch, "Version": Version}[
            Formats[Key]["Type"]
        ]
        Formated[Key] = (
            Formater().get(Formats[Key]["Format"])
            if Formats[Key].get("Format") is not None
            else Formater().get()
        )

    return String.format_map(Formated)
