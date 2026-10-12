import unreal
EXT="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld"
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
reg=unreal.AssetRegistryHelpers.get_asset_registry()
for a in reg.get_assets_by_path(EXT,recursive=True):
    lab=str(a.get_tag_value("ActorLabel") or "")
    if lab in ("SS_ExactBuildings","SS_DGM1_Terrain"):
        obj=a.get_asset()
        unreal.log("[HLODREF] actor="+lab+" pkg="+str(a.package_name))
        for p in ("hlod_layer","enable_auto_lod_generation"):
            try: unreal.log("[HLODREF] "+p+"="+str(obj.get_editor_property(p)))
            except Exception as e: unreal.log("[HLODREF] "+p+" ERR "+str(e))
try:
    deps=reg.get_dependencies(MAP, unreal.AssetRegistryDependencyOptions(
        include_soft_package_references=True,
        include_hard_package_references=True,
        include_searchable_names=False,
        include_soft_management_references=True,
        include_hard_management_references=True))
    for dep in deps:
        if "HLOD" in str(dep) or "hlod" in str(dep):
            unreal.log("[HLODREF] dependency="+str(dep))
except Exception as e:
    unreal.log_error("[HLODREF] deps ERR "+str(e))
