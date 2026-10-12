import unreal,json,os,traceback
assets={
'dgm':'/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v61/SM_RathausSpandau_DGM1_DOP_v60.SM_RathausSpandau_DGM1_DOP_v60',
'roads':'/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v55/SM_RathausSpandau_ROADS_DGM_v54.SM_RathausSpandau_ROADS_DGM_v54'}
out={}
for k,p in assets.items():
 m=unreal.load_asset(p); d={'path':p}
 for prop in ['has_navigation_data','nav_collision']:
  try:
   v=m.get_editor_property(prop); d[prop]=str(v)
   if prop=='nav_collision' and v:
    d['nav_class']=v.get_class().get_name(); d['nav_methods']=[x for x in dir(v) if any(s in x.lower() for s in ['bound','convex','tri','collision','setup'])]
    try:
     b=v.get_bounds(); d['nav_bounds']=str(b)
    except Exception as e:d['nav_bounds_error']=str(e)
  except Exception as e:d[prop+'_error']=str(e)
 d['mesh_nav_dir']=[x for x in dir(m) if 'nav' in x.lower()]
 out[k]=d
report=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_staticmesh_navcollision_audit.json')
open(report,'w',encoding='utf-8').write(json.dumps(out,indent=2,ensure_ascii=False))
unreal.log('[STATICMESH_NAVCOL] '+json.dumps(out))
