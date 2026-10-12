import unreal,json,os,traceback
assets={'dgm':'/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v61/SM_RathausSpandau_DGM1_DOP_v60.SM_RathausSpandau_DGM1_DOP_v60','roads':'/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v55/SM_RathausSpandau_ROADS_DGM_v54.SM_RathausSpandau_ROADS_DGM_v54'}
out={}
for name,p in assets.items():
 m=unreal.load_asset(p);bs=m.get_editor_property('body_setup');ag=bs.get_editor_property('agg_geom'); cvs=ag.get_editor_property('convex_elems'); rows=[]
 for i,c in enumerate(cvs):
  r={'index':i,'dir':[x for x in dir(c) if any(k in x.lower() for k in ['vertex','box','transform','elem','index'])]}
  for prop in ['vertex_data','index_data','elem_box','transform']:
   try:
    v=c.get_editor_property(prop)
    if prop=='vertex_data':
     pts=[[q.x,q.y,q.z] for q in v];r[prop]=pts;r['vertex_count']=len(pts)
     if pts:r['bounds']={'min':[min(x[j] for x in pts) for j in range(3)],'max':[max(x[j] for x in pts) for j in range(3)]}
    else:r[prop]=str(v)
   except Exception as e:r[prop+'_error']=str(e)
  rows.append(r)
 out[name]={'path':p,'trace_flag':str(bs.get_editor_property('collision_trace_flag')),'convex':rows}
report=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_convex_hull_audit.json');open(report,'w',encoding='utf-8').write(json.dumps(out,indent=2,ensure_ascii=False));unreal.log('[CONVEX_AUDIT] '+json.dumps(out))
