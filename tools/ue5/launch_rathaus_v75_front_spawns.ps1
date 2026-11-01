param([string]$EngineRoot='C:\Program Files\Epic Games\UE_5.8',[int]$NumBots=15,[string]$MapPath='')
$ErrorActionPreference='Stop'
$repo=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$uproject=Join-Path $repo 'ue5\SpandauStrike\SpandauStrike.uproject'
$editor=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
if(-not $MapPath){ $MapPath=(Get-Content (Join-Path $PSScriptRoot 'rathaus_validation_target.json') -Raw | ConvertFrom-Json).map_path }
$url="${MapPath}?Experience=B_ShooterGame_Elimination?NumBots=$NumBots"
Start-Process -FilePath $editor -ArgumentList @($uproject,$url,'-game','-windowed','-ResX=1600','-ResY=900','-log','-nop4')
Write-Host "Started Rathaus map=$MapPath with $NumBots bots."

