# -*- coding: utf-8 -*-

class AccountErrors(Exception):
    """账户管理错误主类"""

class AccountNotFound(AccountErrors):
    """账户未找到"""

class AccountDuplicate(AccountErrors):
    """账户重复"""

class UnsupportedAccountType(AccountErrors):
    """不支持的账户类型"""

class NoAccountsFound(AccountErrors):
    """未找到任何账户"""

class AuthError(Exception):
    """登录错误主类"""

class AuthDeclined(AuthError):
    """账户取消登录"""

class MicrosoftOAuthError(AuthError):
    """微软账户登录错误主类"""

class MicrosoftOAuthDeclined(MicrosoftOAuthError, AuthError):
    """微软账户登录过程中取消登录"""

class MicrosoftOAuthTimeOut(MicrosoftOAuthError):
    """微软账户登录过程中超时"""

