#! /usr/bin/pwsh

Get-ChildItem * -Include __pycache__ -Recurse | Remove-Item -Recurse
