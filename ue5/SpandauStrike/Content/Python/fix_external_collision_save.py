import unreal, traceback
EXT="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld"
EXACT="/ShooterMaps/Maps/SpandauStrikeGIS/Assets/SM_Falkenhagener_ExactBuildings"
DGM="/ShooterMaps/Maps/SpandauStrikeGIS/Assets/SM_Falkenhagener_DGM1"
MB="/ShooterMaps/Maps/SpandauStrikeGIS/Assets/M_Falkenhagener_Buildings"
MT="/ShooterMaps/Maps/SpandauStrikeGIS/Assets/M_Falkenhagener_Terrain"
def log(s): unreal.log("[EXTFIX] "+str(s))
def main():
    reg=unreal.AssetRegistryHelpers.get_asset_registry()
    assets=reg.get_assets_by_path(EXT,recursive=True)
    mesh_b=unreal.EditorAssetLibrary.load_asset(EXACT)
    mesh_t=unreal.EditorAssetLibrary.load_asset(DGM)
    mat_b=unreal.EditorAssetLibrary.load_asset(MB)
    mat_t=unreal.EditorAssetLibrary.load_asset(MT)
    touched=[]
    for a in assets:
        lab=str(a.get_tag_value("ActorLabel") or "")
        if lab!="SS_ExactBuildings" and not lab.startswith("SS_DGM"): continue
        obj=a.get_asset()
        if not obj: continue
        comp=obj.static_mesh_component
        log("%s pkg=%s mesh=%s collision=%s profile=%s loc=%s"%(lab,a.package_name,
            comp.static_mesh.get_path_name() if comp.static_mesh else None,
            comp.get_collision_enabled(),comp.get_collision_profile_name(),obj.get_actor_location()))
        if lab=="SS_ExactBuildings":
            comp.set_static_mesh(mesh_b); comp.set_material(0,mat_b)
        else:
            comp.set_static_mesh(mesh_t); comp.set_material(0,mat_t)
        comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        comp.set_collision_profile_name("BlockAll")
        obj.modify(); comp.modify(); touched.append(lab)
    ok=unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("save_dirty="+str(ok)+" touched="+str(touched))
    log("EXTFIX_READY")
if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[EXTFIX] FAILED "+str(e)); unreal.log_error(traceback.format_exc()); raise
