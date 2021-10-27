#VERSION=1
#
#From Claset/Game/LoadJson.py
#Claset/Game/Exceptions/LoadJson.py
#

# 解析游戏 Json 错误主类
class LoadGameJsonErrors(Exception): pass

# Features 中缺少对应的键
class FeaturesMissingKey(LoadGameJsonErrors): pass

# 不支持的系统类型
class UnsupportSystemHost(LoadGameJsonErrors): pass