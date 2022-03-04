# -*- coding: utf-8 -*-


LastVersion = 2


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
        "PrefixAndEnds": {
            "JvmPrefix": [],
            "JvmEnd": [],
            "GamePrefix": [],
            "GameEnd": []
        }
    }
}


Difference = {
    "1->2": [
        "REPLACE:[Global, WindowsPriority]->NORMAL",
        "DELETE:[UnableGlobal, NativesDir]"
    ]
}

