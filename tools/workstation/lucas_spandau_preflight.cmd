@echo off
setlocal
set "REPO=C:\Users\anony\Documents\SpandauStrike\repo"
set "GIT=C:\Program Files\Git\cmd\git.exe"
set "BLENDER=C:\Users\anony\Apps\blender-4.5.10-windows-x64\blender.exe"
set "UE=C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe"
set "UPROJECT=%REPO%\ue5\SpandauStrike\SpandauStrike.uproject"
set "MASTER=%REPO%\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v51_PEDIMENT_READABILITY.blend"

for %%F in ("%GIT%" "%BLENDER%" "%UE%" "%UPROJECT%" "%MASTER%") do (
  if not exist "%%~F" (
    echo SPANDAU_PREFLIGHT=FAIL missing=%%~F
    exit /b 2
  )
)

cd /d "%REPO%" || exit /b 3
for /f %%H in ('"%GIT%" rev-parse --short HEAD') do set "HEAD=%%H"
for /f %%B in ('"%GIT%" branch --show-current') do set "BRANCH=%%B"
set "DIRTY=0"
"%GIT%" diff --quiet || set "DIRTY=1"
"%GIT%" diff --cached --quiet || set "DIRTY=1"
for /f "delims=" %%S in ('"%GIT%" ls-files --others --exclude-standard') do set "DIRTY=1"

echo SPANDAU_PREFLIGHT=OK
echo DEVICE=DESKTOP-SMN4ATU
echo REPO=%REPO%
echo BRANCH=%BRANCH%
echo HEAD=%HEAD%
echo DIRTY=%DIRTY%
echo BLENDER=%BLENDER%
echo UE=%UE%
exit /b 0
