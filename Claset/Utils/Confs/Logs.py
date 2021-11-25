# -*- coding: utf-8 -*-


LastVersion = 1


File = {
    "FilePath": "$LOG/",
    "LogFormats": {
        "Format": "[%(asctime)s][%(module)s][%(funcName)s][%(levelname)s]: %(message)s",
        "Date": "%Y/%m/%d|%H:%M:%S"
    },
    "Handlers": {
        "Stream": True,
        "File": True
    },
    "ProcessOldLog": {
        "Type": "Archive",
        "TypeSettings": {
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


Difference = {
}
