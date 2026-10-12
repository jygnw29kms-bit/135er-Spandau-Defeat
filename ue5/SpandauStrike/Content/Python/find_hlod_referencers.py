import unreal
reg=unreal.AssetRegistryHelpers.get_asset_registry()
opts=unreal.AssetRegistryDependencyOptions(
    include_soft_package_references=True,
    include_hard_package_references=True,
    include_searchable_names=False,
    include_soft_management_references=True,
    include_hard_management_references=True)
for p in [
"/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld_HLODLayer_Instanced",
"/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld_HLODLayer_Merged"]:
    unreal.log("[HLODREV] target="+p)
    try:
        refs=reg.get_referencers(p,opts)
        for x in refs: unreal.log("[HLODREV] ref="+str(x))
    except Exception as e: unreal.log_error("[HLODREV] "+str(e))
