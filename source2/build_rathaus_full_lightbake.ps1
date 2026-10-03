$ErrorActionPreference = "Stop"
$rc = "E:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive\game\bin\win64\resourcecompiler.exe"
$map = "E:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive\content\csgo_addons\spandau_defeat\maps\rathaus_spandau.vmap"
$out = "C:\Users\Public\SpandauDefeatMapProduction\rebuild_20260928\rathaus_full_lightbake"
New-Item -ItemType Directory -Force -Path $out | Out-Null
& $rc -threads 5 -fshallow -maxtextureres 256 -dxlevel 110 -quiet -unbufferedio -i $map -noassert -world -bakelighting -lightmapMaxResolution 1024 -lightmapDoWeld -lightmapVRadQuality 1 -lightmapLocalCompile -phys -vis -nav -retail -breakpad -nop4 -outroot $out -lightmapcpu
exit $LASTEXITCODE
