# -*- coding: utf-8 -*-


LastVersion = 4


File = {
    "VERSION": 4,
    "Prefixs": {
        "PREFIX": "$PREFIX",
        "LOG": "$EXEC/Logs",
        "EXEC": "$PREFIX/Claset",
        "CACHE": "$EXEC/Cache",
        "CONFIG": "$EXEC",
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
    "3->4": [
        "REPLACE:VERSION->4",
        "REPLACE:[Prefixs, CACHE]->$EXEC/Cache",
        "REPLACE:[Prefixs, CONFIG]->$EXEC"
        "REPLACE:[Prefixs, LOG]->$EXEC/Logs"
    ],
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
