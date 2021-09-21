#VERSION=0
#
#Claset/Base/Configs/Settings.py
#

def getLastVersion() -> int:
    return 1


def getFile() -> dict:
    return {
        "VERSION": 1,
        "CheckUpdate": True,
        "DownloadServer": "Vanilla"
    }


def getDifference() -> dict:
    return {}
