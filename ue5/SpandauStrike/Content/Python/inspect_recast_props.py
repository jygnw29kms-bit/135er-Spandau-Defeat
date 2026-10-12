import unreal
for n in sorted(dir(unreal.RecastNavMesh)):
    if any(k in n.lower() for k in ("partition","runtime","generation","rebuild","main_nav","nav_data")):
        unreal.log("[RECASTPROP] "+n)
