#VERSION=2
#
#Claset/Base/Configs/Download.py
#

def getLastVersion() -> int:
    return 2

def getFile() -> dict:
    return {
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
            "http": "",
            "https": ""
        }
    }


def getDifference() -> dict:
    return {
        "1->2": [
            "NEW:UseSystemProxy->True",
            "NEW:[Proxies, http]->",
            "NEW:['Proxies, https]->"
            "CHANGEVALUE:[Headers, user-agent]->Claset/0.1.5"
        ]
    }
