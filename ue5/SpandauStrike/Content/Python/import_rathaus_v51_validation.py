import unreal, os
PROJECT_DIR=os.path.normpath(unreal.Paths.project_dir())
FBX=os.path.join(PROJECT_DIR,'SourceArt','Rathaus','v51','RathausSpandau_BUILDING_v51.fbx')
DEST='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v51'
NAME='SM_RathausSpandau_BUILDING_v51'
OUT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v51_import_validation.txt')
if not os.path.isfile(FBX): raise RuntimeError('FBX missing '+FBX)
asset_path=DEST+'/'+NAME
if unreal.EditorAssetLibrary.does_asset_exist(asset_path): unreal.EditorAssetLibrary.delete_asset(asset_path)
task=unreal.AssetImportTask(); task.filename=FBX; task.destination_path=DEST; task.destination_name=NAME; task.automated=True; task.replace_existing=True; task.save=True
ui=unreal.FbxImportUI(); ui.import_mesh=True; ui.import_materials=False; ui.import_textures=False; ui.import_as_skeletal=False
try: ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
except Exception: pass
smi=ui.static_mesh_import_data
for prop,val in [('combine_meshes',True),('generate_lightmap_u_vs',False),('auto_generate_collision',False),('convert_scene',True),('convert_scene_unit',True)]:
    try: smi.set_editor_property(prop,val)
    except Exception: pass
task.options=ui
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
sm=unreal.load_asset(asset_path)
if not sm: raise RuntimeError('import did not create '+asset_path)
b=sm.get_bounds(); slots=len(sm.get_editor_property('static_materials'))
lines=['IMPORTED='+asset_path,'BOUNDS='+str(b),'ORIGIN='+str(b.origin),'BOX_EXTENT='+str(b.box_extent),'MATERIALS='+str(slots)]
os.makedirs(os.path.dirname(OUT),exist_ok=True); open(OUT,'w',encoding='utf-8').write('\n'.join(lines))
if slots != 34: raise RuntimeError('expected 34 material slots, got '+str(slots))
