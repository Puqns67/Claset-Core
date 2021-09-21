# VERSION=6
#
# Claset/Base/Path.py
# 地址转换
#

from json import load
from os import getcwd
from os.path import abspath


def path(input: str, DisableabsPath: bool = True) -> str:
    try:
        with open(getcwd() + "/Claset/Configs/Paths.json") as ConfigFile:
            Config = load(ConfigFile)["Prefixs"]
    except FileNotFoundError:
        Config = {
            "PREFIX": "$PREFIX",
            "EXEC": "$PREFIX/Claset",
            "CACHE": "$PREFIX/Claset/Cache",
            "CONFIG": "$PREFIX/Claset/Configs",
            "MINECRFT": "$PREFIX/.minecraft",
            "ASSETS": "$PREFIX/.minecraft/assets",
            "VERSION": "$PREFIX/.minecraft/version",
            "LIBRERIES": "$PREFIX/.minecraft/libraries",
            "MCVersion": "$CACHE/MCVersionJson",
            "MCAssetIndex": "$CACHE/MCAssetIndex",
            "MCVersionManifest": "$CACHE"
        }

    ConfigKeys = Config.keys()

    while "$" in input:
        for i in ConfigKeys:
            if "$PREFIX" in input:
                input = input.replace("$PREFIX", getcwd())
                break
            if i in input:
                input = input.replace("$" + i, Config[i])

    if DisableabsPath == False:
        input = abspath(input)

    return(input)
