param([int]$RuntimeSeconds=65)
$ErrorActionPreference='Stop'
$repo=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$root=Join-Path $repo 'ue5\SpandauStrike'
$exe='C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$map='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v87_NATIVE_LANDSCAPE_QA?Experience=B_ShooterGame_Elimination?NumBots=15'
$stamp=Get-Date -Format 'yyyyMMdd_HHmmss'
$log=Join-Path $root "Saved\Logs\v87_ground_smoke_$stamp.log"
$report=Join-Path $root "Saved\Reports\v87_ground_smoke_$stamp.json"
function Read-LiveLog([string]$path) {
 if(-not (Test-Path $path)){return ''}
 $stream=[System.IO.FileStream]::new($path,[System.IO.FileMode]::Open,[System.IO.FileAccess]::Read,[System.IO.FileShare]::ReadWrite)
 try { $reader=[System.IO.StreamReader]::new($stream); return $reader.ReadToEnd() } finally { $reader.Dispose() }
}
$p=$null
try {
 $args=@((Join-Path $root 'SpandauStrike.uproject'),$map,'-game','-nullrhi','-nosound','-unattended','-nop4','-SpandauGroundProbe',"-ABSLOG=$log")
 $p=Start-Process -FilePath $exe -ArgumentList $args -PassThru
 $deadline=(Get-Date).AddSeconds(150)
 $ready=$false
 while((Get-Date)-lt $deadline) {
  Start-Sleep -Seconds 1
  $p.Refresh()
  if($p.HasExited){break}
  if(Test-Path $log) {
   $t=Read-LiveLog $log
   if($t.Contains('Spandau objective routing: sector=1 routed=15 failed=0')) {$ready=$true;break}
  }
 }
 if($ready){ Start-Sleep -Seconds $RuntimeSeconds }
 $t=if(Test-Path $log){Read-LiveLog $log}else{''}
 $events=@{}
 foreach($k in @('Spandau restart finished:','Spandau objective routing:','Playing Phase','FellOutOfWorld','KillZ','WorldBounds','Spandau respawn completed:','LogCharacterMovement: Warning')) {
  $events[$k]=([regex]::Matches($t,[regex]::Escape($k))).Count
 }
 $probes=[regex]::Matches($t,'Spandau ground probe: t=([0-9.]+) pawn=([^ ]+) human=([01]).*?hit=([01]).*?gap=([-0-9.]+) falling=([01]).*?result=(OK|FAIL)')
 $summaries=[regex]::Matches($t,'Spandau ground probe summary: t=([0-9.]+) sampled=([0-9]+) failed=([0-9]+)')
 $failCount=0; $humanCount=0; $noHitCount=0
 foreach($match in $probes){ if($match.Groups[7].Value -eq 'FAIL'){$failCount++}; if($match.Groups[3].Value -eq '1'){$humanCount++}; if($match.Groups[4].Value -eq '0'){$noHitCount++} }
 $hitActors=[regex]::Matches($t,'Spandau ground probe:.*?hitActor=([^ ]+) result=(OK|FAIL)')
 $landscapeHits=@($hitActors | Where-Object {$_.Groups[1].Value -match '^Landscape'}).Count
 $staticMeshHits=@($hitActors | Where-Object {$_.Groups[1].Value -match '^StaticMeshActor'}).Count
 $lastT=if($summaries.Count){[double]$summaries[$summaries.Count-1].Groups[1].Value}else{0}
 $intervals=@(0,5,15,30,60)
 $completeIntervals=0
 foreach($target in $intervals){
  $matching=@($summaries | Where-Object { [math]::Abs([double]$_.Groups[1].Value-$target) -le 1.5 -and [int]$_.Groups[2].Value -ge 16 -and [int]$_.Groups[3].Value -eq 0 })
  if($matching.Count -gt 0){$completeIntervals++}
 }
 # Native Landscape is the required collision surface; StaticMeshActor hits cannot pass P0.
 $allHitsAreLandscape=($hitActors.Count -eq $probes.Count) -and ($landscapeHits -eq $probes.Count)
 $groundPassed=$ready -and $RuntimeSeconds -ge 60 -and $probes.Count -ge 80 -and $completeIntervals -eq $intervals.Count -and $lastT -ge 60 -and $humanCount -ge 5 -and $failCount -eq 0 -and $noHitCount -eq 0 -and $allHitsAreLandscape
 $result=[ordered]@{timestamp=(Get-Date).ToString('o');map=$map;log=$log;runtime_seconds=$RuntimeSeconds;startup_ready=$ready;events=$events;ground_probe_samples=$probes.Count;ground_probe_intervals=$summaries.Count;ground_probe_required_intervals_passed=$completeIntervals;ground_probe_required_intervals=$intervals;ground_probe_last_second=$lastT;ground_probe_human_samples=$humanCount;ground_probe_failed_samples=$failCount;ground_probe_nohit_samples=$noHitCount;ground_probe_landscape_hits=$landscapeHits;ground_probe_static_mesh_hits=$staticMeshHits;ground_probe_all_hits_landscape=$allHitsAreLandscape;ground_probe_passed=$groundPassed;grounding_proven=$false;note='Probe is diagnostic only; full Grounding PASS also requires capsule sweep, movement and respawn verification.'}
 $result|ConvertTo-Json -Depth 5|Set-Content -Path $report -Encoding utf8
 Write-Output "REPORT=$report"
 Write-Output ($result|ConvertTo-Json -Depth 5)
 if(-not $groundPassed){ exit 2 }
} finally {
 if($p){$p.Refresh();if(-not $p.HasExited){Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue}}
}
