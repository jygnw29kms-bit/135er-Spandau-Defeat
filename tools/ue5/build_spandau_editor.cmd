@echo off
"C:\Program Files\Epic Games\UE_5.8\Engine\Build\BatchFiles\Build.bat" LyraEditor Win64 Development "C:\Users\anony\Documents\SpandauStrike\repo\ue5\SpandauStrike\SpandauStrike.uproject" -WaitMutex -FromMsBuild
exit /b %errorlevel%
