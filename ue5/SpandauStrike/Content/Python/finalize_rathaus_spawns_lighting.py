import unreal, math, traceback
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1"
CENTER=(10085.0,289.6,1500.0)
SP=[
(3803.4,-3969.7,177.0),(4830.9,-5259.7,294.0),(6101.6,-6232.1,294.0),(7615.3,-6886.8,294.0),
(12554.7,7466.0,160.0),(14068.4,6811.3,160.0),(15339.1,5838.9,160.0),(16366.6,4548.9,151.0)]
def log(s):unreal.log("[RATHAUS_FINAL_GAMEPLAY] "+str(s))
try:
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP):raise RuntimeError("map load failed")
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors=eas.get_all_level_actors()
    starts=sorted([a for a in actors if a.get_class().get_name()=="LyraPlayerStart"],key=lambda x:x.get_actor_label())
    for a,xyz in zip(starts,SP):
        a.set_actor_location(unreal.Vector(*xyz),False,False)
        yaw=math.degrees(math.atan2(CENTER[1]-xyz[1],CENTER[0]-xyz[0]))
        a.set_actor_rotation(unreal.Rotator(0,yaw,0),False)
        try:a.set_editor_property("is_spatially_loaded",False)
        except:pass
        log("SPAWN "+a.get_actor_label()+" "+str(xyz)+" yaw="+str(round(yaw,1)))
    for a in actors:
        cn=a.get_class().get_name()
        if cn=="PostProcessVolume":
            s=a.get_editor_property("settings")
            try:s.set_editor_property("auto_exposure_bias",0.0);s.set_editor_property("override_auto_exposure_bias",True)
            except:pass
            a.set_editor_property("settings",s)
        elif cn=="ExponentialHeightFog":
            try:
                c=a.component;c.set_editor_property("fog_density",0.00025);c.set_editor_property("fog_height_falloff",0.15);c.set_editor_property("start_distance",10000.0)
            except Exception as e:log("FOG "+str(e))
        elif cn=="DirectionalLight":
            try:a.light_component.set_editor_property("intensity",3.5)
            except:pass
        elif cn=="SkyLight":
            try:a.light_component.set_editor_property("intensity",1.0);a.light_component.set_editor_property("real_time_capture",True)
            except:pass
    if not sub.save_current_level():raise RuntimeError("save failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("READY")
except Exception as e:
    unreal.log_error("[RATHAUS_FINAL_GAMEPLAY] FAILED "+str(e));unreal.log_error(traceback.format_exc());raise
