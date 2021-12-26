# -*- coding: utf-8 -*-

from typing import Any

def getValueFromDict(Keys: list, Dict: dict) -> Any:
    if len(Keys) == 1:
        return(Dict[Keys[0]])
    else:
        return(getValueFromDict(Keys=Keys[1:], Dict=Dict[Keys[0]]))

