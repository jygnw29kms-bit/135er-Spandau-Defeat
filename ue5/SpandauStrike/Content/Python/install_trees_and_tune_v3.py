import unreal, os, traceback

MAP="/Game/Maps/BerlinSpandau/falkenhagener_feld_prod_v3"
DEST="/Game/SpandauStrikeGIS/Combined"
MATROOT="/Game/SpandauStrikeGIS/Materials"
BASE=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\DerivedData\Trees_FalkenhagenerFeld"
TRUNK_OBJ=os.path.join(BASE,"falkenhagener_tree_trunks.obj")
CROWN_OBJ=os.path.join(BASE,"falkenhagener_tree_crowns.obj")

def log(s): unreal.log("[SS_V3VIS] "+str(s))

def material(name,rgb,rough):
    path=MATROOT+"/"+name
    mat=unreal.EditorAssetLibrary.load_asset(path)
    if not mat:
        mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name,MATROOT,unreal.Material,unreal.MaterialFactoryNew())
    if not mat: raise RuntimeError("material failed "+name)
    try: unreal.MaterialEditingLibrary.delete_all_material_expressions(mat)
    except: pass
    c=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-300,0)
    c.constant=unreal.LinearColor(*rgb,1.0)
    unreal.MaterialEditingLibrary.connect_material_property(c,"",unreal.MaterialProperty.MP_BASE_COLOR)
    r=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant,-300,160)
    r.r=rough
    unreal.MaterialEditingLibrary.connect_material_property(r,"",unreal.MaterialProperty.MP_ROUGHNESS)
    unreal.MaterialEditingLibrary.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    return mat
def import_obj(src,name,mat):
    task=unreal.AssetImportTask()
    task.filename=src; task.destination_path=DEST; task.destination_name=name
    task.automated=True; task.replace_existing=True; task.replace_existing_settings=True; task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    p=list(task.imported_object_paths)
    if not p: raise RuntimeError("import failed "+name)
    m=unreal.EditorAssetLibrary.load_asset(p[0])
    if not m: raise RuntimeError("load failed "+name)
    m.set_material(0,mat)
    unreal.EditorAssetLibrary.save_loaded_asset(m)
    return m

def spawn(mesh,mat,label,folder):
    a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(
        unreal.StaticMeshActor,unreal.Vector(),unreal.Rotator())
    a.set_actor_label(label); a.set_folder_path(folder)
    c=a.static_mesh_component; c.set_static_mesh(mesh); c.set_material(0,mat)
    c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    c.set_collision_profile_name("NoCollision")
    return a
def main():
    mb=material("M_SS_Building",(0.20,0.18,0.16),0.92)
    mt=material("M_SS_Terrain",(0.08,0.16,0.055),0.96)
    mr=material("M_SS_Road",(0.028,0.032,0.036),0.94)
    mw=material("M_SS_Water",(0.012,0.075,0.14),0.30)
    mtr=material("M_SS_TreeTrunk",(0.11,0.055,0.022),0.96)
    mcr=material("M_SS_TreeCrown",(0.055,0.19,0.035),0.90)
    trunk=import_obj(TRUNK_OBJ,"SM_Falkenhagener_TreeTrunks_V3",mtr)
    crown=import_obj(CROWN_OBJ,"SM_Falkenhagener_TreeCrowns_V3",mcr)

    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("map load failed")
    actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in list(actor_sub.get_all_level_actors()):
        if a.get_actor_label() in ("SS_TreeTrunks","SS_TreeCrowns"):
            actor_sub.destroy_actor(a)
        elif a.get_actor_label()=="Sun":
            try: a.light_component.set_editor_property("intensity",2.0)
            except: pass
    spawn(trunk,mtr,"SS_TreeTrunks","SpandauStrike_PROD_V3/Vegetation")
    spawn(crown,mcr,"SS_TreeCrowns","SpandauStrike_PROD_V3/Vegetation")

    # Rebind shared materials explicitly on combined map actors.
    mats={"SS_ExactBuildings":mb,"DGM1_Terrain_Real":mt,
          "SS_GIS_Roads_DGM":mr,"SS_GIS_Water_DGM":mw}
    for a in actor_sub.get_all_level_actors():
        lab=a.get_actor_label()
        if lab in mats:
            try:
                a.static_mesh_component.set_material(0,mats[lab])
                a.modify(); a.static_mesh_component.modify()
            except: pass
    if not sub.save_current_level(): raise RuntimeError("save failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("READY trees=6493 visuals_tuned")

if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[SS_V3VIS] FAILED "+str(e))
        unreal.log_error(traceback.format_exc())
        raise
