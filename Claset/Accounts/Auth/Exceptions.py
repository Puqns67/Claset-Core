# -*- coding: utf-8 -*-

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

