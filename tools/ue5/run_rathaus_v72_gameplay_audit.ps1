param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8',
    [int]$RuntimeSeconds = 20
)
$ErrorActionPreference='Stop'
$repo=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$projectRoot=Join-Path $repo 'ue5\SpandauStrike'
$uproject=Join-Path $projectRoot 'SpandauStrike.uproject'
$editor=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$log=Join-Path $projectRoot 'Saved\Logs\SpandauStrike.log'
$reportDir=Join-Path $projectRoot 'Saved\Reports'
$report=Join-Path $reportDir 'v72_gameplay_audit.json'
$url='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v72_FIRST_PLAY?Experience=B_ShooterGame_Elimination'
$required=@(
  'LogGlobalStatus: UEngine::LoadMap Load map complete /Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v72_FIRST_PLAY',
  'LogLyraExperience: EXPERIENCE: OnExperienceLoadComplete(CurrentExperience = LyraExperienceDefinition:B_ShooterGame_Elimination',
  'SPANDAU_AUDIT POSSESSION',
  'SPANDAU_AUDIT READY',
  'SPANDAU_AUDIT EQUIPMENT',
  'SPANDAU_AUDIT MOVEMENT',
  'SPANDAU_AUDIT JUMP',
  'SPANDAU_AUDIT FIRE_INPUT',
  'SPANDAU_AUDIT COMPLETE'
)
$bad='FellOutOfWorld|KillZ|WorldBounds|Accessed None|Failed to spawn|SpawnActor failed|Fatal error|Unhandled Exception'
foreach($p in @($uproject,$editor)){ if(!(Test-Path $p)){ throw "Missing prerequisite: $p" } }
if(Get-Process UnrealEditor -ErrorAction SilentlyContinue){ throw 'Preflight refused: UnrealEditor already running.' }
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$result=[ordered]@{timestamp=(Get-Date).ToString('o'); runtime_seconds=$RuntimeSeconds; runtime_started=$false; map_loaded=$false; experience_complete=$false; possession=$false; equipment=$false; movement_passed=$false; jump_passed=$false; fire_bound_and_dispatched=$false; bad_count=-1; passed=$false; editor_pid=$null}
$p=$null
try {
  if(Test-Path $log){Remove-Item $log -Force}
  $p=Start-Process -FilePath $editor -ArgumentList @($uproject,$url,'-game','-windowed','-ResX=1280','-ResY=720','-unattended','-nop4','-log','-SpandauGameplayAudit') -PassThru
  $result.editor_pid=$p.Id; $result.runtime_started=$true
  $deadline=(Get-Date).AddSeconds($RuntimeSeconds)
  do {
    Start-Sleep -Milliseconds 500
    if($p.HasExited){throw "Unreal exited early with code $($p.ExitCode)"}
    $txt=if(Test-Path $log){Get-Content $log -Raw -ErrorAction SilentlyContinue}else{''}
    if($txt.Contains('SPANDAU_AUDIT COMPLETE')){break}
  } while((Get-Date) -lt $deadline)
  $txt=if(Test-Path $log){Get-Content $log -Raw}else{''}
  $result.map_loaded=$txt.Contains($required[0])
  $result.experience_complete=$txt.Contains($required[1])
  $result.possession=$txt.Contains('SPANDAU_AUDIT POSSESSION') -and $txt.Contains('SPANDAU_AUDIT READY')
  $result.equipment=$txt.Contains('SPANDAU_AUDIT EQUIPMENT quickbar=true') -and $txt.Contains('asc=')
  $result.movement_passed=[regex]::IsMatch($txt,'SPANDAU_AUDIT MOVEMENT .*passed=true')
  $result.jump_passed=[regex]::IsMatch($txt,'SPANDAU_AUDIT JUMP .*passed=true')
  $result.fire_bound_and_dispatched=[regex]::IsMatch($txt,'SPANDAU_AUDIT FIRE_INPUT .*binding_count=[1-9][0-9]* .*dispatched=true')
  $result.bad_count=[regex]::Matches($txt,$bad,[Text.RegularExpressions.RegexOptions]::IgnoreCase).Count
  $result.missing_required=@($required | Where-Object {-not $txt.Contains($_)})
  $result.passed=$result.map_loaded -and $result.experience_complete -and $result.possession -and $result.equipment -and $result.movement_passed -and $result.jump_passed -and $result.fire_bound_and_dispatched -and ($result.bad_count -eq 0) -and ($result.missing_required.Count -eq 0)
}
finally {
  if($p -and -not $p.HasExited){Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue}
  $result.closed_after_test=$true
  $result | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 $report
}
Write-Host ('V72_GAMEPLAY_AUDIT=' + ($result | ConvertTo-Json -Compress))
if(-not $result.passed){exit 2}
