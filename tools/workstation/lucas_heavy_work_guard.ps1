param(
    [int]$MinIdleSeconds = 60,
    [int]$SampleMilliseconds = 1200,
    [int]$MaxGpu3DPercent = 55
)
$ErrorActionPreference='Stop'
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class SpandauHeavyGuardInput {
  [StructLayout(LayoutKind.Sequential)] public struct LASTINPUTINFO { public uint cbSize; public uint dwTime; }
  [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X; public int Y; }
  [DllImport("user32.dll")] public static extern bool GetLastInputInfo(ref LASTINPUTINFO plii);
  [DllImport("user32.dll")] public static extern bool GetCursorPos(out POINT lpPoint);
  [DllImport("kernel32.dll")] public static extern uint GetTickCount();
  public static double IdleSeconds(){ var li=new LASTINPUTINFO(); li.cbSize=(uint)Marshal.SizeOf(li); GetLastInputInfo(ref li); return (uint)(GetTickCount()-li.dwTime)/1000.0; }
}
"@
$idle0=[SpandauHeavyGuardInput]::IdleSeconds(); [SpandauHeavyGuardInput+POINT]$p0=New-Object SpandauHeavyGuardInput+POINT; [void][SpandauHeavyGuardInput]::GetCursorPos([ref]$p0)
Start-Sleep -Milliseconds $SampleMilliseconds
$idle1=[SpandauHeavyGuardInput]::IdleSeconds(); [SpandauHeavyGuardInput+POINT]$p1=New-Object SpandauHeavyGuardInput+POINT; [void][SpandauHeavyGuardInput]::GetCursorPos([ref]$p1)
$cursorMoved=($p0.X -ne $p1.X -or $p0.Y -ne $p1.Y); $recentInput=($idle1 -lt $idle0 - 0.25); $inputAvailable=($idle1 -ge $MinIdleSeconds -and -not $cursorMoved -and -not $recentInput)
$blockingNames=@('openomsi','UnrealEditor','blender','Fusion360','OrcaSlicer','BambuStudio')
$blocking=@(Get-Process -ErrorAction SilentlyContinue | Where-Object { $blockingNames -contains $_.ProcessName } | Select-Object Id,ProcessName,MainWindowTitle)
$gpuSamples=@(Get-CimInstance Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine -ErrorAction SilentlyContinue | Where-Object { $_.Name -match 'engtype_3D$' } | Select-Object -ExpandProperty UtilizationPercentage)
$gpu3d=if($gpuSamples.Count){ [double](($gpuSamples | Measure-Object -Maximum).Maximum) } else { 0.0 }
$available=$inputAvailable -and $blocking.Count -eq 0 -and $gpu3d -le $MaxGpu3DPercent
[pscustomobject]@{ available=$available; input_available=$inputAvailable; idle_seconds=[math]::Round($idle1,1); cursor_moved=$cursorMoved; input_reset=$recentInput; gpu3d_max_percent=[math]::Round($gpu3d,1); blocking_processes=@($blocking) } | ConvertTo-Json -Depth 4 -Compress
if($available){ exit 0 } else { exit 11 }
