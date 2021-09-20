#VERSION=1
#
#From Claset/Base/Configs.py
#Claset/Base/Exceptions/Configs.py
#

# 配置文件错误主类
class ConfigsErrors(Exception): pass

# 配置文件未注册
class ConfigsUnregistered(ConfigsErrors): pass

# 配置文件已存在
class ConfigsExist(ConfigsErrors, FileExistsError): pass
    