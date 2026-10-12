import unreal
reg=unreal.AssetRegistryHelpers.get_asset_registry()
root="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld"
assets=reg.get_assets_by_path(root,recursive=True)
unreal.log("[EXTREG] count=%d"%len(assets))
shown=0
for a in assets:
    cls=str(a.asset_class_path.asset_name)
    tags={}
    try:
        for k in ("ActorLabel","ActorClass","FolderPath","ActorFolderPath"):
            v=a.get_tag_value(k)
            if v: tags[k]=str(v)
    except: pass
    if shown<120:
        unreal.log("[EXTREG] %s cls=%s tags=%s"%(a.package_name,cls,tags))
        shown+=1
