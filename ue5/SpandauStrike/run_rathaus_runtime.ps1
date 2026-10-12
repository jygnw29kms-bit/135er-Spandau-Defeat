$ErrorActionPreference = "Stop"
$ue = "C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe"
$project = "C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\SpandauStrike.uproject"
$map = "/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1?NumBots=7"
& $ue $project $map -game -d3d11 -windowed -ResX=1280 -ResY=720 -NoSplash -log
