# -*- coding: utf-8 -*-


LastVersion = 3


File = {
    "MaxThread": 32,
    "SleepTime": 0.1,
    "Retry": 5,
    "UseGobalRequestsSession": True,
    "UseSystemProxy": True,
    "Headers": {
        "user-agent": "Claset/0.2.0"
    },
    "Timeouts": {
        "Connect": 5,
        "Read": 30
    },
    "Proxies": {
        "http": None,
        "https": None
    }
}


Difference = {
    "2->3": [
        "DELETE:ReadFileNameReString",
        "REPLACE:[Headers, user-agent]->Claset/0.2.0"
    ],
    "1->2": [
        "REPLACE:UseSystemProxy->True",
        "REPLACE:[Proxies, http]->Null",
        "REPLACE:[Proxies, https]->Null",
        "REPLACE:[Headers, user-agent]->Claset/0.1.5"
    ]
}
