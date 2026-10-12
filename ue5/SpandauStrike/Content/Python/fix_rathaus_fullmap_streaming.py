import unreal, traceback
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_fullmap_v1"
def log(s): unreal.log("[RATHAUS_FULLMAP_STREAM] "+str(s))
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError("map load failed")
    sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    found=[]
    for a in sub.get_all_level_actors():
        label=a.get_actor_label()
        if label in ("RathausFull_Visible","RathausFull_Collision"):
            try:a.set_editor_property("is_spatially_loaded",False)
            except Exception as e:log("spatial note "+label+" "+str(e))
            if hasattr(a,"static_mesh_component"):
                c=a.static_mesh_component
                if label=="RathausFull_Visible":
                    c.set_editor_property("visible",True)
                    try:c.set_editor_property("hidden_in_game",False)
                    except:pass
                    c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
                    try:c.set_editor_property("can_ever_affect_navigation",False)
                    except:pass
                else:
                    c.set_editor_property("visible",False)
                    try:c.set_editor_property("hidden_in_game",True)
                    except:pass
                    c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
                    c.set_collision_profile_name("BlockAll")
                    try:c.set_editor_property("can_ever_affect_navigation",True)
                    except:pass
            a.modify()
            found.append(label)
    log("FOUND="+str(found))
    if len(found)!=2: raise RuntimeError("expected both map actors")
    if not lvl.save_current_level():raise RuntimeError("save failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("READY")
except Exception as e:
    unreal.log_error("[RATHAUS_FULLMAP_STREAM] FAILED "+str(e))
    unreal.log_error(traceback.format_exc())
    raise
