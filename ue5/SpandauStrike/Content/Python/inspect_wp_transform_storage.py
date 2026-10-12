import unreal
EXT="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld"
reg=unreal.AssetRegistryHelpers.get_asset_registry()
seen=0
for a in reg.get_assets_by_path(EXT,recursive=True):
    lab=str(a.get_tag_value("ActorLabel") or "")
    if not lab.startswith("GIS_Road_"): continue
    o=a.get_asset(); c=o.root_component
    unreal.log("[WPTX] %s pkg=%s"%(lab,a.package_name))
    unreal.log("[WPTX] actor_loc=%s transform=%s"%(o.get_actor_location(),o.get_actor_transform()))
    unreal.log("[WPTX] rel_loc=%s rel_tx=%s comp_loc=%s comp_tx=%s"%(c.get_relative_location(),c.get_relative_transform(),c.get_component_location(),c.get_component_transform()))
    try: unreal.log("[WPTX] tags="+str(a.tags_and_values))
    except Exception as e: unreal.log("[WPTX] tags_err="+str(e))
    seen+=1
    if seen>=2: break
