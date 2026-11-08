param([string]$EngineRoot='C:\Program Files\Epic Games\UE_5.8',[int]$NumBots=15,[string]$MapPath='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v84_GROUND_LOCK_QA',[string]$ViewCmd='BugItGo 18610.425 17623.595 5893.75 -3.100491 -137.5 0')
$ErrorActionPreference='Stop'
$repo=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$uproject=Join-Path $repo 'ue5\SpandauStrike\SpandauStrike.uproject'
$editor=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$url="${MapPath}?Experience=B_ShooterGame_Elimination?NumBots=$NumBots"
$outDir=Join-Path $repo 'ue5\SpandauStrike\Saved\Screenshots\VisualQA'
$mapTag=($MapPath.Split('/')[-1] -replace '[^A-Za-z0-9_-]','_')
$logPath=Join-Path $repo "ue5\SpandauStrike\Saved\Logs\SpandauStrike_visualqa_$mapTag.log"
$diagPath=Join-Path $repo "ue5\SpandauStrike\Saved\Logs\SpandauStrike_visualqa_$mapTag.runner.txt"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
if(Test-Path $logPath){Remove-Item $logPath -Force}
if(Test-Path $diagPath){Remove-Item $diagPath -Force}
trap {
    ($_ | Out-String) | Set-Content -Encoding UTF8 $diagPath
    if($p -and -not $p.HasExited){Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue}
    exit 1
}
$execCmds="DisableAllScreenMessages,$ViewCmd"
$args=@($uproject,$url,'-game','-windowed','-ResX=1600','-ResY=900','-nop4',"-ExecCmds=`"$execCmds`"", "-ABSLOG=$logPath")
$p=Start-Process -FilePath $editor -ArgumentList $args -PassThru
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class SSWin {
 [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left,Top,Right,Bottom; }
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
 [DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr hWnd,int nCmdShow);
 [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
}
"@
$deadline=(Get-Date).AddSeconds(120)
$ready=$false
while((Get-Date)-lt $deadline){
 Start-Sleep -Milliseconds 500
 $p.Refresh()
 if($p.HasExited){throw "UE exited early: $($p.ExitCode)"}
 if(Test-Path $logPath){
  $tail=Get-Content $logPath -Tail 160 -ErrorAction SilentlyContinue
  if($tail -match '\[Phase_Playing_C_0\] Playing Phase'){ $ready=$true; break }
 }
}
if(-not $ready){throw 'Rathaus did not reach the Playing phase.'}
for($i=0;$i -lt 40;$i++){ $p.Refresh(); if($p.MainWindowHandle -ne 0){break}; Start-Sleep -Milliseconds 250 }
if($p.MainWindowHandle -eq 0){throw 'UE main window handle unavailable.'}
[SSWin]::ShowWindowAsync($p.MainWindowHandle,9)|Out-Null
[SSWin]::SetForegroundWindow($p.MainWindowHandle)|Out-Null
Start-Sleep -Seconds 8
$r=New-Object SSWin+RECT
[SSWin]::GetWindowRect($p.MainWindowHandle,[ref]$r)|Out-Null
$w=$r.Right-$r.Left; $h=$r.Bottom-$r.Top
$bmp=New-Object System.Drawing.Bitmap $w,$h
$g=[System.Drawing.Graphics]::FromImage($bmp)
$hdc=$g.GetHdc()
$printed=[SSWin]::PrintWindow($p.MainWindowHandle,$hdc,2)
$g.ReleaseHdc($hdc)
if(-not $printed){
 $g.CopyFromScreen($r.Left,$r.Top,0,0,(New-Object System.Drawing.Size($w,$h)))
}
$stamp=Get-Date -Format 'yyyyMMdd_HHmmss'
$out=Join-Path $outDir "${mapTag}_visualqa_$stamp.png"
$bmp.Save($out,[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Host "SCREENSHOT=$out"
Start-Sleep -Seconds 2
Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
