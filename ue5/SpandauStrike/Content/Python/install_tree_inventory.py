import unreal, traceback

MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
DEST="/ShooterMaps/GeneratedGIS/FalkenhagenerFeld"
MAT_DEST="/Game/SpandauStrikeGIS/Materials"
FILES={
 "SS_TreeTrunks": r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\FalkenhagenerFeld_TreeTrunks.obj",
 "SS_TreeBroadleaf": r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\FalkenhagenerFeld_TreeBroadleaf.obj",
 "SS_TreeConifer": r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\FalkenhagenerFeld_TreeConifer.obj"
}
COLORS={
 "M_SS_TreeTrunk": unreal.LinearColor(0.18,0.095,0.045,1),
 "M_SS_TreeBroadleaf": unreal.LinearColor(0.075,0.23,0.06,1),
 "M_SS_TreeConifer": unreal.LinearColor(0.035,0.13,0.065,1)
}

def log(s): unreal.log("[TREE_GIS] "+str(s))

def make_mat(name,color):
    path=MAT_DEST+"/"+name
    old=unreal.EditorAssetLibrary.load_asset(path+"."+name)
    if old: return old
    tools=unreal.AssetToolsHelpers.get_asset_tools()
    mat=tools.create_asset(name,MAT_DEST,unreal.Material,unreal.MaterialFactoryNew())
    base=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-300,0)
    base.set_editor_property("constant",color)
    unreal.MaterialEditingLibrary.connect_material_property(base,"",unreal.MaterialProperty.MP_BASE_COLOR)
    rough=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant,-300,120)
    rough.set_editor_property("r",0.82)
    unreal.MaterialEditingLibrary.connect_material_property(rough,"",unreal.MaterialProperty.MP_ROUGHNESS)
    unreal.MaterialEditingLibrary.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    return mat
def import_obj(name,filename):
    task=unreal.AssetImportTask()
    task.filename=filename
    task.destination_path=DEST
    task.destination_name="SM_"+name
    task.automated=True
    task.replace_existing=True
    task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    log(name+" imported="+str(task.imported_object_paths))
    for p in task.imported_object_paths:
        a=unreal.EditorAssetLibrary.load_asset(p)
        if isinstance(a,unreal.StaticMesh): return a
    raise RuntimeError("No StaticMesh for "+name)

def main():
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("map load failed")
    mats={
      "SS_TreeTrunks":make_mat("M_SS_TreeTrunk",COLORS["M_SS_TreeTrunk"]),
      "SS_TreeBroadleaf":make_mat("M_SS_TreeBroadleaf",COLORS["M_SS_TreeBroadleaf"]),
      "SS_TreeConifer":make_mat("M_SS_TreeConifer",COLORS["M_SS_TreeConifer"])
    }
    meshes={k:import_obj(k,v) for k,v in FILES.items()}
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in actors.get_all_level_actors():
        if a.get_actor_label() in FILES:
            actors.destroy_actor(a)
    for name,mesh in meshes.items():
        a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0),unreal.Rotator())
        a.static_mesh_component.set_static_mesh(mesh)
        a.static_mesh_component.set_material(0,mats[name])
        a.static_mesh_component.set_collision_profile_name("NoCollision")
        a.set_actor_label(name)
        a.set_folder_path("SpandauStrike_GIS/Vegetation")
        log(name+" actor ready")
    if not sub.save_current_level(): raise RuntimeError("map save failed")
    log("TREE_INVENTORY_READY actors=3 trees=6498")

if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[TREE_GIS] FAILED "+str(e))
        unreal.log_error(traceback.format_exc())
        raise
