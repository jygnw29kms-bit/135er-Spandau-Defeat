import unreal, collections
reg=unreal.AssetRegistryHelpers.get_asset_registry()
root="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld"
assets=reg.get_assets_by_path(root,recursive=True)
counts=collections.Counter()
targets=[]
for a in assets:
    lab=str(a.get_tag_value("ActorLabel") or "")
    if lab.startswith("BLN_"): counts["BLN"]+=1
    elif lab.startswith("GIS_Road_"): counts["ROAD"]+=1
    elif lab.startswith("GIS_Water_"): counts["WATER"]+=1
    elif lab.startswith("SS_DGM"): counts["DGM"]+=1
    elif lab.startswith("SS_Exact"): counts["EXACT"]+=1
    else: counts["OTHER"]+=1
    if lab=="SS_ExactBuildings" or (lab.startswith("BLN_") and not any(x[0]=="BLN" for x in targets)):
        targets.append(("EXACT" if lab=="SS_ExactBuildings" else "BLN",a))
unreal.log("[EXACTCHK] counts="+str(dict(counts)))
for kind,a in targets:
    obj=a.get_asset()
    unreal.log("[EXACTCHK] %s pkg=%s asset=%s obj=%s"%(kind,a.package_name,a.asset_name,obj))
    try:
        smc=obj.static_mesh_component
        mesh=smc.static_mesh
        unreal.log("[EXACTCHK] %s mesh=%s scale=%s loc=%s"%(kind,mesh.get_path_name() if mesh else None,obj.get_actor_scale3d(),obj.get_actor_location()))
        unreal.log("[EXACTCHK] %s mats=%s"%(kind,[smc.get_material(i).get_path_name() if smc.get_material(i) else None for i in range(smc.get_num_materials())]))
    except Exception as e: unreal.log_warning("[EXACTCHK] inspect fail "+str(e))
