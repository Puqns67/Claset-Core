# -*- coding: utf-8 -*-
"""Conf 默认格式"""


LastVersion = int()


File = {"FileContent": "FileContent"}

# Differences Formart:
#   REPLACE:KEYS->VALUE
#   DELETE:KEYS->NULL
#   [WIP]RENAMEKEY:OLDKEYS->NEWKEYNAME
#   [WIP]REMOVEKEY:OLDKEYS->NEWKEYS
# Types: NEW, DEL, RENAMEKEY, REMOVEKEY
Difference = {"Version_1": ["Difference1", "Difference2", "..."], "Version_2": ["Differences"], "...": "..."}

