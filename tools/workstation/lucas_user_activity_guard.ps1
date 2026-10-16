param(
    [int]$MinIdleSeconds = 30,
    [int]$SampleMilliseconds = 1500
)
$ErrorActionPreference='Stop'
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class SpandauInputGuard {
  [StructLayout(LayoutKind.Sequential)] public struct LASTINPUTINFO { public uint cbSize; public uint dwTime; }
  [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X; public int Y; }
  [DllImport("user32.dll")] public static extern bool GetLastInputInfo(ref LASTINPUTINFO plii);
  [DllImport("user32.dll")] public static extern bool GetCursorPos(out POINT lpPoint);
  [DllImport("kernel32.dll")] public static extern uint GetTickCount();
  public static double IdleSeconds(){ var li=new LASTINPUTINFO(); li.cbSize=(uint)Marshal.SizeOf(li); GetLastInputInfo(ref li); return (uint)(GetTickCount()-li.dwTime)/1000.0; }
}
"@
$idle0=[SpandauInputGuard]::IdleSeconds()
[SpandauInputGuard+POINT]$p0=New-Object SpandauInputGuard+POINT
[void][SpandauInputGuard]::GetCursorPos([ref]$p0)
Start-Sleep -Milliseconds $SampleMilliseconds
$idle1=[SpandauInputGuard]::IdleSeconds()
[SpandauInputGuard+POINT]$p1=New-Object SpandauInputGuard+POINT
[void][SpandauInputGuard]::GetCursorPos([ref]$p1)
$cursorMoved=($p0.X -ne $p1.X -or $p0.Y -ne $p1.Y)
$recentInput=($idle1 -lt $idle0 - 0.25)
$available=($idle1 -ge $MinIdleSeconds -and -not $cursorMoved -and -not $recentInput)
[pscustomobject]@{
  available=$available
  idle_seconds=[math]::Round($idle1,1)
  cursor_moved=$cursorMoved
  input_reset=$recentInput
  cursor_x=$p1.X
  cursor_y=$p1.Y
} | ConvertTo-Json -Compress
if($available){ exit 0 } else { exit 10 }
