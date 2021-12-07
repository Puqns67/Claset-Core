# -*- coding: utf-8 -*-


LastVersion = 2


File = {
    "FilePath": "$LOG/",
    "LoggingLevel": "DEBUG",
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
                "ArchiveFileName": "Claset-Log-Archive",
                "TempDirName": "ArchivedLog"
            }
        }
    }
}


Difference = {
    "1->2": [
        "REPLACE:[ProcessOldLog, TypeSettings, Archive, ArchiveFileName]->Claset-Log-Archive",
        "REPLACE:[ProcessOldLog, TypeSettings, Archive, TempDirName]->ArchivedLog",
        "REPLACE:LoggingLevel->DEBUG"
    ]
}
