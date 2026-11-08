@echo off
set "SPANDAU_INSPECT_MAP=/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v78_GAMEPLAY_DGM1000_QA"
"C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "C:\Users\anony\Documents\SpandauStrike\repo\ue5\SpandauStrike\SpandauStrike.uproject" -run=pythonscript -script="C:\Users\anony\Documents\SpandauStrike\repo\ue5\SpandauStrike\Content\Python\inspect_rathaus_visual_runtime.py" -unattended -nop4 -nosplash -nullrhi
exit /b %errorlevel%
