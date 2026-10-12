import unreal, json, os
sm=unreal.load_asset('/Game/SpandauStrike/Maps/Rathaus/Navigation/REAL_v73/SM_RathausSpandau_NAV_PROXY_v73')
sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
bs=sm.get_editor_property('body_setup')
out={
 'subsystem_methods':[x for x in dir(sub) if 'collision' in x.lower() or 'simple' in x.lower()],
 'body_methods':[x for x in dir(bs) if 'collision' in x.lower() or 'physics' in x.lower() or 'agg' in x.lower()],
 'mesh_methods':[x for x in dir(sm) if 'collision' in x.lower() or 'body' in x.lower()],
 'trace_flag':str(bs.get_editor_property('collision_trace_flag')),
}
agg=bs.get_editor_property('agg_geom')
for prop in ['box_elems','sphere_elems','sphyl_elems','convex_elems','tapered_capsule_elems']:
 try: out[prop]=len(agg.get_editor_property(prop))
 except Exception as e: out[prop+'_error']=str(e)
report=os.path.join(unreal.Paths.project_saved_dir(),'Reports','staticmesh_collision_api_probe.json')
open(report,'w',encoding='utf-8').write(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
