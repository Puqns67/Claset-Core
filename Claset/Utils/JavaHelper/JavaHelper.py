# -*- coding: utf-8 -*-
"""获取 Java 的相关信息"""

from logging import getLogger
from os import scandir
from subprocess import run
from re import compile

from zstandard import decompress

from Claset.Utils import pathAdder, saveFile, dfCheck, fixType, OriginalSystem
from Claset.Utils.Exceptions.Claset import UnsupportSystemHost
from Claset.Utils.Platform import System

from .Exceptions import MatchStringError, JavaNotFound

__all__ = (
    "getJavaPath",
    "getJavaInfo",
    "versionFormater",
    "autoPickJava",
    "getJavaInfoList",
    "fixJavaPath",
    "genJarFile",
    "JavaInfo",
)
Logger = getLogger(__name__)
ReMatchJavaInfos = compile(
    r"\s*os\.arch=\"(.+)\"\s*java\.version=\"(.+)\"\s*java\.vendor=\"(.+)\"\s*"
)
JavaInfo = dict[str, str | tuple[int]]


def getJavaPath() -> list[str]:
    """获取 Java 路径列表"""
    InstallPaths = System().get(
        Format={
            "Windows": (
                "C:\\Program Files\\",
                "C:\\Program Files (x86)\\",
            ),
            "Linux": ("/usr/lib/jvm",)
            # TODO: MacOS 位置缺失, 需补充
        },
        Raise=UnsupportSystemHost,
    )
    JavaExecutableFileName = System().get(
        Format={"Windows": "java.exe", "Linux": "java", "Darwin": "java"},
        Raise=UnsupportSystemHost,
    )

    Output = list()

    for InstallPath in InstallPaths:
        if dfCheck(Path=InstallPath, Type="d"):
            for one in scandir(InstallPath):
                if one.is_dir(follow_symlinks=False):
                    javaPath = pathAdder(one.path, "bin", JavaExecutableFileName)
                    if dfCheck(Path=javaPath, Type="f"):
                        Output.append(javaPath)
                        continue
                    for two in scandir(one.path):
                        javaPath = pathAdder(two.path, "bin", JavaExecutableFileName)
                        if dfCheck(Path=javaPath, Type="f"):
                            Output.append(javaPath)

    return Output


def getJavaInfo(Path: str | None) -> JavaInfo:
    """通过 Java 源文件获取 Java 版本"""
    Path = fixJavaPath(Path)
    JarPath = genJarFile("GetJavaInfo.jar")

    Return = run(args=[Path, "-jar", JarPath], capture_output=True)
    Logger.debug('Java from "%s" return: "%s"', Path, Return)
    DecodedReturn = Return.stdout.decode("utf-8")
    try:
        JavaInfos = ReMatchJavaInfos.match(DecodedReturn).groups()
    except AttributeError:
        raise MatchStringError(DecodedReturn)
    return {
        "Path": Path,
        "Arch": JavaInfos[0],
        "Version": versionFormater(JavaInfos[1]),
        "From": JavaInfos[2],
    }


def fixJavaPath(Path: str) -> str:
    """修正路径"""
    if Path is None:
        Path = str()
    match OriginalSystem:
        case "Windows":
            if Path[-4] == "java":
                Path = Path[:-4] + "java.exe"
        case "Linux":
            if Path[-8:] == "java.exe":
                Path = Path[:-8] + "java"
        case _:
            UnsupportSystemHost(OriginalSystem)
    return Path


def versionFormater(Version: str) -> list:
    """格式化 Java 的版本号"""
    Version: list[str] = Version.replace(".", " ").split()
    if Version[0] == "1":
        Version[0] = Version[1]
        Version[1] = "0"
    if Version[-1][:2] == "0_":
        Version[-1] = Version[-1][2:]
    for i in range(len(Version)):
        Version[i] = fixType(Version[i])
    return Version


def getJavaInfoList(PathList: list[str] | None = None) -> list[JavaInfo]:
    """
    通过版本列表获取字典形式的 Java 信息, 如输入为空则通过 Claset.Utils.JavaHelper.getJavaPath() 获取\n
    如获取过程中出现 JavaHelper.MatchStringError 将忽略此版本
    """
    if PathList is None:
        PathList: list[str] = getJavaPath()
    Outputs: list[JavaInfo] = list()
    for Path in PathList:
        try:
            JavaInfos = getJavaInfo(Path)
        except MatchStringError:
            continue
        Outputs.append(JavaInfos)
    return Outputs


def autoPickJava(
    recommendVersion: int, JavaInfoList: list[JavaInfo] | None = None
) -> JavaInfo:
    """自动选择 Java"""
    # 如 JavaInfoList 为空则通过 getJavaInfoList() 获取
    if JavaInfoList is None:
        JavaInfoList = getJavaInfoList()

    # 如 JavaInfoList 为中单位数量为零则抛出 JavaNotFound 异常
    if len(JavaInfoList) == 0:
        raise JavaNotFound
    elif len(JavaInfoList) == 1:
        return JavaInfoList[0]

    for i in JavaInfoList:
        if i["Version"][0] == recommendVersion:
            return i

    if recommendVersion <= 16 and recommendVersion >= 8:
        for i in JavaInfoList:  # 优先使用 LTS 版本
            if i["Version"][0] in [8, 11, 17]:
                return i
        for i in JavaInfoList:
            if i["Version"][0] <= 16 and i["Version"][0] >= 8:
                return i
    elif recommendVersion >= 17:
        for i in JavaInfoList:
            if i["Version"][0] == 17:
                return i
        for i in JavaInfoList:
            if i["Version"][0] >= 17:
                return i

    return JavaInfoList[0]


