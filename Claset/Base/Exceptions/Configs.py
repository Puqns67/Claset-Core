# -*- coding: utf-8 -*-

# 配置文件错误主类
class ConfigsErrors(Exception): pass

# 配置文件未注册
class ConfigsUnregistered(ConfigsErrors): pass

# 配置文件已存在
class ConfigsExist(ConfigsErrors, FileExistsError): pass

# 不存在的差异类型
class UnknownDifferenceType(ConfigsErrors): pass