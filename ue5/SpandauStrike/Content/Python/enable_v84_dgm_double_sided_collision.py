import json, os, traceback, unreal
MESH='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v86/SM_RathausSpandau_DGM1_v86_GAMEPLAY1000'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','v84_dgm_double_sided_apply.json')
out={'ok':False,'mesh':MESH,'errors':[]}
try:
 mesh=unreal.load_asset(MESH)
 if not mesh: raise RuntimeError('DGM asset missing')
 body=mesh.get_editor_property('body_setup')
 if not body: raise RuntimeError('DGM BodySetup missing')
 out['previous_double_sided']=bool(body.get_editor_property('double_sided_geometry'))
 body.set_editor_property('double_sided_geometry',True)
 body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 mesh.modify()
 if not unreal.EditorAssetLibrary.save_loaded_asset(mesh,False): raise RuntimeError('Save failed')
 out['double_sided']=bool(body.get_editor_property('double_sided_geometry'))
 out['ok']=out['double_sided']
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf8') as f: json.dump(out,f,indent=2)
print('DGM_DOUBLE_SIDED='+json.dumps(out))
if not out['ok']: raise RuntimeError('Could not enable double sided DGM collision')
