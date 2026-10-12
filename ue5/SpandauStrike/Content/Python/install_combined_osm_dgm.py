import unreal, traceback

BASE=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\DerivedData\DGM1_FalkenhagenerFeld\OSM_Combined"
ROAD_OBJ=BASE+r"\falkenhagener_roads_dgm.obj"
WATER_OBJ=BASE+r"\falkenhagener_water_dgm.obj"
DEST="/ShooterMaps/Maps/SpandauStrikeGIS/Assets"
ROAD_ASSET=DEST+"/SM_Falkenhagener_Roads_DGM"
WATER_ASSET=DEST+"/SM_Falkenhagener_Water_DGM"
ROAD_MAT=DEST+"/M_Falkenhagener_Road"
WATER_MAT=DEST+"/M_Falkenhagener_Water"
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
EXT="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld"

def log(s): unreal.log("[OSMINSTALL] "+str(s))

def rebuild_mat(path,rgb,rough,metal=0.0):
    mat=unreal.EditorAssetLibrary.load_asset(path)
    if not mat: raise RuntimeError("missing "+path)
    try: unreal.MaterialEditingLibrary.delete_all_material_expressions(mat)
    except: pass
    c=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-300,0)
    c.constant=unreal.LinearColor(*rgb,1.0)
    unreal.MaterialEditingLibrary.connect_material_property(c,"",unreal.MaterialProperty.MP_BASE_COLOR)
    r=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant,-300,180)
    r.r=rough
    unreal.MaterialEditingLibrary.connect_material_property(r,"",unreal.MaterialProperty.MP_ROUGHNESS)
    m=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant,-300,320)
    m.r=metal
    unreal.MaterialEditingLibrary.connect_material_property(m,"",unreal.MaterialProperty.MP_METALLIC)
    unreal.MaterialEditingLibrary.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    return mat
def import_mesh(src,name,mat):
    task=unreal.AssetImportTask()
    task.filename=src
    task.destination_path=DEST
    task.destination_name=name
    task.automated=True
    task.replace_existing=True
    task.replace_existing_settings=True
    task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    mesh=unreal.EditorAssetLibrary.load_asset(DEST+"/"+name)
    if not mesh: raise RuntimeError("mesh import failed "+name)
    mesh.set_material(0,mat)
    try:
        bs=mesh.get_editor_property("body_setup")
        if bs: bs.set_editor_property("collision_trace_flag",unreal.CollisionTraceFlag.CTF_USE_DEFAULT)
    except: pass
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    log(name+" imported")
    return mesh

def disable_old():
    reg=unreal.AssetRegistryHelpers.get_asset_registry()
    changed=0
    for a in reg.get_assets_by_path(EXT,recursive=True):
        lab=str(a.get_tag_value("ActorLabel") or "")
        if not (lab.startswith("GIS_Road_") or lab.startswith("GIS_Water_")): continue
        obj=a.get_asset()
        if not obj: continue
        try:
            obj.set_actor_hidden_in_game(True)
            c=obj.static_mesh_component
            c.set_visibility(False,True)
            c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            c.set_collision_profile_name("NoCollision")
            obj.modify(); c.modify(); changed+=1
        except Exception as e:
            unreal.log_warning("[OSMINSTALL] old actor warning "+lab+" "+str(e))
        if changed and changed%1000==0:
            unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
            log("disabled "+str(changed))
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    return changed
def spawn_combined(roadmesh,watermesh,roadmat,watermat):
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("map load failed")
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        if a.get_actor_label() in ("SS_GIS_Roads_DGM","SS_GIS_Water_DGM"):
            unreal.EditorLevelLibrary.destroy_actor(a)
    specs=[
      ("SS_GIS_Roads_DGM",roadmesh,roadmat,"SpandauStrike_GIS/Roads"),
      ("SS_GIS_Water_DGM",watermesh,watermat,"SpandauStrike_GIS/Water")
    ]
    for label,mesh,mat,folder in specs:
        a=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0),unreal.Rotator())
        a.set_actor_label(label); a.set_folder_path(folder)
        c=a.static_mesh_component; c.set_static_mesh(mesh); c.set_material(0,mat)
        c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        c.set_collision_profile_name("NoCollision")
        log("spawned "+label)
    if not sub.save_current_level(): raise RuntimeError("level save failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)

def main():
    roadmat=rebuild_mat(ROAD_MAT,(0.035,0.04,0.045),0.92)
    watermat=rebuild_mat(WATER_MAT,(0.018,0.10,0.18),0.24)
    road=import_mesh(ROAD_OBJ,"SM_Falkenhagener_Roads_DGM",roadmat)
    water=import_mesh(WATER_OBJ,"SM_Falkenhagener_Water_DGM",watermat)
    old=disable_old()
    log("old overlays disabled="+str(old))
    spawn_combined(road,water,roadmat,watermat)
    log("OSMINSTALL_READY")

if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[OSMINSTALL] FAILED "+str(e)); unreal.log_error(traceback.format_exc()); raise
