@echo off
set "PROJECT=C:\Users\anony\Documents\SpandauStrike\repo\ue5\SpandauStrike"
set "SCRIPT=C:\Users\anony\Documents\SpandauStrike\repo\tools\blender_pipeline\build_rathaus_dgm_master.py"
"C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "%PROJECT%\SpandauStrike.uproject" -run=pythonscript -script="%SCRIPT%" -unattended -nop4 -nosplash -nullrhi -abslog="%PROJECT%\Saved\Logs\SpandauStrike_build_dgm1000.log"
exit /b %errorlevel%
