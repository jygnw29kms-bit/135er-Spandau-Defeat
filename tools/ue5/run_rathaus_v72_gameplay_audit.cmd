@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_rathaus_v72_gameplay_audit.ps1" %*
exit /b %ERRORLEVEL%