def genJarFile(FileName: str, Overwrite: bool = False) -> str:
    """生成 Jar 文件至缓存文件夹"""
    FullPath = pathAdder("$JARS", FileName)

    # 如 Overwrite 为 False 且文件存在则提前返回
    if (Overwrite == False) and dfCheck(Path=FullPath, Type="f"):
        return FullPath

    match FileName:
        case "GetJavaInfo.jar":
            FileContent = (
                b"(\xb5/\xfd`\xb9\x02%\x17\x00D*PK\x03\x04\x14\x00\x08\x08\x08\x00&\xbb\x86S\x00\t\x00\x04\x00META-INF/\xfe\xca\x00\x00\x03\x00PK\x07\x08\x02\x14\x00\x00MANIFEST.MF\xf3M\xcc\xcbLK-.\xd1\rK-*\xce\xcc\xcf\xb3R0\xd43\xe0\xe5\xf2M\xcc\xcc\xd3u\xceI,.\xb6RpO-\xf1J,K\xf4\xccK\xcb\xe7\xe5r.JM,IM\xd1u\xaa\x04\xaa4\xd73\xd03T\xd0pM\xce\xc9,(NUpL\xc9/(\xc9,\xcd\xd5\xe4\xe5\xe2\xe5\x02\xb1\xa2c\xd1ZY\x1b\x11GetJavaInfo.class\x8dR]O\x13A\x14=\x97-\xecv\xd9B-\x9f~\xa0R\x15\xb7(\xad\x82_I\xc5\x07%\x12L\xa3$5$\xc6\xa7m;\xd4!\xedN3\x9d\x92\xf0\x1b\xfc5\xfaP\x8c$\xfe\x00\x7f\x94\xf1\xce\xda\xc4U\x1a\xe3<\xdc;s\xce\xb9'g&\xf3\xfd\xc7\xd7o\x00\xb6\xf0\xc4\xc7\x04\x1c\x17\x99\x00\x93\x98\"\xe4\x8f\xa2\xe3\xa8\xd2\x89\xe2v\xe5M\xe3H4\ra\xea\xa9\x8c\xa5yFp\xc2\xd2A\x16\x1e\xb2.\xfc\x00\xd3\x08\xfe\x90\xd7O\xfaFtY\xa5\x06<\xb4PK\x18\xa9*\xfbZ\xc6\xa6n\xb4\x88\xbaU\x173\x84\xa5\xd4\x8ca\xb2\xfd|"
                b' ;-\xa1}\xe4\xe0x\xb8@\xc8\xaa~9\xd2\xcd\x0f\xdbE\x8b\xcd\x05\x98\xc7\x02\xe7\x88z=\x11\xb7\x08\x1ba\xedo\x8bj\xe9\x1c4r\xadzX"\xb8#G\x9f\xe3_\x0cp\t\x97\t\xd3ma\xf6\xb5\xea\tmN\x08k\xffe\xcan+\x04Jr]\x0bp\x1d\xab\x04\xcf\xa8_$a>\x1c3\xe2\xe3\x06n\xba\xb8\x15`\r\xb7\tsc\x1e\x86\x03\xf6\xec\xa9\x13\xf3\xcb\x8d\x0br\xe0\xa1D\x98\xb1D\xf9X\xe8\xbeT\xf1v\xd1\xc3\x1dB\x90\xc6<l\x10r#$n)mE\x15\xbej\nrq\x9f\x81]a^1\xb6\x17\x1f*B\xe6\x85j\t\xc2lM\xc6\xe2\xf5\xa0\xdb\x10\xfam\xd4\xe80\x92\xe9F\x92#-\x86\xef\xc7e"\xf8u5\xd0M\xf1RZq>\xe5Y\xb6r\xac\xe2\x1e\xff.\xbb&@\xf6\x7fq\xdd\xe4\xd3\nw\xe2>\xb9~\n\xfa\xc4\x1b\xe2\x9f\x88\x84\xb6\xfb,\x1e\xe0\xe1H\xfa\x11N\x82\xb6?\xc3=C\xee\xdd)f\x0b\xf9!\n\x85\xc5/X\xb6\xfd\n\x97!\xae\x0eQL)B\xcb\xac\xffKq\xd72\xe5s\x8a\xdfa\n\xc8puP\xe4\xbe\xc3\xd9\x0f\x93x\x8f\x92\xbb<\xfe\tPK\x07\x08Ql*\x9d\xcf\x01\x00\x00?\x03\x00\x00PK\x01\x02\x14\x00\x02\x14=\x1b\x11\xd9PK\x05\x06\x03\x00\x03\x00\xbc\x00\x00\x00\xe7\x02\x00\x00\x00\x00\x18'
                b" \xc0D\x02)\xa2\xf0\x0b\xc8\xd3\xa7O\x1f\xcc\xc9\xd9\x01.\xe4\x0c\xdfk\xa6;\x04\xcd8\xf0y\xa0os\x00\x07\xd8i\\\xf6\xaf\x94'\xc0\xee\xe4q\rJ~\xbc\xc7\x9b\x03\xb5f\xa0\xb3~\x891\xaf\x03"
            )
        case _:
            raise ValueError(FileName)

    dfCheck(Path=FullPath, Type="fm")
    saveFile(Path=FullPath, FileContent=decompress(FileContent), Type="bytes")
    return FullPath
