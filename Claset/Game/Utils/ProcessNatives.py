# -*- coding: utf-8 -*-

from logging import getLogger
from zipfile import ZipFile, Path as ZipPath, is_zipfile as isZipFile
from os.path import basename as baseName, splitext as splitExt
from hashlib import sha1
from copy import deepcopy as deepCopy

from Claset.Utils import pathAdder, saveFile

from .LoadJson import getNativesObject

from .Exceptions import NativesFileError, Sha1VerificationError

__all__ = ("processNatives",)
Logger = getLogger(__name__)


def processNatives(VersionJson: dict, ExtractTo: str, Features: dict | None = None):
    """处理 Natives"""
    for Libraries in VersionJson["libraries"]:
        NativesObject = getNativesObject(Libraries=Libraries, Features=Features, getExtract=True)
        if NativesObject != None:
            Path = pathAdder("$LIBRERIES", NativesObject["path"])
            Extract: dict = NativesObject["Extract"]
            BaseNameByPath = baseName(Path)

            if not(isZipFile(Path)): raise NativesFileError
            Logger.info("Extract Natives: %s", BaseNameByPath)
            File = ZipFile(file=Path, mode="r")
            FileList = File.namelist()

            # 分离 sha1 文件, 并生成 File Sha1 的对应关系, 存入 FileSha1
            FileSha1 = dict()
            FileListBackUp = deepCopy(FileList)
            for FilePathInZip in FileListBackUp:
                Name, Ext = splitExt(FilePathInZip)
                TheZipPath = ZipPath(File, at=FilePathInZip)
                if Ext == ".git":
                    FileList.remove(FilePathInZip)
                    Logger.debug("Excluded: \"%s\" From \"%s\" By file extension name", FilePathInZip, BaseNameByPath)
                elif Ext == ".sha1":
                    FileList.remove(FilePathInZip)
                    # 读取对应的 sha1 值
                    Sha1 = File.read(FilePathInZip).decode("utf-8")
                    if Sha1[-1] == "\n": Sha1 = Sha1.rstrip()
                    # 存入 FileSha1
                    FileSha1[Name] = Sha1
                elif TheZipPath.is_dir():
                    FileList.remove(FilePathInZip)
                elif ((Extract != None) and ("exclude" in Extract.keys())):
                    for Exclude in Extract["exclude"]:
                        if Exclude in FilePathInZip:
                            FileList.remove(FilePathInZip)
                            Logger.debug("Excluded: \"%s\" From \"%s\" By Extract", FilePathInZip, BaseNameByPath)
                            break

            FileSha1Keys = FileSha1.keys()

            for FilePathInZip in FileList:
                TheFile = File.read(FilePathInZip)
                if (FilePathInZip in FileSha1Keys):
                    if not (sha1(TheFile).hexdigest() == FileSha1[FilePathInZip]):
                        raise Sha1VerificationError

                RealFilePath = pathAdder(ExtractTo, FilePathInZip)
                saveFile(Path=RealFilePath, FileContent=TheFile, Type="bytes")

