#VERSION=1
#
#Claset/Base/Configs/Download.py
#

def getLastVersion() -> int:
    return 1

def getFile() -> dict:
    return {
        "VERSION": 1,
        "MaxThread": 32,
        "SleepTime": 0.1,
        "Retry": 5,
        "UseGobalRequestsSession": True,
        "ReadFileNameReString": "([a-zA-Z0-9_.-]*)$",
        "Headers": {
            "user-agent": "Claset/0.1.4"
        },
        "Timeouts": {
            "Connect": 5,
            "Read": 30
        }
    }


def getDifference() -> dict:
    return {}
