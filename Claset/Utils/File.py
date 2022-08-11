# -*- coding: utf-8 -*-
"""用于读取/写入/检查文件"""

from json import dumps, load
from logging import getLogger
from os import makedirs, remove as removeFile
from os.path import basename, dirname, exists, getsize, isdir, isfile
from shutil import move, copy2 as copyFile, rmtree as removeDir
from tarfile import open as openTar
from enum import Enum, auto

from zstandard import ZstdCompressor, ZstdDecompressor

from .Path import pathAdder, path as Pathmd

from .Exceptions.File import UnsupportType

__all__ = (
    "FileTypes",
    "loadFile",
    "saveFile",
    "copyFile",
    "moveFile",
    "dfCheck",
    "removeFile",
    "removeDir",
    "compressFile",
    "decompressFile",
    "makeArchive",
    "addFileIntoArchive",
)
Logger = getLogger(__name__)


class FileTypes(Enum):
    Text = auto()
    Bytes = auto()
    Json = auto()
    Log = auto()
    Zstandard = auto()


def loadFile(
    Path: str, Type: FileTypes = FileTypes.Text, NotFormat: bool = False
) -> dict | bytes | str:
    """
    加载文件
    * Path: 文件路径
    * Type: 类型(json, bytes, text)
    """
    if not NotFormat:
        Path = Pathmd(Path, IsPath=True)

    Logger.debug('Path: "%s", Type: "%s"', Path, Type)

    match Type:
        case FileTypes.Json:
            with open(file=Path, mode="r", encoding="UTF-8") as openedfile:
                return load(openedfile)
        case FileTypes.Bytes:
            with open(file=Path, mode="rb") as openedfile:
                return openedfile.read()
        case FileTypes.Text:
            with open(file=Path, mode="r", encoding="UTF-8") as openedfile:
                return openedfile.read()
        case _:
            raise UnsupportType(Type)


def saveFile(
    Path: str,
    FileContent: str | bytes,
    Type: FileTypes = FileTypes.Text,
    NotFormat: bool = False,
) -> None:
    """
    保存文件
    * Path: 文件路径
    * FileContent: 文件内容
    * Type: 类型(json, bytes, log, text)
    """
    if not NotFormat:
        Path = Pathmd(Path, IsPath=True)

    Logger.debug('Path: "%s", Type: "%s", FileContent Type: %s', Path, Type, type(FileContent))

    dfCheck(Path=Path, Type="fm", NotFormat=NotFormat)

    match Type:
        case FileTypes.Json:
            with open(Path, mode="w+", encoding="UTF-8") as thefile:
                thefile.write(dumps(FileContent, indent=4, ensure_ascii=False))
        case FileTypes.Bytes:
            with open(Path, mode="wb+") as thefile:
                thefile.write(FileContent)
        case FileTypes.Log:
            with open(Path, mode="a+", encoding="UTF-8") as thefile:
                thefile.write(FileContent)
        case FileTypes.Text:
            with open(Path, mode="w+", encoding="UTF-8") as thefile:
                thefile.write(FileContent)
        case _:
            raise UnsupportType(Type)


def moveFile(File: str, To: str, OverWrite: bool = True, Rename: bool = False) -> None:
    """
    移动文件: 较为稳定的移动文件方式
    * File: 源文件位置
    * To: 目标文件夹/目标路径(重命名)
    * OverWirte: 若目标文件夹指向文件, 此时 OverWrite 为 False 则触发 FileExistsError, 若为 True 则覆盖
    * Rename: 若无法分辨 To 为"目标文件夹"还是"目标路径"时, 此时 Rename 为 True 则视为"目标路径", 若为 False 则为"目标文件夹"
    """

    Logger.debug('Path: "%s", To: "%s"', File, To)

    if not dfCheck(Path=File, Type="f"):
        raise FileNotFoundError(File)

    if isdir(To):
        # 若为文件夹, 则检查在其中是否有与源文件重名的文件
        ToFile = pathAdder(To, basename(File))
        if dfCheck(Path=ToFile, Type="f"):
            if OverWrite:
                removeFile(ToFile)
            else:
                raise FileExistsError(ToFile)
        else:
            To = ToFile
    elif isfile(To):
        # 若为文件, 此时 OverWrite 为 False 则触发 FileExistsError, 若为 True 则覆盖
        if OverWrite:
            removeFile(To)
        else:
            raise FileExistsError(To)
    else:
        # 若目标文件夹不为文件夹也不为文件则判断是否需要覆盖, 若 Rename 为 True 则优先判定其为重命名
        if not Rename:
            dfCheck(Path=To, Type="dm")

    move(src=File, dst=To)


def compressFile(
    Type: FileTypes, SourceFilePath: str, ToFilePath: str, CompressLevel: int = 8
):
    """
    压缩文件
    * Type: 文档类型
    * SourceFilePath: 源文件位置
    * ToFilePath: 压缩后文件位置
    * CompressLevel: 压缩等级
    """
    # 读取
    SourceFile = loadFile(Path=SourceFilePath, Type=FileTypes.Bytes)

    # 压缩
    match Type:
        case FileTypes.Zstandard:
            Compressor = ZstdCompressor(level=CompressLevel, threads=-1)
            FileContent = Compressor.compress(SourceFile)
        case _:
            raise UnsupportType(Type)

    # 保存
    saveFile(Path=ToFilePath, FileContent=FileContent, Type=FileTypes.Bytes)


