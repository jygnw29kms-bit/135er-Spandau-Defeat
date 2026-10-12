import unreal
EXT="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld"
reg=unreal.AssetRegistryHelpers.get_asset_registry()
seen=0
for a in reg.get_assets_by_path(EXT,recursive=True):
    lab=str(a.get_tag_value("ActorLabel") or "")
    if lab=="SS_ExactBuildings" or lab=="SS_DGM1_Terrain" or lab.startswith("GIS_Road_"):
        obj=a.get_asset()
        if not obj: continue
        unreal.log("[ACTHLOD] label="+lab+" pkg="+str(a.package_name))
        for p in ["hlod_layer","include_actor_in_hlod","enable_auto_lod_generation"]:
            try: unreal.log("[ACTHLOD] "+p+"="+str(obj.get_editor_property(p)))
            except Exception as e: unreal.log("[ACTHLOD] "+p+" ERR "+str(e))
        seen+=1
        if seen>=4: break
