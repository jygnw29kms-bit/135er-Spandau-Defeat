import unreal, math, traceback

MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld_playable_v8"
CP_CLASS="/ShooterCore/Blueprint/B_ControlPointVolume.B_ControlPointVolume_C"

# Real OSM-derived anchor corridors (cm in local GIS frame)
WEST=[(-54800,8648),(-49184,27817)]          # Am Bogen / Paul-Gerhardt-Ring
CENTER=[(-18000,30000),(-5000,19000)]        # Am Kiesteich / Falkenseer Chaussee corridor
EAST=[(29119,-29714),(52000,-18000)]         # Pionierstrasse corridor

STARTS=[
 (-58500, 10500, 500),(-55500, 14500,500),(-51000, 24000,500),(-53500,30500,500),
 ( 33000,-33000,500),( 39000,-28500,500),( 47500,-21000,500),( 54000,-15000,500)
]
CAPTURE=[
 ("SS_ControlPoint_A",-47000,26000,500),
 ("SS_ControlPoint_B", -8000,20000,500),
 ("SS_ControlPoint_C", 30000,-28500,500),
]

def log(s): unreal.log("[V8GAMEPLAY] "+str(s))

try:
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("map load failed")
    actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors=actor_sub.get_all_level_actors()

    starts=[a for a in actors if a.get_class().get_name()=="LyraPlayerStart"]
    starts.sort(key=lambda a:a.get_actor_label())
    if len(starts)<8: raise RuntimeError("expected 8 LyraPlayerStarts, got %d"%len(starts))
    for i,a in enumerate(starts[:8]):
        x,y,z=STARTS[i]
        a.set_actor_location(unreal.Vector(x,y,z),False,False)
        yaw=math.degrees(math.atan2(-y,-x))
        a.set_actor_rotation(unreal.Rotator(0,0,yaw),False)
        side="West" if i<4 else "East"
        a.set_actor_label("SS_%sSpawn_%02d"%(side,i+1 if i<4 else i-3))
        log("spawn %d -> %.0f %.0f %.0f"%(i+1,x,y,z))

    # Remove earlier V8 test capture actors only.
    for a in list(actor_sub.get_all_level_actors()):
        if a.get_actor_label().startswith("SS_ControlPoint_"):
            actor_sub.destroy_actor(a)

    cp_cls=unreal.load_class(None,CP_CLASS)
    if not cp_cls: raise RuntimeError("control point class unavailable")
    for label,x,y,z in CAPTURE:
        a=actor_sub.spawn_actor_from_class(cp_cls,unreal.Vector(x,y,z),unreal.Rotator())
        a.set_actor_label(label)
        a.set_folder_path("SpandauStrike_V8/Gameplay/ControlPoints")
        try:a.set_editor_property("is_spatially_loaded",False)
        except:pass
        # Preserve Blueprint defaults; modest world scale only if the reference actor uses unit scale.
        log("controlpoint "+label+" class="+a.get_class().get_name()+" loc="+str(a.get_actor_location())+" scale="+str(a.get_actor_scale3d()))

    world=unreal.EditorLevelLibrary.get_editor_world()
    try: unreal.SystemLibrary.execute_console_command(world,"RebuildNavigation")
    except Exception as e: log("nav rebuild command warning "+str(e))
    if not sub.save_current_level(): raise RuntimeError("save failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("READY starts=8 controlpoints=3")
except Exception as e:
    unreal.log_error("[V8GAMEPLAY] FAILED "+str(e))
    unreal.log_error(traceback.format_exc())
    raise
