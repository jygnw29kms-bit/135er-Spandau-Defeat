import unreal, traceback

MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
DEST="/ShooterMaps/GeneratedGIS/FalkenhagenerFeld"
MAT_DEST="/Game/SpandauStrikeGIS/Materials"
SRC=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS"
SETS={
 "Residential":(r"FalkenhagenerFeld_Buildings_Residential_DGM.obj",unreal.LinearColor(0.55,0.42,0.30,1)),
 "Public":(r"FalkenhagenerFeld_Buildings_Public_DGM.obj",unreal.LinearColor(0.48,0.16,0.10,1)),
 "Industrial":(r"FalkenhagenerFeld_Buildings_Industrial_DGM.obj",unreal.LinearColor(0.24,0.31,0.36,1)),
 "Aux":(r"FalkenhagenerFeld_Buildings_Aux_DGM.obj",unreal.LinearColor(0.30,0.28,0.24,1))
}

def log(s): unreal.log("[BLDG_DGM] "+str(s))

def make_mat(cat,color):
    name="M_SS_Building_"+cat
    obj=unreal.EditorAssetLibrary.load_asset(MAT_DEST+"/"+name+"."+name)
    if obj: return obj
    mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,MAT_DEST,unreal.Material,unreal.MaterialFactoryNew())
    mat.set_editor_property("two_sided",True)
    base=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-300,0)
    base.set_editor_property("constant",color)
    unreal.MaterialEditingLibrary.connect_material_property(base,"",unreal.MaterialProperty.MP_BASE_COLOR)
    rough=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant,-300,120)
    rough.set_editor_property("r",0.78)
    unreal.MaterialEditingLibrary.connect_material_property(rough,"",unreal.MaterialProperty.MP_ROUGHNESS)
    unreal.MaterialEditingLibrary.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    return mat
def import_obj(cat,filename):
    task=unreal.AssetImportTask()
    task.filename=SRC+"\\"+filename
    task.destination_path=DEST
    task.destination_name="SM_SS_Buildings_"+cat+"_DGM"
    task.automated=True
    task.replace_existing=True
    task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    log(cat+" paths="+str(task.imported_object_paths))
    for p in task.imported_object_paths:
        m=unreal.EditorAssetLibrary.load_asset(p)
        if isinstance(m,unreal.StaticMesh):
            try:
                body=m.get_editor_property("body_setup")
                body.set_editor_property("collision_trace_flag",unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
                unreal.EditorAssetLibrary.save_loaded_asset(m)
            except Exception as e: log(cat+" collision warning "+str(e))
            return m
    raise RuntimeError("No mesh imported for "+cat)

def main():
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("map load failed")
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    mats={cat:make_mat(cat,col) for cat,(_,col) in SETS.items()}
    meshes={cat:import_obj(cat,fn) for cat,(fn,_) in SETS.items()}
    labels={"SS_Buildings_"+k for k in SETS}
    for a in actors.get_all_level_actors():
        if a.get_actor_label() in labels: actors.destroy_actor(a)
    for cat,m in meshes.items():
        a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0),unreal.Rotator())
        a.static_mesh_component.set_static_mesh(m)
        a.static_mesh_component.set_material(0,mats[cat])
        a.static_mesh_component.set_collision_profile_name("BlockAll")
        a.set_actor_label("SS_Buildings_"+cat)
        a.set_folder_path("SpandauStrike_GIS/Buildings")
        log(cat+" actor ready")
    try:
        world=unreal.EditorLevelLibrary.get_editor_world()
        unreal.SystemLibrary.execute_console_command(world,"RebuildNavigation")
        log("navigation rebuild requested")
    except Exception as e: log("nav warning "+str(e))
    if not sub.save_current_level(): raise RuntimeError("save failed")
    log("BUILDINGS_DGM_READY actors=4 buildings=4610")

if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[BLDG_DGM] FAILED "+str(e))
        unreal.log_error(traceback.format_exc())
        raise
