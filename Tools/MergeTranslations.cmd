xgettext ..\Claset\Execution\CommandLine\Main.py --keyword=python --output=..\Translations\new.pot
msgmerge ..\Translations\template.pot ..\Translations\new.pot --output=..\Translations\template.pot
msgmerge ..\Translations\zh_CN.po ..\Translations\template.pot --output=..\Translations\zh_CN.po
del ..\Translations\new.pot