import unreal, os, json, traceback, math
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
DGM='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v83/SM_RathausSpandau_DGM1_DOP_v83_RAWDGM'
DOPMAT='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v76/M_Rathaus_DOP2025_v76'
NAV='/Game/SpandauStrike/Maps/Rathaus/Navigation/REAL_v84/SM_RathausSpandau_NAV_PROXY_v84'
ROADS='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v85/SM_RathausSpandau_ROADS_DGM_v85_PROJECTED_V83'
ROADMAT='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v80/M_Rathaus_ROADS_Asphalt_v80'
REP=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v83_v84_v85_final_install.json')
OX=377956.8271307037; OY=5822062.184676066; OZ=33.45
ROOT=r'C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\SourceData\DGM1'
files=[os.path.join(ROOT,'376_5820','dgm1_33_376_5820_2_be.xyz'),os.path.join(ROOT,'376_5822','dgm1_33_376_5822_2_be.xyz'),os.path.join(ROOT,'378_5820','dgm1_33_378_5820_2_be.xyz'),os.path.join(ROOT,'378_5822','dgm1_33_378_5822_2_be.xyz')]
out={'ok':False,'errors':[],'spawns':[]}
try:
 lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
 if not lvl.load_level(MAP): raise RuntimeError('FINAL load failed')
 dgm=unreal.load_asset(DGM); dopmat=unreal.load_asset(DOPMAT); nav=unreal.load_asset(NAV); roads=unreal.load_asset(ROADS); roadmat=unreal.load_asset(ROADMAT)
 if not all([dgm,dopmat,nav,roads,roadmat]): raise RuntimeError('one or more v83/v84/v85 assets missing')
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
 visible=None; proxy=None; road=None
 for a in actors:
  c=getattr(a,'static_mesh_component',None); sm=c.get_editor_property('static_mesh') if c else None; p=sm.get_path_name() if sm else ''; lab=a.get_actor_label()
  if visible is None and ('DGM1_DOP_v79' in p or lab.startswith('A_Rathaus_DGM1_DOP')): visible=a
  if proxy is None and ('NAV_PROXY_v7' in p or 'NAV_PROXY_v84' in p or 'TerrainProxy' in lab): proxy=a
  if road is None and ('ROADS_DGM_v8' in p or 'ROADS_VISUAL' in lab): road=a
 if not visible: raise RuntimeError('visible DGM actor missing')
 if not proxy: raise RuntimeError('nav proxy actor missing')
 if not road: raise RuntimeError('road actor missing')
 cv=visible.static_mesh_component; cp=proxy.static_mesh_component; cr=road.static_mesh_component
 out['old_visible']=cv.static_mesh.get_path_name() if cv.static_mesh else None; out['old_proxy']=cp.static_mesh.get_path_name() if cp.static_mesh else None; out['old_roads']=cr.static_mesh.get_path_name() if cr.static_mesh else None
 cv.set_static_mesh(dgm); cv.set_material(0,dopmat); cv.set_collision_profile_name('NoCollision'); cv.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); cv.set_editor_property('can_ever_affect_navigation',False); visible.set_actor_hidden_in_game(False); visible.set_actor_label('A_Rathaus_DGM1_DOP_v83')
 cp.set_static_mesh(nav); cp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS); cp.set_collision_profile_name('BlockAll'); cp.set_editor_property('can_ever_affect_navigation',True); cp.set_visibility(False,True); cp.set_hidden_in_game(True); proxy.set_actor_label('NAV_Rathaus_TerrainProxy_v84')
 cr.set_static_mesh(roads); cr.set_material(0,roadmat); cr.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); cr.set_editor_property('can_ever_affect_navigation',False); road.set_actor_label('Rathaus_ROADS_VISUAL_v85')
 starts=[a for a in actors if a.get_class().get_name()=='LyraPlayerStart']; starts.sort(key=lambda a:a.get_actor_label())
 if len(starts)<2: raise RuntimeError('expected 2 LyraPlayerStarts')
 es=[]; ns=[]
 for a in starts:
  p=a.get_actor_location(); es.append(OX+p.x/100.0); ns.append(OY-p.y/100.0)
 emin,emax=min(es)-3,max(es)+3; nmin,nmax=min(ns)-3,max(ns)+3; pts={}
 for fp in files:
  with open(fp,'r',encoding='utf-8',errors='ignore') as f:
   for line in f:
    try:e,n,z=map(float,line.split()[:3])
    except:continue
    if emin<=e<=emax and nmin<=n<=nmax: pts[(round(e*2),round(n*2))]=z
 def sample(e,n):
  e0=math.floor(e-0.5)+0.5; n0=math.floor(n-0.5)+0.5; e1=e0+1; n1=n0+1
  q=[pts.get((round(e0*2),round(n0*2))),pts.get((round(e1*2),round(n0*2))),pts.get((round(e0*2),round(n1*2))),pts.get((round(e1*2),round(n1*2)))]
  if None in q: raise RuntimeError('missing raw DGM sample '+str((e,n,q)))
  tx=e-e0; ty=n-n0; return (q[0]*(1-tx)+q[1]*tx)*(1-ty)+(q[2]*(1-tx)+q[3]*tx)*ty
 for i,a in enumerate(starts):
  p=a.get_actor_location(); e=OX+p.x/100.0; n=OY-p.y/100.0; surf=(sample(e,n)-OZ)*100.0; a.set_actor_location(unreal.Vector(p.x,p.y,surf+120.0),False,False)
  r=unreal.Rotator(); r.pitch=0.0; r.yaw=0.0 if i==0 else 180.0; r.roll=0.0; a.set_actor_rotation(r,False)
  out['spawns'].append({'label':a.get_actor_label(),'xy':[p.x,p.y],'surface_z':surf,'new_z':surf+120.0,'yaw':r.yaw})
 out['new_visible']=cv.static_mesh.get_path_name(); out['new_proxy']=cp.static_mesh.get_path_name(); out['new_roads']=cr.static_mesh.get_path_name()
 out['save_current_level']=bool(lvl.save_current_level()); unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True); out['ok']=out['save_current_level']
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REP),exist_ok=True); open(REP,'w',encoding='utf-8').write(json.dumps(out,indent=2,ensure_ascii=False,default=str)); print(json.dumps(out,indent=2,ensure_ascii=False,default=str)); unreal.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')