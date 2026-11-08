param([string]$LogPath = (Join-Path $PSScriptRoot '..\..\ue5\SpandauStrike\Saved\Logs\v84_ground_smoke_20261107_164233.log'))
$ErrorActionPreference='Stop'
if(-not (Test-Path $LogPath)){throw "Baseline log missing: $LogPath"}
$raw=[System.IO.File]::ReadAllText((Resolve-Path $LogPath).Path)
$probes=[regex]::Matches($raw,'Spandau ground probe: t=([0-9.]+) pawn=([^ ]+) human=([01]).*?hit=([01]).*?gap=([-0-9.]+) falling=([01]).*?result=(OK|FAIL)')
$summaries=[regex]::Matches($raw,'Spandau ground probe summary: t=([0-9.]+) sampled=([0-9]+) failed=([0-9]+)')
$failed=@($probes | Where-Object {$_.Groups[7].Value -eq 'FAIL'}).Count
$noHit=@($probes | Where-Object {$_.Groups[4].Value -eq '0'}).Count
$human=@($probes | Where-Object {$_.Groups[3].Value -eq '1'}).Count
$expected=@(5,2,6,6,6)
$actual=@($summaries | ForEach-Object {[int]$_.Groups[3].Value})
$ok=$probes.Count -eq 80 -and $summaries.Count -eq 5 -and $failed -eq 25 -and $noHit -eq 10 -and $human -eq 5 -and (($actual -join ',') -eq ($expected -join ','))
[pscustomobject]@{log=$LogPath;samples=$probes.Count;summary_failures=$actual -join ',';failed=$failed;no_hit=$noHit;human=$human;baseline_reproduced=$ok;grounding_pass=$false} | ConvertTo-Json
if(-not $ok){throw 'Baseline regression mismatch: inspect parser or source log'}
