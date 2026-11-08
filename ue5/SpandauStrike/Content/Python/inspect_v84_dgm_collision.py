import json, os, traceback, unreal
MESH='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v86/SM_RathausSpandau_DGM1_v86_GAMEPLAY1000'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','v84_dgm_collision_asset_inspect.json')
out={'ok':False,'path':MESH,'properties':{},'errors':[]}
try:
 mesh=unreal.load_asset(MESH)
 if not mesh: raise RuntimeError('Missing DGM static mesh')
 body=mesh.get_editor_property('body_setup')
 if not body: raise RuntimeError('Missing BodySetup')
 for prop in ('collision_trace_flag','double_sided_geometry','generate_mirrored_collision','generate_non_mirrored_collision'):
  try: out['properties'][prop]=str(body.get_editor_property(prop))
  except Exception as exc: out['properties'][prop+'_error']=str(exc)
 out['ok']=True
except Exception as exc:
 out['errors']=[str(exc),traceback.format_exc()]
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf8') as f: json.dump(out,f,indent=2)
print('DGM_COLLISION_INSPECT='+json.dumps(out))
if not out['ok']: raise RuntimeError('DGM collision inspect failed')
