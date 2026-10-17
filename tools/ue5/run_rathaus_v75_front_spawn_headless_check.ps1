param(
    [string]$EngineRoot='C:\Program Files\Epic Games\UE_5.8',
    [int]$StartupTimeoutSeconds=120,
    [int]$RuntimeSeconds=45,
    [int]$NumBots=15
)
$ErrorActionPreference='Stop'
$repo=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$projectRoot=Join-Path $repo 'ue5\SpandauStrike'
$uproject=Join-Path $projectRoot 'SpandauStrike.uproject'
$editor=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$cmd=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$validator=Join-Path $projectRoot 'Content\Python\validate_rathaus_v75_front_spawns.py'
$reportDir=Join-Path $projectRoot 'Saved\Reports'
$report=Join-Path $reportDir 'v75_front_spawn_headless_workflow.json'
$log=Join-Path $projectRoot 'Saved\Logs\SpandauStrike.log'
$url="/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v75_FRONTSPAWNS?Experience=B_ShooterGame_Elimination?NumBots=$NumBots"
$bad='FellOutOfWorld|KillZ|WorldBounds|Accessed None|Failed to spawn|SpawnActor failed|Fatal error|Unhandled Exception'
$result=[ordered]@{timestamp=(Get-Date).ToString('o');map=$url;static_validation=$false;startup_ready=$false;front_spawn_seen=$false;bad_count=-1;passed=$false}
$editorProcess=$null
try {
    $v=Start-Process -FilePath $cmd -ArgumentList @($uproject,'-run=pythonscript',('-script='+$validator),'-unattended','-nop4','-nosplash','-nullrhi') -PassThru -Wait
    if($v.ExitCode -ne 0){throw "v75 validator failed: $($v.ExitCode)"}
    $result.static_validation=$true
    if(Test-Path $log){Remove-Item $log -Force}
    $editorProcess=Start-Process -FilePath $editor -ArgumentList @($uproject,$url,'-game','-nullrhi','-nosound','-unattended','-nop4','-log') -PassThru
    $deadline=(Get-Date).AddSeconds($StartupTimeoutSeconds)
    do {
        Start-Sleep 1
        if($editorProcess.HasExited){throw "Unreal exited during startup: $($editorProcess.ExitCode)"}
        if(Test-Path $log){$txt=Get-Content $log -Raw; $result.startup_ready=($txt -match 'SpandauCaptureDirector teams resolved' -and $txt -match 'Spandau objective routing: sector=1 routed=15 failed=0')}
    } while(-not $result.startup_ready -and (Get-Date) -lt $deadline)
    if(-not $result.startup_ready){throw 'v75 runtime not ready'}
    $end=(Get-Date).AddSeconds($RuntimeSeconds)
    do { Start-Sleep 1; if($editorProcess.HasExited){break} } while((Get-Date) -lt $end)
    $txt=Get-Content $log -Raw
    $result.front_spawn_seen=($txt -match 'Spandau front spawn candidates:')
    $result.bad_count=[regex]::Matches($txt,$bad,[Text.RegularExpressions.RegexOptions]::IgnoreCase).Count
    $result.passed=($result.static_validation -and $result.startup_ready -and $result.bad_count -eq 0)
    if(-not $result.passed){throw 'v75 runtime gate failed'}
}
finally {
    if($editorProcess -and -not $editorProcess.HasExited){Stop-Process -Id $editorProcess.Id -Force -ErrorAction SilentlyContinue}
    $result | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 $report
}
Write-Host ('V75_FRONTSPAWN_HEADLESS='+($result|ConvertTo-Json -Compress))
