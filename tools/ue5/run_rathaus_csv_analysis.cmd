@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d C:\Users\anony\Documents\SpandauStrike\repo
set "CSVROOT=C:\Users\anony\AppData\Local\UnrealEngine\5.8\Saved\Profiling\CSV"
set "LATEST="
for /f "delims=" %%F in ('dir /b /a-d /o-d "%CSVROOT%\Profile*.csv" 2^>nul') do if not defined LATEST set "LATEST=%CSVROOT%\%%F"
if not defined LATEST (
  echo ERROR: Kein UE CSV-Profil gefunden.
  exit /b 2
)
echo Analysiere: %LATEST%
node tools\ue5\analyze_rathaus_csv_profile.js "%LATEST%" --warmup 20 --measure 30 --out-dir ue5\SpandauStrike\Saved\Profiling\Reports
exit /b %errorlevel%
