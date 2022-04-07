# -*- coding: utf-8 -*-


LastVersion = 3


File = {
    "UseGlobalConfig": True,
    "Global": {
        "MemoryMin": None,
        "MemoryMax": None,
        "WindowWidth": None,
        "WindowHeight": None,
        "JavaPath": None,
        "NotCheckGame": None,
        "NotCheckJvm": None,
        "WindowsPriority": None
    },
    "UnableGlobal": {
        "VersionIndependent": False,
        "PrefixAndSuffix": {
            "JvmPrefix": [],
            "JvmSuffix": [],
            "GamePrefix": [],
            "GameSuffix": []
        }
    }
}


Difference = {
    "2->3": [
        "REPLACE:[UnableGlobal, VersionIndependent]->False",
        "RENAME:[UnableGlobal, PrefixAndEnds]->PrefixAndSuffix",
        "RENAME:[UnableGlobal, PrefixAndSuffix, JvmEnd]->JvmSuffix",
        "RENAME:[UnableGlobal, PrefixAndSuffix, GameEnd]->GameSuffix"
    ],
    "1->2": [
        "REPLACE:[Global, WindowsPriority]->NORMAL",
        "DELETE:[UnableGlobal, NativesDir]"
    ]
}

