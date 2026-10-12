import unreal, math, traceback

MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld_playable_v8"

# Compact combat sector within real Falkenhagener Feld anchors:
# west/south: Am Bogen, center: Paul-Gerhardt-Ring, east/north: Am Kiesteich / Im Spektefeld.
WEST_CENTER=(-54800, 8648)
EAST_CENTER=(-30061, 48472)
CAPTURE=[
 ("SS_ControlPoint_A",-50000,24500,500),  # Paul-Gerhardt-Ring south edge
 ("SS_ControlPoint_B",-40500,35500,500),  # connector / central neighborhood
 ("SS_ControlPoint_C",-31000,47500,500),  # Am Kiesteich
]
STARTS=[
 (-59000,  6500,500),(-56500,  9000,500),(-59000, 12000,500),(-55000, 13500,500),
 (-26000, 50000,500),(-29000, 52500,500),(-24500, 46000,500),(-31500, 50000,500)
]

def log(s): unreal.log("[V8COMPACT] "+str(s))
try:
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("map load failed")
    actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors=actor_sub.get_all_level_actors()
    starts=[a for a in actors if a.get_class().get_name()=="LyraPlayerStart"]
    starts.sort(key=lambda a:a.get_actor_label())
    if len(starts)<8: raise RuntimeError("need 8 starts")
    for i,a in enumerate(starts[:8]):
        x,y,z=STARTS[i]
        a.set_actor_location(unreal.Vector(x,y,z),False,False)
        target=EAST_CENTER if i<4 else WEST_CENTER
        yaw=math.degrees(math.atan2(target[1]-y,target[0]-x))
        a.set_actor_rotation(unreal.Rotator(0,0,yaw),False)
        a.set_actor_label(("SS_WestSpawn_" if i<4 else "SS_EastSpawn_")+("%02d"%((i%4)+1)))
        log("spawn "+a.get_actor_label()+" "+str(a.get_actor_location()))
    cps=[a for a in actors if a.get_actor_label().startswith("SS_ControlPoint_")]
    bylabel={a.get_actor_label():a for a in cps}
    for label,x,y,z in CAPTURE:
        a=bylabel.get(label)
        if not a: raise RuntimeError("missing "+label)
        a.set_actor_location(unreal.Vector(x,y,z),False,False)
        a.set_actor_rotation(unreal.Rotator(),False)
        log("cp "+label+" "+str(a.get_actor_location()))
    world=unreal.EditorLevelLibrary.get_editor_world()
    try: unreal.SystemLibrary.execute_console_command(world,"RebuildNavigation")
    except: pass
    if not sub.save_current_level(): raise RuntimeError("save failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("READY compact sector")
except Exception as e:
    unreal.log_error("[V8COMPACT] FAILED "+str(e))
    unreal.log_error(traceback.format_exc())
    raise
