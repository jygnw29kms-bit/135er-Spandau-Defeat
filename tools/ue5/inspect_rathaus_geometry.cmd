@echo off
setlocal
set "PROJECT=C:\Users\anony\Documents\SpandauStrike\repo\ue5\SpandauStrike"
set "SPANDAU_VALIDATION_MAP=/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v77_GAMEPLAY_ROADS_V85_QA"
set "SPANDAU_GEOMETRY_REPORT=%PROJECT%\Saved\Reports\rathaus_geometry_v77.json"
"C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "%PROJECT%\SpandauStrike.uproject" -run=pythonscript -script="%PROJECT%\Content\Python\inspect_rathaus_geometry.py" -unattended -nop4 -nosplash -nullrhi -abslog="%PROJECT%\Saved\Logs\SpandauStrike_geometry_v77.log"
exit /b %errorlevel%
