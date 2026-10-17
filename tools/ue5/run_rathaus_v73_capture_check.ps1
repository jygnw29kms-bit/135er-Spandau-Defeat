param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8',
    [int]$StartupTimeoutSeconds = 300,
    [int]$RuntimeSeconds = 60,
    [int]$NumBots = 15
)
$ErrorActionPreference='Stop'
$repo=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$projectRoot=Join-Path $repo 'ue5\SpandauStrike'
$uproject=Join-Path $projectRoot 'SpandauStrike.uproject'
$editor=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$cmd=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$validator=Join-Path $projectRoot 'Content\Python\validate_rathaus_v73_capture_prototype.py'
$reportDir=Join-Path $projectRoot 'Saved\Reports'
$report=Join-Path $reportDir 'v73_capture_workflow.json'
$log=Join-Path $projectRoot 'Saved\Logs\SpandauStrike.log'
$url="/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v73_CAPTURE_PROTO?Experience=B_ShooterGame_Elimination?NumBots=$NumBots"
$bad='FellOutOfWorld|KillZ|WorldBounds|Accessed None|Failed to spawn|SpawnActor failed|Fatal error|Unhandled Exception|B_AI_Controller_LyraShooter.*Error'
$good=@(
    'Load map complete /Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v73_CAPTURE_PROTO',
    'Identified experience LyraExperienceDefinition:B_ShooterGame_Elimination',
    'OnExperienceLoadComplete(CurrentExperience = LyraExperienceDefinition:B_ShooterGame_Elimination'
)
foreach($p in @($uproject,$editor,$cmd,$validator)){ if(!(Test-Path $p)){ throw "Missing prerequisite: $p" } }
if(Get-Process UnrealEditor -ErrorAction SilentlyContinue){ throw 'Preflight refused: UnrealEditor is already running. Close it before this isolated check.' }
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$result=[ordered]@{
    timestamp=(Get-Date).ToString('o'); map=$url; startup_timeout_seconds=$StartupTimeoutSeconds;
    runtime_seconds=$RuntimeSeconds; bots=$NumBots; static_validation=$false; runtime_started=$false;
    startup_ready=$false; experience_complete=$false; capture_class_seen=$false; bad_count=-1;
    passed=$false; editor_pid=$null
}
$editorProcess=$null
try {
    $v=Start-Process -FilePath $cmd -ArgumentList @($uproject,'-run=pythonscript',('-script='+$validator),'-unattended','-nop4','-nosplash','-nullrhi') -PassThru -Wait
    if($v.ExitCode -ne 0){ throw "Capture prototype validator failed with exit code $($v.ExitCode)" }
    $result.static_validation=$true
    if(Test-Path $log){ Remove-Item $log -Force }
    $editorProcess=Start-Process -FilePath $editor -ArgumentList @($uproject,$url,'-game','-d3d11','-windowed','-ResX=1280','-ResY=720','-unattended','-nop4','-log') -PassThru
    $result.editor_pid=$editorProcess.Id; $result.runtime_started=$true

    $startupDeadline=(Get-Date).AddSeconds($StartupTimeoutSeconds)
    do {
        Start-Sleep -Seconds 1
        if($editorProcess.HasExited){ throw "Unreal exited during startup with code $($editorProcess.ExitCode)" }
        if(Test-Path $log){
            $txt=Get-Content $log -Raw -ErrorAction SilentlyContinue
            $result.experience_complete=$txt.Contains($good[2])
            $result.capture_class_seen=($txt -match 'SpandauCaptureDirector runtime ready' -and $txt -match 'SpandauCapturePoint runtime ready')
            $mapReady=$txt.Contains($good[0])
            $result.startup_ready=($mapReady -and $result.experience_complete -and $result.capture_class_seen)
        }
    } while(-not $result.startup_ready -and (Get-Date) -lt $startupDeadline)

    if(-not $result.startup_ready){ throw 'Capture prototype did not reach runtime-ready state before startup timeout.' }
    $result.startup_ready_at=(Get-Date).ToString('o')

    $observationDeadline=(Get-Date).AddSeconds($RuntimeSeconds)
    do {
        Start-Sleep -Seconds 1
        if($editorProcess.HasExited){ throw "Unreal exited during runtime observation with code $($editorProcess.ExitCode)" }
    } while((Get-Date) -lt $observationDeadline)

    $txt=if(Test-Path $log){Get-Content $log -Raw}else{''}
    $missing=@($good | Where-Object { -not $txt.Contains($_) })
    $matches=[regex]::Matches($txt,$bad,[Text.RegularExpressions.RegexOptions]::IgnoreCase)
    $result.bad_count=$matches.Count
    $result.missing_good_signals=$missing
    $result.passed=($result.static_validation -and $result.startup_ready -and $result.experience_complete -and $result.capture_class_seen -and $result.bad_count -eq 0 -and $missing.Count -eq 0)
    if(-not $result.passed){ throw 'Capture prototype workflow gate failed; inspect JSON report/log.' }
}
finally {
    if($editorProcess -and -not $editorProcess.HasExited){ Stop-Process -Id $editorProcess.Id -Force -ErrorAction SilentlyContinue }
    $result.closed_after_test=$true
    $result | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 $report
}
Write-Host ('V73_CAPTURE_WORKFLOW=' + ($result | ConvertTo-Json -Compress))
