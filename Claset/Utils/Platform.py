# -*- coding: utf-8 -*-

from platform import system, machine, version

from .Exceptions.Claset import UnsupportSystemHost

__all__ = ("System", "Arch", "Version", "OriginalSystem", "OriginalArch", "OriginalVersion",)
SystemFormats = {"Minecraft": {"Windows": "windows", "Darwin": "osx", "Linux": "linux"}}
ArchFormats = {"Minecraft": {"amd64": "x64", "x86_64": "x64", "x64": "x64", "i386": "x86", "x86": "x86", "i686": "x86"}}
OriginalSystem = system()
OriginalArch = machine()
OriginalVersion = version()


class Base():
    def getLower(self, Format: str = "Python") -> str:
        return(self.getFormated(Format=Format).lower())


    def getUpper(self, Format: str = "Python") -> str:
        return(self.getFormated(Format=Format).upper())


class System(Base):
    """用于方便获取各类风格的 System 字符串"""
    def getFormated(self, Format: str = "Python") -> str:
        """返回已格式化的 System 字符串"""
        match Format:
            case "Minecraft":
                try:
                    return(SystemFormats["Minecraft"][OriginalSystem])
                except KeyError:
                    raise UnsupportSystemHost(system())
            case "Python": return(OriginalSystem)
            case _: raise ValueError(Format)


class Arch(Base):
    def getFormated(self, Format: str = "Python") -> str:
        match Format:
            case "Minecraft": return(ArchFormats["Minecraft"][OriginalArch.lower()])
            case "PureNumbers": return(self.getFormated(Format="Minecraft").replace("x", str()))
            case "Python": return(OriginalArch)
            case _: raise ValueError(Format)


class Version(Base):
    def getFormated(self, Format: str = "Python") -> str:
        match Format:
            case "Python": return(OriginalVersion)
            case _: raise ValueError(Format)

