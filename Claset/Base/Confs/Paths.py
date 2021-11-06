# -*- coding: utf-8 -*-


LastVersion = 3


File = {
    "VERSION": 3,
    "Prefixs": {
        "PREFIX": "$PREFIX",
        "EXEC": "$PREFIX/Claset",
        "CACHE": "$PREFIX/Claset/Cache",
        "CONFIG": "$PREFIX/Claset",
        "MINECRFT": "$PREFIX/.minecraft",
        "ASSETS": "$MINECRFT/assets",
        "VERSION": "$MINECRFT/version",
        "LIBRERIES": "$MINECRFT/libraries",
        "MCVersion": "$CACHE/MCVersionJson",
        "MCAssetIndex": "$ASSETS/indexes",
        "MCVersionManifest": "$CACHE"
    },
    "Others": []
}


Difference = {
    "2->3": [
        "REPLACE:VERSION->3",
        "REPLACE:[Prefixs, ASSETS]->$MINECRFT/assets",
        "REPLACE:[Prefixs, VERSION]->$MINECRFT/version",
        "REPLACE:[Prefixs, LIBRERIES]->$MINECRFT/libraries",
        "REPLACE:[Prefixs, MCAssetIndex]->$ASSETS/indexes"
    ],
    "1->2": [
        "REPLACE:VERSION->2",
        "REPLACE:[Prefixs, CONFIG]->$PREFIX/Claset"
    ]
}
