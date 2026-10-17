param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8',
    [int]$NumBots = 15
)
$ErrorActionPreference='Stop'
$repo=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$uproject=Join-Path $repo 'ue5\SpandauStrike\SpandauStrike.uproject'
$editor=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
if(!(Test-Path $editor)){ throw "UnrealEditor.exe not found: $editor" }
if(!(Test-Path $uproject)){ throw "SpandauStrike.uproject not found: $uproject" }
$url="/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v73_CAPTURE_PROTO?Experience=B_ShooterGame_Elimination?NumBots=$NumBots"
Start-Process -FilePath $editor -ArgumentList @($uproject,$url,'-game','-d3d11','-windowed','-ResX=1600','-ResY=900','-log','-nop4')
