#VERSION=2
#
#Claset/Base/Configs/Paths.py
#

def getLastVersion() -> int:
    return 2

def getFile() -> dict:
    return {
        "VERSION": 2,
        "Prefixs": {
            "PREFIX": "$PREFIX",
            "EXEC": "$PREFIX/Claset",
            "CACHE": "$PREFIX/Claset/Cache",
            "CONFIG": "$PREFIX/Claset",
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
    return {
        "1->2": [
            "CHANGEVALUE:['Perfixs','CONFIG']->'$PREFIX/Claset'"
        ]
    }