def decompressFile(Type: FileTypes, SourceFilePath: str, ToFilePath: str):
    """
    解压文件
    * AType: 文档类型
    * SourceFilePath: 源文件位置
    * ToFilePath: 解压后文件位置
    """
    # 读取
    SourceFile = loadFile(Path=SourceFilePath, Type=FileTypes.Bytes)

    # 压缩
    match Type:
        case FileTypes.Zstandard:
            Compressor = ZstdDecompressor()
            FileContent = Compressor.decompress(SourceFile)
        case _:
            raise UnsupportType(Type)

    # 保存
    saveFile(Path=ToFilePath, FileContent=FileContent, Type=FileTypes.Bytes)


def dfCheck(Path: str, Type: str, Size: int | None = None, NotFormat: bool = False) -> bool:
    """
    检测文件夹/文件是否存在和体积是否正常\n
    在输入 Type 不存在时触发 UnsupportType\n
    * Path: 对象路径
    * Type: 检查选项
    * Size: 对应的文件大小(字节), 用于匹配大小\n
    检查选项
    * f: 检测文件是否存在, 也可检测文件夹
    * d: 检测文件夹是否存在, 也可检测文件
    * dm: 创建文件夹
    * fm: 建立对应的文件夹
    * fs: 对比输入的 Size, 在文件不存在时触发 FileNotFoundError, Size 为空时触发 UnsupportType\n
    若选项有误则触发 UnsupportType
    """
    if not NotFormat:
        Path = Pathmd(Path, IsPath=True)

    if "d" in Type:
        if "m" in Type:
            try:
                makedirs(Path)
            except FileExistsError:
                return True
            return False
        return exists(Path)
    elif "f" in Type:
        if "s" in Type:
            if not dfCheck(Path=Path, Type="f"):
                raise FileNotFoundError(Path)
            FileSize = getsize(Path)
            return False if Size != FileSize else True
        elif "m" in Type:
            try:
                makedirs(dirname(Path))
            except FileExistsError:
                return True
            return False
        return exists(Path)
    else:
        raise UnsupportType(Type)


def makeArchive(
    SourcePaths: str,
    ArchivePath: str,
    Type: FileTypes = FileTypes.Zstandard,
    CompressLevel: int = 8,
) -> None:
    """
    制作存档
    * SourcePaths: 源文件/文件夹地址
    * ArchivePath: 保存至的文件路径
    * Type: 存档文件类型, 暂只支持 "Zstandard"
    * CompressLevel: 压缩等级, 某些压缩类型支持
    """
    FullSourcePaths = Pathmd(SourcePaths, IsPath=True)
    ArchivePath = Pathmd(ArchivePath, IsPath=True)
    SourcePaths = basename(FullSourcePaths)
    TempFilePath = ArchivePath + ".TempTarFile"

    if dfCheck(Path=TempFilePath, Type="f"):
        removeFile(TempFilePath)

    with openTar(name=TempFilePath, mode="x") as File:
        File.add(name=FullSourcePaths, arcname=SourcePaths)

    compressFile(
        Type=Type,
        SourceFilePath=TempFilePath,
        ToFilePath=ArchivePath,
        CompressLevel=CompressLevel,
    )

    removeFile(TempFilePath)


def addFileIntoArchive(
    ArchivePath: str,
    SourcePaths: list[str] | str,
    Type: FileTypes = FileTypes.Zstandard,
    ArcnamePerfix: str | None = None,
) -> None:
    """
    添加文件至存档
    * ArchivePath: 存档的文件路径
    * SourcePaths: 源文件/文件夹地址
    * Type: 存档文件类型, 暂只支持 "Zstandard"
    * ArcnamePerfix: 添加至存档内的路径
    """
    ArchivePath = Pathmd(ArchivePath, IsPath=True)
    TempFilePath = ArchivePath + ".TempTarFile"

    if isinstance(SourcePaths, str):
        SourcePaths = [SourcePaths]

    # 解压
    decompressFile(Type=Type, SourceFilePath=ArchivePath, ToFilePath=TempFilePath)
    removeFile(ArchivePath)

    # 添加
    with openTar(name=TempFilePath, mode="a") as File:
        for SourcePath in SourcePaths:
            SourcePath = Pathmd(SourcePath, IsPath=True)
            Arcname = basename(SourcePath)
            if ArcnamePerfix is not None:
                Arcname = ArcnamePerfix + "/" + Arcname
            File.add(name=SourcePath, arcname=Arcname)

    # 压缩
    compressFile(Type=Type, SourceFilePath=TempFilePath, ToFilePath=ArchivePath)

    # 移除缓存
    removeFile(TempFilePath)
