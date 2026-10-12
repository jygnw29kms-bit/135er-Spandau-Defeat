import unreal, traceback
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld_playable_v8"
def log(s): unreal.log("[V8NAV] "+str(s))
try:
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("map load failed")
    actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors=actor_sub.get_all_level_actors()
    recasts=[a for a in actors if a.get_class().get_name()=="RecastNavMesh"]
    log("recasts_before="+str(len(recasts)))
    if recasts:
        nav=recasts[0]
    else:
        nav=actor_sub.spawn_actor_from_class(unreal.RecastNavMesh,unreal.Vector(0,0,0),unreal.Rotator())
        nav.set_actor_label("RecastNavMesh-Default")
        nav.set_folder_path("SpandauStrike_V8/Gameplay")
        log("spawned="+str(nav))
    try: nav.set_editor_property("is_spatially_loaded",False)
    except Exception as e: log("spatial warning "+str(e))
    world=unreal.EditorLevelLibrary.get_editor_world()
    unreal.SystemLibrary.execute_console_command(world,"RebuildNavigation")
    if not sub.save_current_level(): raise RuntimeError("save failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    actors=actor_sub.get_all_level_actors()
    log("recasts_after="+str(len([a for a in actors if a.get_class().get_name()=="RecastNavMesh"])))
    log("READY")
except Exception as e:
    unreal.log_error("[V8NAV] FAILED "+str(e))
    unreal.log_error(traceback.format_exc())
    raise
