param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)
$ErrorActionPreference='Stop'
$repo=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$projectRoot=Join-Path $repo 'ue5\SpandauStrike'
$uproject=Join-Path $projectRoot 'SpandauStrike.uproject'
$cmd=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$builder=Join-Path $projectRoot 'Content\Python\build_rathaus_v73_capture_prototype.py'
$validator=Join-Path $projectRoot 'Content\Python\validate_rathaus_v73_capture_prototype.py'
foreach($p in @($uproject,$cmd,$builder,$validator)){ if(!(Test-Path $p)){ throw "Missing prerequisite: $p" } }
if(Get-Process UnrealEditor -ErrorAction SilentlyContinue){ throw 'Close UnrealEditor before isolated v73 map build.' }
$b=Start-Process -FilePath $cmd -ArgumentList @($uproject,'-run=pythonscript',('-script='+$builder),'-unattended','-nop4','-nosplash','-nullrhi') -PassThru -Wait
if($b.ExitCode -ne 0){ throw "v73 builder failed with exit code $($b.ExitCode)" }
$v=Start-Process -FilePath $cmd -ArgumentList @($uproject,'-run=pythonscript',('-script='+$validator),'-unattended','-nop4','-nosplash','-nullrhi') -PassThru -Wait
if($v.ExitCode -ne 0){ throw "v73 validator failed with exit code $($v.ExitCode)" }
Write-Host 'V73_CAPTURE_BUILD_AND_VALIDATE_OK'
