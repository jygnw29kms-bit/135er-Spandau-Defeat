$project='C:\Users\dezen\Documents\Unreal Projects\SpandauStrike'
$exe='C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$uproject=Join-Path $project 'SpandauStrike.uproject'
$prep=Join-Path $project 'Saved\GIS\prepare_map_v1.py'
$select=Join-Path $project 'Saved\GIS\select_gameplay_points.py'
$build=Join-Path $project 'Content\Python\build_generic_playable_v1.py'
$final=Join-Path $project 'Content\Python\finalize_generic_playable_v1.py'
$log=Join-Path $project 'Saved\GIS\batch_hist2_status.log'
$maps=@('radeland_1945','hakenfelde_heeresamt_1944','zitadelle_1945','britischer_sektor_spandau')
"START $(Get-Date -Format s)" | Set-Content $log
foreach($m in $maps){
  try {
    "[$m] PREP $(Get-Date -Format s)" | Add-Content $log
    & python -u $prep $m 550
    if($LASTEXITCODE -ne 0){ throw "prep $LASTEXITCODE" }
    & python -u $select $m 550
    if($LASTEXITCODE -ne 0){ throw "select $LASTEXITCODE" }
    "[$m] BUILD $(Get-Date -Format s)" | Add-Content $log
    $env:SPANDAU_MAPID=$m
    & $exe $uproject "-ExecutePythonScript=$build" -unattended -nullrhi -nosplash -NoSound -stdout -FullStdOutLogOutput
    if($LASTEXITCODE -ne 0){ throw "build $LASTEXITCODE" }
    "[$m] FINAL $(Get-Date -Format s)" | Add-Content $log
    & $exe $uproject "-ExecutePythonScript=$final" -unattended -nullrhi -nosplash -NoSound -stdout -FullStdOutLogOutput
    if($LASTEXITCODE -ne 0){ throw "final $LASTEXITCODE" }
    "[$m] READY $(Get-Date -Format s)" | Add-Content $log
  } catch {
    "[$m] FAILED $($_.Exception.Message) $(Get-Date -Format s)" | Add-Content $log
  }
}
"DONE $(Get-Date -Format s)" | Add-Content $log
