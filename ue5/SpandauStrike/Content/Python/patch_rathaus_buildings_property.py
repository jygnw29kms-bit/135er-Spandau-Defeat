import unreal, traceback
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1"
NEW="/ShooterMaps/GeneratedGIS/RathausSpandauFinal/SM_Rathaus_Buildings_NoLandmark"
def log(s): unreal.log("[RATHAUS_PROP_PATCH] "+str(s))
try:
    new=unreal.EditorAssetLibrary.load_asset(NEW)
    if not new: raise RuntimeError("new buildings mesh missing")
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("map load failed")
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    hits=[]
    for a in eas.get_all_level_actors():
        if isinstance(a, unreal.StaticMeshActor):
            c=a.static_mesh_component
            m=c.get_editor_property("static_mesh")
            mp=m.get_path_name() if m else ""
            lab=a.get_actor_label()
            log("ACTOR "+lab+" | "+mp)
            low=(mp+" "+lab).lower()
            if ("rathaus_buildings" in low or "rathaus_exactbuildings" in low) and "nolandmark" not in low:
                hits.append(a)
    log("HITS="+str(len(hits)))
    for a in hits:
        a.static_mesh_component.set_editor_property("static_mesh",new)
        a.set_actor_label("Rathaus_Buildings_NoLandmark")
        a.static_mesh_component.set_collision_profile_name("BlockAll")
        log("REPLACED "+a.get_name())
    if not sub.save_current_level(): raise RuntimeError("save failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("READY")
except Exception as e:
    unreal.log_error("[RATHAUS_PROP_PATCH] FAILED "+str(e))
    unreal.log_error(traceback.format_exc())
    raise
