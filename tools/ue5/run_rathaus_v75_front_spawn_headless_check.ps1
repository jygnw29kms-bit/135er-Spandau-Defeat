param(
    [string]$EngineRoot='C:\Program Files\Epic Games\UE_5.8',
    [int]$StartupTimeoutSeconds=120,
    [int]$RuntimeSeconds=45,
    [int]$NumBots=15
)

$ErrorActionPreference='Stop'
$runner=Join-Path $PSScriptRoot 'run_rathaus_v75_front_spawn_headless_check.py'

& python $runner `
    --engine-root $EngineRoot `
    --startup-timeout $StartupTimeoutSeconds `
    --runtime-seconds $RuntimeSeconds `
    --num-bots $NumBots

exit $LASTEXITCODE
