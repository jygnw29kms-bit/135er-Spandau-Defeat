import unreal, traceback
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1"
NEW="/ShooterMaps/GeneratedGIS/RathausSpandauFinal/SM_Rathaus_Buildings_NoLandmark"
def log(s): unreal.log("[RATHAUS_PATCH] "+str(s))
try:
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("map load failed")
    new=unreal.EditorAssetLibrary.load_asset(NEW)
    if not new: raise RuntimeError("filtered buildings asset missing")
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    hits=[]
    for a in actors.get_all_level_actors():
        if isinstance(a, unreal.StaticMeshActor):
            c=a.static_mesh_component
            m=c.get_static_mesh()
            path=m.get_path_name() if m else ""
            log(a.get_actor_label()+" | "+path)
            lp=path.lower()
            if ("rathaus_buildings" in lp or "rathaus_exactbuildings" in lp) and "nolandmark" not in lp:
                hits.append(a)
    if not hits:
        # fallback: choose the old large building actor by label containing building and Rathaus
        for a in actors.get_all_level_actors():
            if isinstance(a, unreal.StaticMeshActor):
                lab=a.get_actor_label().lower()
                if "rathaus" in lab and "building" in lab and "landmark_final" not in lab:
                    hits.append(a)
    log("HITS="+str(len(hits)))
    for a in hits:
        a.static_mesh_component.set_static_mesh(new)
        a.set_actor_label("Rathaus_Buildings_NoLandmark")
        a.static_mesh_component.set_collision_profile_name("BlockAll")
        log("REPLACED "+a.get_name())
    if not sub.save_current_level(): raise RuntimeError("save failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("READY")
except Exception as e:
    unreal.log_error("[RATHAUS_PATCH] FAILED "+str(e))
    unreal.log_error(traceback.format_exc())
    raise
