# -*- coding: utf-8 -*-


LastVersion = 6


File = {
    "DownloadServer": "Vanilla",
    "Language": None,
    "GlobalConfig": {
        "MemoryMin": 512,
        "MemoryMax": 1024,
        "WindowWidth": 854,
        "WindowHeight": 480,
        "JavaPath": "AUTOPICK",
        "NotCheckGame": False,
        "NotCheckJvm": False,
        "WindowsPriority": "NORMAL",
    },
}


Difference = {
    "5->6": ["REPLACE:Language->None"],
    "4->5": [
        "REPLACE:[GlobalConfig, WindowsPriority]->NORMAL",
    ],
    "3->4": ["REPLACE:[GlobalConfig, JavaPath]->AUTOPICK"],
    "2->3": [
        "REPLACE:[GlobalConfig, MemoryMin]->512",
        "REPLACE:[GlobalConfig, MemoryMax]->1024",
    ],
    "1->2": [
        "REPLACE:[GlobalConfig, WindowWidth]->845",
        "REPLACE:[GlobalConfig, WindowHeight]->480"
        "REPLACE:[GlobalConfig, JavaPath]->None",
        "REPLACE:[GlobalConfig, NotCheckGame]->False",
        "REPLACE:[GlobalConfig, NotCheckJvm]->False",
    ],
}
