# -*- coding: utf-8 -*-


LastVersion = 5


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
        "WindowsPriority": None,
    },
    "UnableGlobal": {
        "InstanceType": "Client",
        "NativesDir": "AUTOSET",
        "VersionIndependent": False,
        "PrefixAndSuffix": {
            "JvmPrefix": [],
            "JvmSuffix": [],
            "ExecPrefix": [],
            "ExecSuffix": [],
        },
    },
}


Difference = {
    "4->5": [
        "REPLACE:[UnableGlobal, InstanceType]->Client",
        "RENAME:[UnableGlobal, PrefixAndSuffix, GamePrefix]->ExecPrefix",
        "RENAME:[UnableGlobal, PrefixAndSuffix, GameSuffix]->ExecSuffix",
    ],
    "3->4": ["REPLACE:[UnableGlobal, NativesDir]->AUTOSET"],
    "2->3": [
        "REPLACE:[UnableGlobal, VersionIndependent]->False",
        "RENAME:[UnableGlobal, PrefixAndEnds]->PrefixAndSuffix",
        "RENAME:[UnableGlobal, PrefixAndSuffix, JvmEnd]->JvmSuffix",
        "RENAME:[UnableGlobal, PrefixAndSuffix, GameEnd]->GameSuffix",
    ],
    "1->2": [
        "REPLACE:[Global, WindowsPriority]->NORMAL",
        "DELETE:[UnableGlobal, NativesDir]",
    ],
}
