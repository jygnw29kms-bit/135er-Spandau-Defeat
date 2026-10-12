import unreal
for n in ["HierarchicalInstancedStaticMeshComponent","InstancedStaticMeshComponent","Actor","StaticMeshActor"]:
    unreal.log("[HISM_API] %s=%s"%(n,hasattr(unreal,n)))
for n in sorted(dir(unreal.Actor)):
    if "component" in n.lower(): unreal.log("[HISM_API] Actor."+n)
