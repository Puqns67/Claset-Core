New-Item -Path "Translations/zh_CN/LC_MESSAGES" -ItemType Directory
msgfmt Translations/zh_CN.po --output=Translations/zh_CN/LC_MESSAGES/Default.mo
