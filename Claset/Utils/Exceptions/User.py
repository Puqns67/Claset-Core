# -*- coding: utf-8 -*-

class UserErrors(Exception):
    """用户管理错误主类"""

class UserNotFound(UserErrors):
    """用户未找到"""

class UserDuplicate(UserErrors):
    """用户重复"""

