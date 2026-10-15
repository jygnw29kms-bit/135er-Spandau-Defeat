param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8',
    [int]$RuntimeSeconds = 45
)
$ErrorActionPreference='Stop'
$repo=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$projectRoot=Join-Path $repo 'ue5\SpandauStrike'
$uproject=Join-Path $projectRoot 'SpandauStrike.uproject'
$editor=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$cmd=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$validator=Join-Path $projectRoot 'Content\Python\validate_rathaus_v72_spawn_safety.py'
$reportDir=Join-Path $projectRoot 'Saved\Reports'
$report=Join-Path $reportDir 'v72_firstplay_workflow.json'
$log=Join-Path $projectRoot 'Saved\Logs\SpandauStrike.log'
$url='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v72_FIRST_PLAY?Experience=B_ShooterGame_Elimination'
$bad='FellOutOfWorld|KillZ|WorldBounds|Accessed None|Failed to spawn|SpawnActor failed|Fatal error|Unhandled Exception|B_AI_Controller_LyraShooter.*Error'
$good=@('Load map complete /Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v72_FIRST_PLAY','Identified experience LyraExperienceDefinition:B_ShooterGame_Elimination','OnExperienceLoadComplete(CurrentExperience = LyraExperienceDefinition:B_ShooterGame_Elimination')
foreach($p in @($uproject,$editor,$cmd,$validator)){ if(!(Test-Path $p)){ throw "Missing prerequisite: $p" } }
if(Get-Process UnrealEditor -ErrorAction SilentlyContinue){ throw 'Preflight refused: UnrealEditor is already running. Close it before this isolated check.' }
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$result=[ordered]@{timestamp=(Get-Date).ToString('o'); map=$url; runtime_seconds=$RuntimeSeconds; static_validation=$false; runtime_started=$false; experience_complete=$false; bad_count=-1; passed=$false; editor_pid=$null}
$editorProcess=$null
try {
    $v=Start-Process -FilePath $cmd -ArgumentList @($uproject,'-run=pythonscript',('-script='+$validator),'-unattended','-nop4','-nosplash','-nullrhi') -PassThru -Wait
    if($v.ExitCode -ne 0){ throw "Spawn safety validator failed with exit code $($v.ExitCode)" }
    $result.static_validation=$true
    if(Test-Path $log){ Remove-Item $log -Force }
    $editorProcess=Start-Process -FilePath $editor -ArgumentList @($uproject,$url,'-game','-windowed','-ResX=1280','-ResY=720','-unattended','-nop4','-log') -PassThru
    $result.editor_pid=$editorProcess.Id; $result.runtime_started=$true
    $deadline=(Get-Date).AddSeconds($RuntimeSeconds)
    do {
        Start-Sleep -Seconds 1
        if($editorProcess.HasExited){ throw "Unreal exited early with code $($editorProcess.ExitCode)" }
        if(Test-Path $log){
            $txt=Get-Content $log -Raw -ErrorAction SilentlyContinue
            $result.experience_complete=$txt.Contains($good[2])
        }
    } while((Get-Date) -lt $deadline)
    $txt=if(Test-Path $log){Get-Content $log -Raw}else{''}
    $missing=@($good | Where-Object { -not $txt.Contains($_) })
    $matches=[regex]::Matches($txt,$bad,[Text.RegularExpressions.RegexOptions]::IgnoreCase)
    $result.bad_count=$matches.Count
    $result.missing_good_signals=$missing
    $result.passed=($result.static_validation -and $result.experience_complete -and $result.bad_count -eq 0 -and $missing.Count -eq 0)
    if(-not $result.passed){ throw 'First-play workflow gate failed; inspect JSON report/log.' }
}
finally {
    if($editorProcess -and -not $editorProcess.HasExited){ Stop-Process -Id $editorProcess.Id -Force -ErrorAction SilentlyContinue }
    $result.closed_after_test=$true
    $result | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 $report
}
Write-Host ('V72_FIRSTPLAY_WORKFLOW=' + ($result | ConvertTo-Json -Compress))
