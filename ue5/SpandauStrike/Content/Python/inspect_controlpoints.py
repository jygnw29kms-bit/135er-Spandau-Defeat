import unreal
MAP="/ShooterMaps/Maps/L_Convolution_Blockout"
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.load_level(MAP): raise RuntimeError("load fail")
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
for a in actors:
    cn=a.get_class().get_name()
    if "ControlPoint" in cn or "controlpoint" in cn.lower():
        unreal.log("[CPINSPECT] class="+cn+" label="+a.get_actor_label()+" path="+a.get_path_name())
        unreal.log("[CPINSPECT] loc="+str(a.get_actor_location())+" rot="+str(a.get_actor_rotation())+" scale="+str(a.get_actor_scale3d()))
        names=[n for n in dir(a) if any(k in n.lower() for k in ("control","point","team","id","name","letter","index"))]
        unreal.log("[CPINSPECT] attrs="+",".join(sorted(names)))
        for n in names:
            try:
                v=a.get_editor_property(n)
                unreal.log("[CPPROP] "+n+"="+str(v))
            except: pass
