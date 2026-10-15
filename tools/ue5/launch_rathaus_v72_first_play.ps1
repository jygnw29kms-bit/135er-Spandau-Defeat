param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)
$ErrorActionPreference='Stop'
$repo=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$uproject=Join-Path $repo 'ue5\SpandauStrike\SpandauStrike.uproject'
$editor=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
if(!(Test-Path $editor)){ throw "UnrealEditor.exe not found: $editor" }
if(!(Test-Path $uproject)){ throw "SpandauStrike.uproject not found: $uproject" }
$url='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v72_FIRST_PLAY?Experience=B_ShooterGame_Elimination'
Start-Process -FilePath $editor -ArgumentList @($uproject,$url,'-game','-windowed','-ResX=1600','-ResY=900','-log','-nop4')
