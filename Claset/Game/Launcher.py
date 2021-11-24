# -*- coding: utf-8 -*-
"""游戏启动器"""


class GameLauncher():
    """游戏启动器"""
    def __init__(self, VersionName: str):
        self.VersionName = VersionName


    def Replaces(Key: str) -> str:
        """替换"""
        match Key:
            case "launcher_name": return("Claset")
            case "launcher_version": return("22")
            case "assetsDir": return("$ASSETS")
            case "assets_index_name": return("")
            case "auth_player_name": return("WIP")
            case "user_type": return("WIP")
            case "version_type": return("WIP")
            case "classpath": return("WIP")
            case "natives_directory": return("WIP")
            case "game_directory": return("WIP")
