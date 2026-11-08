# GetLastInputInfo is session-local. DCO service runs in session 0, while Lucas uses the console session.
$console = Get-CimInstance Win32_Process -Filter "Name = 'explorer.exe'" | Where-Object { $_.SessionId -ne 0 } | Select-Object -First 1
if ($console -and $console.SessionId -ne (Get-Process -Id $PID).SessionId) {
  Write-Output ("IDLE_UNKNOWN=SESSION_MISMATCH; DCO_SESSION=" + (Get-Process -Id $PID).SessionId + "; CONSOLE_SESSION=" + $console.SessionId)
  exit 2
}
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class SSIdle {
  [StructLayout(LayoutKind.Sequential)] public struct LASTINPUTINFO { public uint cbSize; public uint dwTime; }
  [DllImport("user32.dll")] public static extern bool GetLastInputInfo(ref LASTINPUTINFO plii);
}
"@
$li = New-Object SSIdle+LASTINPUTINFO
$li.cbSize = [Runtime.InteropServices.Marshal]::SizeOf($li)
if (-not [SSIdle]::GetLastInputInfo([ref]$li)) { throw 'GetLastInputInfo failed; idle state unknown' }
# LASTINPUTINFO.dwTime is a 32-bit tick count; subtract modulo 2^32 to handle wraparound.
$now32 = [uint64](([Environment]::TickCount64 % 4294967296L + 4294967296L) % 4294967296L)
$idleMs = ($now32 - [uint64]$li.dwTime + 4294967296L) % 4294967296L
Write-Output ("IDLE_SEC=" + [math]::Round($idleMs / 1000.0, 1))
Get-Process UnrealEditor -ErrorAction SilentlyContinue | Select-Object Id,StartTime,MainWindowTitle | Format-List
