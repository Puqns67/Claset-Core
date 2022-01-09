# -*- coding: utf-8 -*-

class AccountErrors(Exception):
    """账户管理错误主类"""

class AccountNotFound(AccountErrors):
    """账户未找到"""

class AccountDuplicate(AccountErrors):
    """账户重复"""

class UnsupportedAccountType(AccountErrors):
    """不支持的账户类型"""

