import unreal
EXT="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld"
reg=unreal.AssetRegistryHelpers.get_asset_registry()
assets=reg.get_assets_by_path(EXT,recursive=True)
for a in assets:
    lab=str(a.get_tag_value("ActorLabel") or "")
    if lab.startswith("SS_DGM") or lab.startswith("GIS_DGM") or lab=="SS_ExactBuildings":
        unreal.log("[GISEXT] label="+lab+" pkg="+str(a.package_name)+" class="+str(a.asset_class_path))
