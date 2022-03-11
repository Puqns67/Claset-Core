# -*- coding: utf-8 -*-

from platform import system, machine, version

from .Exceptions.Claset import UnsupportSystemHost

__all__ = ("System", "Arch", "Version",)

try:
    System = {"Windows": "windows", "Darwin": "osx", "Linux": "linux"}[system()]
except KeyError:
    raise UnsupportSystemHost(system())

Arch = {"amd64": "x64", "x86_64": "x64", "x64": "x64", "i386": "x86", "x86": "x86", "i686": "x86"}[machine().lower()]

Version = version()

