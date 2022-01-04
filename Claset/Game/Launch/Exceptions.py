# -*- coding: utf-8 -*-

class LauncherError(Exception):
    """启动器错误主类"""

class VersionNotFound(LauncherError):
    """版本不存在"""

class UnsupportComplianceLevel(LauncherError):
    """不支持的 ComplianceLevel"""

class LauncherVersionError(LauncherError):
    """此版本所要求的启动器版本不被本启动器所满足"""

