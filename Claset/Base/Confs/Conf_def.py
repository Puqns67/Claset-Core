#VERSION=0
#
#Claset/Base/Configs/Conf_def.py
#Conf 默认格式
#

def getLastVersion() -> int:
    return int()

def getFile() -> dict:
    return {"FileContent": "FileContent"}

def getDifference() -> dict:
    # Differences Formart:
    #   NEW:KEY
    #   DEL:KEY
    #   CHANGEKEY:OLDKEY->NEWKEY
    #   CHANGEVALUE:OLDVALUE->NEWVALUE
    # Types: NEW, DEL, CHANGEKEY, CHANGEVALUE

    return {"Version_1": ["Difference1", "Difference2", "..."], "Version_2": ["Differences"], "...": "..."}
