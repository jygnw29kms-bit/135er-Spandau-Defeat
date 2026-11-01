param(
    [string]$EngineRoot='C:\Program Files\Epic Games\UE_5.8',
    [int]$NumBots=15,
    [int]$CaptureFrames=12000,
    [int]$WarmupSeconds=20,
    [int]$MeasureSeconds=30,
    [int]$TimeoutSeconds=900,
    [string]$MapPath=''
)

$ErrorActionPreference='Stop'
$repo=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$uproject=Join-Path $repo 'ue5\SpandauStrike\SpandauStrike.uproject'
$editor=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
if(-not $MapPath){ $MapPath=(Get-Content (Join-Path $PSScriptRoot 'rathaus_validation_target.json') -Raw | ConvertFrom-Json).map_path }
$url="${MapPath}?Experience=B_ShooterGame_Elimination?NumBots=$NumBots"
$logPath=Join-Path $repo 'ue5\SpandauStrike\Saved\Logs\SpandauStrike_v75_csvperf_current.log'
$started=Get-Date
if(Test-Path $logPath){ Remove-Item $logPath -Force }

$profileRoots=@(
    (Join-Path $repo 'ue5\SpandauStrike\Saved\Profiling\CSV'),
    (Join-Path $env:LOCALAPPDATA 'UnrealEngine\5.8\Saved\Profiling\CSV')
)

Write-Host "Starting Rathaus CSV perf capture: map=$MapPath bots=$NumBots frames=$CaptureFrames"
$args=@(
    $uproject,
    $url,
    '-game',
    '-windowed',
    '-ResX=1600',
    '-ResY=900',
    '-nop4',
    "-ABSLOG=$logPath",
    "-csvCaptureFrames=$CaptureFrames",
    '-csvCompression=0'
)
$p=Start-Process -FilePath $editor -ArgumentList $args -PassThru
Write-Host "Unreal PID=$($p.Id)"

Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class SpandauForeground {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);
}
"@
$focused=$false
for($i=0; $i -lt 100; $i++){
    Start-Sleep -Milliseconds 200
    $p.Refresh()
    if($p.HasExited){ break }
    if($p.MainWindowHandle -ne 0){
        [SpandauForeground]::ShowWindowAsync($p.MainWindowHandle,9) | Out-Null
        [SpandauForeground]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
        $focused=$true
        Write-Host "Foreground window activated: handle=$($p.MainWindowHandle)"
        break
    }
}
if(-not $focused){ Write-Warning 'Unreal main window could not be activated before capture polling.' }

$deadline=(Get-Date).AddSeconds($TimeoutSeconds)
$captureEnded=$false
while((Get-Date) -lt $deadline){
    Start-Sleep -Seconds 2
    $p.Refresh()
    if(Test-Path $logPath){
        $tail=Get-Content $logPath -Tail 80 -ErrorAction SilentlyContinue
        if($tail -match 'Capture Ended\. Writing CSV to file'){
            $captureEnded=$true
            break
        }
    }
    if($p.HasExited){
        Write-Host "Unreal exited early with code $($p.ExitCode)"
        break
    }
}

if(-not $captureEnded){
    if(-not $p.HasExited){ Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
    Write-Host '--- UE LOG TAIL ---'
    if(Test-Path $logPath){ Get-Content $logPath -Tail 120 }
    throw 'CSV capture did not reach Capture Ended.'
}

Start-Sleep -Seconds 2
$candidates=@()
foreach($root in $profileRoots){
    if(Test-Path $root){
        $candidates += Get-ChildItem $root -File -Filter '*.csv' | Where-Object { $_.LastWriteTime -ge $started.AddSeconds(-5) -and $_.Length -gt 1024 }
    }
}
$csv=$candidates | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if(-not $csv){
    Write-Host '--- UE LOG TAIL ---'
    Get-Content $logPath -Tail 120
    throw 'Capture ended but no non-empty fresh UE CSV profile was found.'
}
Write-Host "Fresh CSV=$($csv.FullName) size=$($csv.Length)"

if(-not $p.HasExited){
    Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
    Write-Host 'Stopped perf-test UE instance after CSV finalization.'
}

Set-Location $repo
& node 'tools\ue5\analyze_rathaus_csv_profile.js' $csv.FullName --warmup $WarmupSeconds --measure $MeasureSeconds --out-dir 'ue5\SpandauStrike\Saved\Profiling\Reports'
if($LASTEXITCODE -ne 0){ exit $LASTEXITCODE }
exit 0

