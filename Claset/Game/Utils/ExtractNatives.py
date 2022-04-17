# -*- coding: utf-8 -*-

from logging import getLogger
from zipfile import ZipFile, Path as ZipPath, is_zipfile as isZipFile
from os.path import basename as baseName, splitext as splitExt
from hashlib import sha1
from copy import deepcopy as deepCopy

from Claset.Utils import pathAdder, saveFile
from Claset.Utils.File import dfCheck, loadFile

from .LoadJson import getNativesObject

from .Exceptions import NativesFileError, Sha1VerificationError

__all__ = ("extractNatives",)
Logger = getLogger(__name__)


def extractNatives(VersionJson: dict, ExtractTo: str, Features: dict | None = None):
    """提取 Natives"""
    for Libraries in VersionJson["libraries"]:
        NativesObject = getNativesObject(Libraries=Libraries, Features=Features, getExtract=True)
        if NativesObject is not None:
            Path = pathAdder("$LIBRERIES", NativesObject["path"])
            Extract: dict = NativesObject["Extract"]
            BaseNameByPath = baseName(Path)

            if not(isZipFile(Path)): raise NativesFileError
            Logger.info("Extract Natives: %s", BaseNameByPath)
            File = ZipFile(file=Path, mode="r")
            FileList = File.namelist()

            # 分离 sha1 文件, 并生成 File Sha1 的对应关系, 存入 FileSha1
            FileSha1 = dict()
            FileListBackup = deepCopy(FileList)
            for FilePathInZip in FileListBackup:
                Name, Ext = splitExt(FilePathInZip)
                TheZipPath = ZipPath(File, at=FilePathInZip)
                if Ext == ".git":
                    FileList.remove(FilePathInZip)
                    Logger.debug("Excluded: \"%s\" From \"%s\" By file extension name", FilePathInZip, BaseNameByPath)
                elif Ext == ".sha1":
                    FileList.remove(FilePathInZip)
                    # 读取对应的 sha1 值, 并存入 FileSha1
                    FileSha1[Name] = File.read(FilePathInZip).decode("utf-8").rstrip()
                elif TheZipPath.is_dir():
                    FileList.remove(FilePathInZip)
                elif ((Extract is not None) and ("exclude" in Extract)):
                    for Exclude in Extract["exclude"]:
                        if Exclude in FilePathInZip:
                            FileList.remove(FilePathInZip)
                            Logger.debug("Excluded: \"%s\" From \"%s\" By Extract", FilePathInZip, BaseNameByPath)
                            break

            for FilePathInZip in FileList:
                RealFilePath = pathAdder(ExtractTo, FilePathInZip)
                if dfCheck(Path=RealFilePath, Type="f"):
                    if FilePathInZip in FileSha1:
                        if (sha1(loadFile(Path=RealFilePath, Type="bytes")).hexdigest() == FileSha1[FilePathInZip]):
                            continue
                TheFile = File.read(FilePathInZip)
                if FilePathInZip in FileSha1:
                    if not (sha1(TheFile).hexdigest() == FileSha1[FilePathInZip]):
                        raise Sha1VerificationError
                saveFile(Path=RealFilePath, FileContent=TheFile, Type="bytes")

