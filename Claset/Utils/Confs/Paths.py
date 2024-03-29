# -*- coding: utf-8 -*-


LastVersion = 7


File = {
    "Prefixs": {
        "PREFIX": "$PREFIX",
        "LOG": "$EXEC/Logs",
        "EXEC": "$PREFIX/Claset",
        "CACHE": "$EXEC/Cache",
        "CONFIG": "$EXEC",
        "JARS": "$CACHE/Jars",
        "MINECRFT": "$PREFIX/.minecraft",
        "ASSETS": "$MINECRFT/assets",
        "VERSION": "$MINECRFT/versions",
        "LIBRERIES": "$MINECRFT/libraries",
    },
    "Others": [],
}


Difference = {
    "6->7": [
        "DELETE:[Prefixs, MCVersion]",
        "DELETE:[Prefixs, MCAssetIndex]",
        "DELETE:[Prefixs, MCVersionManifest]",
    ],
    "5->6": ["REPLACE:[Prefixs, JARS]->$CACHE/Jars"],
    "4->5": ["REPLACE:[Prefixs, VERSION]->$MINECRFT/versions"],
    "3->4": [
        "REPLACE:[Prefixs, CACHE]->$EXEC/Cache",
        "REPLACE:[Prefixs, CONFIG]->$EXECREPLACE:[Prefixs, LOG]->$EXEC/Logs",
    ],
    "2->3": [
        "REPLACE:[Prefixs, ASSETS]->$MINECRFT/assets",
        "REPLACE:[Prefixs, VERSION]->$MINECRFT/version",
        "REPLACE:[Prefixs, LIBRERIES]->$MINECRFT/libraries",
        "REPLACE:[Prefixs, MCAssetIndex]->$ASSETS/indexes",
    ],
    "1->2": ["REPLACE:[Prefixs, CONFIG]->$PREFIX/Claset"],
}
