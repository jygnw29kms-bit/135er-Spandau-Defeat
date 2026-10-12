import unreal, traceback
EXT="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld"
MAT_B="/ShooterMaps/Maps/SpandauStrikeGIS/Assets/M_Falkenhagener_Buildings"
MAT_T="/ShooterMaps/Maps/SpandauStrikeGIS/Assets/M_Falkenhagener_Terrain"
def log(s): unreal.log("[GISCLEAN] "+str(s))
def main():
    reg=unreal.AssetRegistryHelpers.get_asset_registry()
    assets=list(reg.get_assets_by_path(EXT,recursive=True))
    dgms=[]
    for a in assets:
        lab=str(a.get_tag_value("ActorLabel") or "")
        if lab.startswith("SS_DGM") or lab.startswith("GIS_DGM"):
            dgms.append((str(a.package_name),lab,a))
    dgms.sort(key=lambda x:x[0])
    ss=[x for x in dgms if x[1].startswith("SS_DGM")]
    if not ss: raise RuntimeError("no SS_DGM terrain actor")
    keep=ss[0]
    log("keep "+keep[0])
    for pkg,lab,a in dgms:
        if pkg==keep[0]: continue
        ok=unreal.EditorAssetLibrary.delete_asset(pkg)
        log("delete "+lab+" "+pkg+" = "+str(ok))
    obj=keep[2].get_asset()
    mt=unreal.EditorAssetLibrary.load_asset(MAT_T)
    if obj and mt:
        c=obj.static_mesh_component
        c.set_material(0,mt)
        c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        c.set_collision_profile_name("BlockAll")
        obj.modify()
        unreal.EditorAssetLibrary.save_asset(keep[0],only_if_is_dirty=False)
        log("retained terrain material/collision updated")
    mb=unreal.EditorAssetLibrary.load_asset(MAT_B)
    if not mb: raise RuntimeError("building material missing")
    ok_nanite=False
    for prop in ("used_with_nanite","b_used_with_nanite","bUsedWithNanite"):
        try:
            mb.set_editor_property(prop,True)
            log("nanite property set via "+prop)
            ok_nanite=True
            break
        except Exception as e:
            log("nanite property "+prop+" unavailable")
    unreal.MaterialEditingLibrary.recompile_material(mb)
    unreal.EditorAssetLibrary.save_loaded_asset(mb,only_if_is_dirty=False)
    log("building material saved nanite="+str(ok_nanite))
    log("READY")
if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[GISCLEAN] FAILED "+str(e)); unreal.log_error(traceback.format_exc()); raise
