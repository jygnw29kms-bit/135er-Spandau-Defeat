@echo off
"C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "C:\Users\anony\Documents\SpandauStrike\repo\ue5\SpandauStrike\SpandauStrike.uproject" -run=pythonscript -script="C:\Users\anony\Documents\SpandauStrike\repo\ue5\SpandauStrike\Content\Python\inspect_rathaus_render_flags.py" -unattended -nop4 -nosplash -nullrhi
exit /b %errorlevel%
