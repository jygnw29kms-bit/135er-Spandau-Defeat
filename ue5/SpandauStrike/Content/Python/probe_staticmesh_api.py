import unreal
for n in ["StaticMeshEditorSubsystem","EditorStaticMeshLibrary","StaticMeshReductionOptions","StaticMeshReductionSettings"]:
    o=getattr(unreal,n,None)
    unreal.log("[API] "+n+"="+str(o))
    if o:
        unreal.log("[API] "+n+" methods="+",".join(x for x in dir(o) if "lod" in x.lower() or "collision" in x.lower()))
try:
    x=unreal.StaticMeshEditorSubsystem()
    unreal.log("[API] instance="+str(x))
    unreal.log("[API] inst_methods="+",".join(y for y in dir(x) if "lod" in y.lower() or "collision" in y.lower()))
except Exception as e:
    unreal.log_error("[API] instantiate failed "+str(e))
