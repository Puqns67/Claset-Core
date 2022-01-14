# -*- coding: utf-8 -*-


LastVersion = 5


File = {
    "MaxThread": 32,
    "SleepTime": 0.1,
    "Retry": 5,
    "UseGobalRequestsSession": True,
    "UseSystemProxy": True,
    "ProxyLink": None,
    "ErrorByStatusCode": True,
    "SSLVerify": True,
    "Headers": {
        "user-agent": "Claset/0.2.1"
    },
    "Timeouts": {
        "Connect": 5,
        "Read": 30
    }
}


Difference = {
    "4->5": [
        "DELETE:Proxies",
        "REPLACE:ProxyLink->Null",
        "REPLACE:ErrorByStatusCode->True",
        "REPLACE:SSLVerify->True"
    ],
    "3->4": [
        "REPLACE:[Headers, user-agent]->Claset/0.2.1"
    ],
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
