#VERSION=0
#
#Claset/Base/Configs/Logs.py
#

def getLastVersion() -> int:
    return 1


def getFile() -> dict:
    return {
        "VERSION": 1,
        "ENABLE": True,
        "Format": {
            "Perfix": r"[{Name}]",
            "Value": r"{Value}",
            "Time": r"%Y/%m/%d_%H:%M:%S",
            "FullLog": r"[{Time}]{{Type}}{Perfixs}: {Text}."
        },
        "ProgressiveWrite": True,
        "Debug": True,
        "Types": [
            "INFO",
            "WARN",
            "DEBUG",
            "ERROR"
        ],
        "OldLogProcess": {
            "Type": "Archive",
            "Types": [
                "Delete",
                "Archive"
            ],
            "Settings": {
                "Delete": {
                    "MaxKeepFile": 3
                },
                "Archive": {
                    "MaxKeepFile": 3,
                    "ArchiveFileName": "Claset-Log-Archive.tar"
                }
            }
        }
    }


def getDifference() -> dict:
    return {}
