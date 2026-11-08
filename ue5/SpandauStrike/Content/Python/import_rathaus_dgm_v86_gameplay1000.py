import json, os, traceback, unreal
SRC=r'C:\Users\anony\Documents\SpandauStrike\SourceData\DGM1\rathaus_dgm_gameplay1000_1000m_513.obj'
DEST='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v86'
NAME='SM_RathausSpandau_DGM1_v86_GAMEPLAY1000'
REP=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_dgm_v86_import.json')
out={'ok':False,'errors':[]}
try:
    task=unreal.AssetImportTask()
    task.filename=SRC
    task.destination_path=DEST
    task.destination_name=NAME
    task.automated=True
    task.replace_existing=True
    task.replace_existing_settings=True
    task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    paths=[str(x) for x in task.imported_object_paths]
    out['imported_paths']=paths
    if not paths: raise RuntimeError('v86 import produced no assets')
    mesh=unreal.load_asset(paths[0])
    if not mesh: raise RuntimeError('v86 mesh load failed')
    b=mesh.get_bounds()
    out['mesh']=mesh.get_path_name()
    out['bounds_origin']=[b.origin.x,b.origin.y,b.origin.z]
    out['bounds_extent']=[b.box_extent.x,b.box_extent.y,b.box_extent.z]
    out['radius']=b.sphere_radius
    unreal.EditorAssetLibrary.save_loaded_asset(mesh,False)
    out['ok']=True
except Exception as e:
    out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REP),exist_ok=True)
with open(REP,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
