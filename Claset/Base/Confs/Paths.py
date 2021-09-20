#VERSION=1
#
#Claset/Base/Configs/Paths.py
#

def getLastVersion() -> int:
    return 1

def getFile() -> dict:
    return {
        "VERSION": 1,
        "Prefixs": {
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
        },
        "Others": []
    }


def getDifference() -> dict:
    return {}
