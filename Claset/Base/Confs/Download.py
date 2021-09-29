# VERSION=2
#
# Claset/Base/Configs/Download.py
#


LastVersion = 2


File = {
    "VERSION": 2,
    "MaxThread": 32,
    "SleepTime": 0.1,
    "Retry": 5,
    "UseGobalRequestsSession": True,
    "UseSystemProxy": True,
    "ReadFileNameReString": "([a-zA-Z0-9_.-]*)$",
    "Headers": {
        "user-agent": "Claset/0.1.5"
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
    "1->2": [
        "REPLACE:VERSION->2",
        "REPLACE:UseSystemProxy->True",
        "REPLACE:[Proxies, http]->Null",
        "REPLACE:[Proxies, https]->Null",
        "REPLACE:[Headers, user-agent]->Claset/0.1.5"
    ]
}
