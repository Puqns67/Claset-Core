# -*- coding: utf-8 -*-

CLASET_CLIENT_ID = "baadb158-b1d7-424d-b2cd-a5957c70348a"
CLASET_SCOPE = "XboxLive.signin offline_access"

# Microsoft API
MICROSOFT_TENANT = "consumers"
MICROSOFT_DEVICE_CODE_URL = f"https://login.microsoftonline.com/{MICROSOFT_TENANT}/oauth2/v2.0/devicecode"
MICROSOFT_TOKEN_URL = f"https://login.microsoftonline.com/{MICROSOFT_TENANT}/oauth2/v2.0/token"

# XBox API
XBOX_LIVE_AUTH_URL = "https://user.auth.xboxlive.com/user/authenticate"
XBOX_XSTS_AUTH_URL = "https://xsts.auth.xboxlive.com/xsts/authorize"

# Mojang API
MOJANG_AUTH_SERVICES_URL = "https://api.minecraftservices.com/authentication/login_with_xbox"
MOJANG_PROFILE_URL = "https://api.minecraftservices.com/minecraft/profile"

