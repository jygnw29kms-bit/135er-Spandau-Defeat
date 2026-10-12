import unreal, os, traceback
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1"
GEN="/ShooterMaps/GeneratedGIS/RathausSpandauFinal"
FBX=r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final\engine\RathausSpandau_Landmark_LOD0.fbx"
BLDG=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\RathausSpandau_v1\rathaus_buildings_no_landmark.obj"
def log(s): unreal.log("[RATHAUS_FINAL] "+str(s))
def import_fbx():
    task=unreal.AssetImportTask();task.filename=FBX;task.destination_path=GEN;task.destination_name="SM_Rathaus_Landmark_Final"
    task.automated=True;task.replace_existing=True;task.replace_existing_settings=True;task.save=True
    opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_as_skeletal=False
    opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
    opt.import_materials=True;opt.import_textures=False
    sm=opt.static_mesh_import_data;sm.combine_meshes=True;sm.generate_lightmap_u_vs=True;sm.auto_generate_collision=False
    task.options=opt;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    a=unreal.EditorAssetLibrary.load_asset(GEN+"/SM_Rathaus_Landmark_Final")
    if not a: raise RuntimeError("Landmark FBX import failed")
    return a

def import_buildings():
    task=unreal.AssetImportTask();task.filename=BLDG;task.destination_path=GEN;task.destination_name="SM_Rathaus_Buildings_NoLandmark"
    task.automated=True;task.replace_existing=True;task.replace_existing_settings=True;task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    a=unreal.EditorAssetLibrary.load_asset(GEN+"/SM_Rathaus_Buildings_NoLandmark")
    if not a: raise RuntimeError("filtered buildings import failed")
    return a
def complex_collision(mesh):
    bs=mesh.get_editor_property("body_setup")
    if not bs:
        try: unreal.StaticMeshEditorSubsystem().add_simple_collisions(mesh,unreal.ScriptingCollisionShapeType.BOX)
        except: pass
        bs=mesh.get_editor_property("body_setup")
    if bs:
        bs.set_editor_property("collision_trace_flag",unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh,False)

def main():
    log("importing landmark")
    landmark=import_fbx()
    buildings=import_buildings()
    complex_collision(landmark);complex_collision(buildings)
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("map load failed")
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    old=None
    for a in actors.get_all_level_actors():
        if a.get_actor_label()=="Rathaus_ExactBuildings": old=a
        if a.get_actor_label()=="Rathaus_Landmark_Final": actors.destroy_actor(a)
    if old:
        old.static_mesh_component.set_static_mesh(buildings)
        old.set_actor_label("Rathaus_Buildings_NoLandmark")
        log("filtered GIS buildings applied")
    else:
        log("WARNING old building actor not found")
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0),unreal.Rotator(0,0,0))
    a.set_actor_label("Rathaus_Landmark_Final");a.set_folder_path("Rathaus_Final/Landmark")
    a.static_mesh_component.set_static_mesh(landmark)
    a.static_mesh_component.set_collision_profile_name("BlockAll")
    a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    try:a.set_editor_property("is_spatially_loaded",False)
    except:pass

    if not sub.save_current_level():raise RuntimeError("level save failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("READY mesh="+landmark.get_name()+" actors="+str(len(actors.get_all_level_actors())))
if __name__=="__main__":
    try:main()
    except Exception as e:
        unreal.log_error("[RATHAUS_FINAL] FAILED "+str(e))
        unreal.log_error(traceback.format_exc())
        raise

