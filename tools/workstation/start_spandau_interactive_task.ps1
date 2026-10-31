param(
    [string]$TaskName='SpandauStrike_RathausPerf',
    [string]$ScriptPath='C:\Users\anony\Documents\SpandauStrike\repo\tools\ue5\run_rathaus_v75_csv_perf.ps1'
)

$ErrorActionPreference='Stop'
$user="$env:COMPUTERNAME\anony"
if(-not (Test-Path $ScriptPath)){ throw "Script not found: $ScriptPath" }

$argument="-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ScriptPath`""
$action=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $argument
$principal=New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Highest
$settings=New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 2) -MultipleInstances IgnoreNew

if(Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue){
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}
Register-ScheduledTask -TaskName $TaskName -Action $action -Principal $principal -Settings $settings | Out-Null
Start-ScheduledTask -TaskName $TaskName
Start-Sleep -Seconds 2
Get-ScheduledTask -TaskName $TaskName | Select-Object TaskName,State
Get-ScheduledTaskInfo -TaskName $TaskName | Select-Object LastRunTime,LastTaskResult,NextRunTime
