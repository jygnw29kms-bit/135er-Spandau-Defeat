import unreal, traceback
FBX=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\RathausSpandau_v1\rathaus_buildings_no_landmark_correct.fbx"
GEN="/ShooterMaps/GeneratedGIS/RathausSpandau";NAME="SM_Rathaus_Buildings"
def log(s):unreal.log("[RATHAUS_CORRECT_OVERWRITE] "+str(s))
try:
 task=unreal.AssetImportTask();task.filename=FBX;task.destination_path=GEN;task.destination_name=NAME
 task.automated=True;task.replace_existing=True;task.replace_existing_settings=True;task.save=True
 opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_as_skeletal=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
 opt.import_materials=False;opt.import_textures=False;opt.static_mesh_import_data.combine_meshes=True;opt.static_mesh_import_data.generate_lightmap_u_vs=True
 task.options=opt;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
 mesh=unreal.load_asset(GEN+"/"+NAME)
 if not mesh:raise RuntimeError("mesh load failed")
 bs=mesh.get_editor_property("body_setup")
 if bs:bs.set_editor_property("collision_trace_flag",unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 unreal.EditorAssetLibrary.save_loaded_asset(mesh,False)
 log("BOUNDS "+str(mesh.get_bounding_box()));log("READY")
except Exception as e:
 unreal.log_error("[RATHAUS_CORRECT_OVERWRITE] FAILED "+str(e));unreal.log_error(traceback.format_exc());raise
