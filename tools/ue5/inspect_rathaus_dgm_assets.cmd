@echo off
set "PROJECT=C:\Users\anony\Documents\SpandauStrike\repo\ue5\SpandauStrike"
"C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "%PROJECT%\SpandauStrike.uproject" -run=pythonscript -script="%PROJECT%\Content\Python\inspect_rathaus_dgm_v83_asset.py" -unattended -nop4 -nosplash -nullrhi -abslog="%PROJECT%\Saved\Logs\SpandauStrike_dgm_assets.log"
exit /b %errorlevel%
