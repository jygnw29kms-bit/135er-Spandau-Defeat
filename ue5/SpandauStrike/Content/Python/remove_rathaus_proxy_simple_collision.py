import unreal, os, json, traceback
ASSET='/Game/SpandauStrike/Maps/Rathaus/Navigation/REAL_v73/SM_RathausSpandau_NAV_PROXY_v73'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_proxy_remove_simple_collision_2026-10-12.json')
out={'ok':False,'errors':[]}
try:
    sm=unreal.load_asset(ASSET)
    if not sm: raise RuntimeError('proxy asset load failed')
    sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    bs=sm.get_editor_property('body_setup')
    agg=bs.get_editor_property('agg_geom')
    out['before']={
      'trace_flag':str(bs.get_editor_property('collision_trace_flag')),
      'simple_count':int(sub.get_simple_collision_count(sm)),
      'convex_count':len(agg.get_editor_property('convex_elems')),
    }
    sub.remove_collisions(sm)
    bs=sm.get_editor_property('body_setup')
    bs.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    sm.modify()
    if not unreal.EditorAssetLibrary.save_loaded_asset(sm): raise RuntimeError('save proxy failed')
    bs=sm.get_editor_property('body_setup'); agg=bs.get_editor_property('agg_geom')
    out['after']={
      'trace_flag':str(bs.get_editor_property('collision_trace_flag')),
      'simple_count':int(sub.get_simple_collision_count(sm)),
      'convex_count':len(agg.get_editor_property('convex_elems')),
    }
    out['ok']=out['after']['convex_count']==0 and 'COMPLEX_AS_SIMPLE' in out['after']['trace_flag']
except Exception as e:
    out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
