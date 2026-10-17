param([string]$EngineRoot='C:\Program Files\Epic Games\UE_5.8',[int]$NumBots=15)
$ErrorActionPreference='Stop'
$repo=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$uproject=Join-Path $repo 'ue5\SpandauStrike\SpandauStrike.uproject'
$editor=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$url="/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v75_FRONTSPAWNS?Experience=B_ShooterGame_Elimination?NumBots=$NumBots"
Start-Process -FilePath $editor -ArgumentList @($uproject,$url,'-game','-windowed','-ResX=1600','-ResY=900','-log','-nop4')
Write-Host "Started Rathaus v75 Front Spawns with $NumBots bots."
