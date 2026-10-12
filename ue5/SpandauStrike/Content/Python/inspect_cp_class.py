import unreal
path="/ShooterCore/Blueprint/B_ControlPointVolume.B_ControlPointVolume_C"
cls=unreal.load_class(None,path)
unreal.log("[CPCLASS] cls="+str(cls))
if cls:
    obj=unreal.get_default_object(cls)
    names=[n for n in dir(obj) if any(k in n.lower() for k in ("control","point","team","id","name","letter","index","capture","score"))]
    unreal.log("[CPCLASS] attrs="+",".join(sorted(names)))
    for n in names:
        try: unreal.log("[CPDEFAULT] "+n+"="+str(obj.get_editor_property(n)))
        except: pass
