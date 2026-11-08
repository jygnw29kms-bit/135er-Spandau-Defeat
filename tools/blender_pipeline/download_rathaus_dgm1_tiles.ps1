$ErrorActionPreference='Stop'
$root='C:\Users\anony\Documents\SpandauStrike\SourceData\DGM1'
New-Item -ItemType Directory -Force -Path $root | Out-Null
$tiles=@('376_5820','378_5820','376_5822','378_5822')
foreach($t in $tiles){
    $zip=Join-Path $root ("DGM1_${t}.zip")
    $url="https://gdi.berlin.de/data/dgm1/atom/DGM1_${t}.zip"
    Write-Host "DOWNLOAD $url"
    Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $zip
    $dst=Join-Path $root $t
    New-Item -ItemType Directory -Force -Path $dst | Out-Null
    Expand-Archive -Path $zip -DestinationPath $dst -Force
}
Get-ChildItem $root -Recurse -File | Select-Object FullName,Length | Format-Table -AutoSize
