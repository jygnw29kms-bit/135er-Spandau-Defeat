import unreal, traceback
DROP={
"/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld/9/OJ/EB7AG52WPY7LVO3GBQ58A8",
"/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld/B/WW/LDCUIP91CWEM4DF4JKCJR1",
}
EXT="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld"
def log(s): unreal.log("[DGMCLEAN] "+str(s))
def main():
    reg=unreal.AssetRegistryHelpers.get_asset_registry()
    changed=[]
    for a in reg.get_assets_by_path(EXT,recursive=True):
        p=str(a.package_name)
        if p not in DROP: continue
        obj=a.get_asset()
        if not obj: continue
        c=obj.static_mesh_component
        obj.set_actor_hidden_in_game(True)
        c.set_visibility(False,True)
        c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        c.set_collision_profile_name("NoCollision")
        obj.modify(); c.modify(); changed.append(p)
        log("disabled "+p)
    ok=unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("save_dirty="+str(ok)+" changed="+str(changed))
    log("DGMCLEAN_READY")
if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[DGMCLEAN] FAILED "+str(e)); unreal.log_error(traceback.format_exc()); raise
