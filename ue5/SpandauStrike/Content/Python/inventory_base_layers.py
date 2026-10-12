import unreal,collections
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.load_level(MAP): raise RuntimeError("load failed")
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
all=actors.get_all_level_actors()
unreal.log("[LAYERS] count=%d"%len(all))
for a in all:
    try:
        comp=a.static_mesh_component
    except: continue
    if not comp: continue
    mesh=comp.static_mesh
    if not mesh: continue
    try: spatial=a.get_editor_property("is_spatially_loaded")
    except: spatial="?"
    unreal.log("[LAYERS] label=%s mesh=%s loc=%s spatial=%s coll=%s"%(a.get_actor_label(),mesh.get_path_name(),a.get_actor_location(),spatial,comp.get_collision_profile_name()))
