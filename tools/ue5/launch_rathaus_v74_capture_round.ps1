param(
    [string]$EngineRoot='C:\Program Files\Epic Games\UE_5.8',
    [int]$NumBots=15
)
$ErrorActionPreference='Stop'
$repo=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$uproject=Join-Path $repo 'ue5\SpandauStrike\SpandauStrike.uproject'
$editor=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$url="/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v74_CAPTURE_ROUND?Experience=B_ShooterGame_Elimination?NumBots=$NumBots"
foreach($p in @($uproject,$editor)){ if(!(Test-Path $p)){ throw "Missing prerequisite: $p" } }
Start-Process -FilePath $editor -ArgumentList @($uproject,$url,'-game','-windowed','-ResX=1600','-ResY=900','-log','-nop4')
Write-Host "Started Rathaus v74 Capture Round with $NumBots bots."
