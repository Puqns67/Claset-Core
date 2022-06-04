# -*- coding: utf-8 -*-

from gettext import GNUTranslations, NullTranslations, find as findMoFile
from os import environ
from sys import exec_prefix

import Claset


def simpleI18n(message: str) -> str:
    """默认 i18n 文字处理器"""
    return message


def getTargetLanguage(
    CurrentLanguage: str | None = None, ForceLanguage: str | list | None = None
) -> list[str]:
    if ForceLanguage is not None:
        TargetLanguage = ForceLanguage
    else:
        if Claset.Utils.OriginalSystem == "Windows":
            EnvironLanguage = None
            for i in (
                "LANGUAGE",
                "LC_ALL",
                "LC_MESSAGES",
                "LANG",
            ):
                EnvironLanguage = environ.get(i)
                if EnvironLanguage is not None:
                    EnvironLanguage = EnvironLanguage.split(";")
                    break
            TargetLanguage = CurrentLanguage or EnvironLanguage or "zh_CN.UTF-8"
        else:
            TargetLanguage = CurrentLanguage

    if isinstance(TargetLanguage, str):
        TargetLanguage = (TargetLanguage,)

    return TargetLanguage


def getI18nProcessor(TargetLanguage: list[str] | None = None) -> None:
    """获取多国语言支持"""
    if TargetLanguage is None:
        TargetLanguage = getTargetLanguage()

    MoFilePath = findMoFile(
        domain="Default",
        localedir=Claset.Utils.path(Input=f"{exec_prefix}/Translations", IsPath=True),
        languages=TargetLanguage,
    )

    # 若无法在可执行位置找到翻译文件目录则尝试在当前位置寻找
    if MoFilePath is None:
        MoFilePath = findMoFile(
            domain="Default",
            localedir=Claset.Utils.path(Input="$PREFIX/Translations", IsPath=True),
            languages=TargetLanguage,
        )

    if MoFilePath is None:
        TranslateObj = NullTranslations()
    else:
        with open(file=MoFilePath, mode="rb") as MoFile:
            TranslateObj = GNUTranslations(fp=MoFile)

    return TranslateObj.gettext
