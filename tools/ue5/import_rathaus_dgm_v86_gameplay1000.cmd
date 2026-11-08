@echo off
set "PROJECT=C:\Users\anony\Documents\SpandauStrike\repo\ue5\SpandauStrike"
"C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "%PROJECT%\SpandauStrike.uproject" -run=pythonscript -script="%PROJECT%\Content\Python\import_rathaus_dgm_v86_gameplay1000.py" -unattended -nop4 -nosplash -nullrhi -abslog="%PROJECT%\Saved\Logs\SpandauStrike_import_dgm_v86.log"
exit /b %errorlevel%
