# -*- coding: utf-8 -*-


LastVersion = 2


File = {
    "VERSION": 2,
    "ENABLE": True,
    "Format": {
        "Perfix": r"[{Name}]",
        "Value": r"{Value}",
        "Time": r"%Y/%m/%d_%H:%M:%S",
        "FullLog": r"[{Time}]{{Type}}{Perfixs}: {Text}"
    },
    "ProgressiveWrite": True,
    "Debug": True,
    "Types": [
        "INFO",
        "WARN",
        "DEBUG",
        "ERROR"
    ],
    "OldLogProcess": {
        "Type": "Archive",
        "Types": [
                "Delete",
                "Archive"
        ],
        "Settings": {
            "Delete": {
                "MaxKeepFile": 3
            },
            "Archive": {
                "MaxKeepFile": 3,
                "ArchiveFileName": "Claset-Log-Archive.tar"
            }
        }
    }
}


Difference = {
    "1->2": [
        "REPLACE:VERSION->2",
        "REPLACE:[Format, FullLog]->[{Time}]{{Type}}{Perfixs}: {Text}"
    ]
}
