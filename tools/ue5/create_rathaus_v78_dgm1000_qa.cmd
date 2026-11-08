@echo off
set "PROJECT=C:\Users\anony\Documents\SpandauStrike\repo\ue5\SpandauStrike"
"C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "%PROJECT%\SpandauStrike.uproject" -run=pythonscript -script="%PROJECT%\Content\Python\create_rathaus_v78_dgm1000_qa.py" -unattended -nop4 -nosplash -nullrhi -abslog="%PROJECT%\Saved\Logs\SpandauStrike_create_v78_dgm1000.log"
exit /b %errorlevel%
