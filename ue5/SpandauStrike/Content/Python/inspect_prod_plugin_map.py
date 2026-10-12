import unreal
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld_prod_v2"
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.load_level(MAP): raise RuntimeError("load failed")
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
unreal.log("[PRODINSPECT] count=%d"%len(actors))
for a in actors:
    lab=a.get_actor_label()
    cls=a.get_class().get_name()
    mesh=""
    try:
        m=a.static_mesh_component.static_mesh
        if m: mesh=m.get_path_name()
    except: pass
    unreal.log("[PRODINSPECT] %s | %s | %s"%(lab,cls,mesh))
