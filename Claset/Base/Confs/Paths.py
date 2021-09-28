# VERSION=2
#
# Claset/Base/Configs/Paths.py
#


LastVersion = 2


File = {
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


Difference = {
    "1->2": [
        "CHANGEVALUE:[Perfixs, CONFIG]->$PREFIX/Claset"
    ]
}
