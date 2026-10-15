@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_rathaus_v72_first_play_check.ps1" %*
exit /b %ERRORLEVEL%
