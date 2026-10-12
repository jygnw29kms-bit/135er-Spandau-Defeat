import unreal
EXT="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld"
reg=unreal.AssetRegistryHelpers.get_asset_registry()
for a in reg.get_assets_by_path(EXT,recursive=True):
    lab=str(a.get_tag_value("ActorLabel") or "")
    if not (lab.startswith("SS_DGM") or lab.startswith("GIS_DGM")):
        continue
    obj=a.get_asset()
    mesh=""
    try:
        sm=obj.static_mesh_component.get_editor_property("static_mesh")
        mesh=sm.get_path_name() if sm else "NONE"
    except Exception as e:
        mesh="ERR "+str(e)
    unreal.log("[DGMDET] label="+lab+" pkg="+str(a.package_name)+" mesh="+mesh+" loc="+str(obj.get_actor_location())+" rot="+str(obj.get_actor_rotation())+" scale="+str(obj.get_actor_scale3d()))
