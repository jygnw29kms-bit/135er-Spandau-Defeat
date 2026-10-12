import unreal,json,os,traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
DGM='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v61/SM_RathausSpandau_DGM1_DOP_v60.SM_RathausSpandau_DGM1_DOP_v60'
ROADS='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v55/SM_RathausSpandau_ROADS_DGM_v54.SM_RathausSpandau_ROADS_DGM_v54'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nav_no_navcollision_test.json')
state={'ticks':0,'phase':'waiting','rebuild_tick':0,'done':False,'result':{'ok':False,'errors':[]}}
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); actorsub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem); ue=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
if not lvl.load_level(MAP): raise RuntimeError('map load failed')
for p in [DGM,ROADS]:
 m=unreal.load_asset(p)
 if not m: raise RuntimeError('asset load failed '+p)
 state['result'].setdefault('before',{})[p]={'has_navigation_data':str(m.get_editor_property('has_navigation_data')),'nav_collision':str(m.get_editor_property('nav_collision'))}
 m.set_editor_property('has_navigation_data',False)
 state['result'].setdefault('after_set',{})[p]={'has_navigation_data':str(m.get_editor_property('has_navigation_data')),'nav_collision':str(m.get_editor_property('nav_collision'))}

def finish(ok,extra=None):
 if state['done']: return
 state['done']=True;r=state['result'];r['ok']=bool(ok);r['ticks']=state['ticks'];r['phase']=state['phase'];
 if extra:r.update(extra)
 open(REPORT,'w',encoding='utf-8').write(json.dumps(r,indent=2,ensure_ascii=False));unreal.log('[NAV_NO_NAVCOL_TEST] '+json.dumps(r))
 try:unreal.unregister_slate_post_tick_callback(state['handle'])
 except:pass
 unreal.EditorPythonScripting.set_keep_python_script_alive(False)

def validate():
 world=ue.get_editor_world(); starts={a.get_actor_label():a for a in actorsub.get_all_level_actors() if 'PlayerStart' in a.get_class().get_name()}; labels=sorted(starts)
 exts=[unreal.Vector(50,50,250),unreal.Vector(100,100,300),unreal.Vector(500,500,1000)]
 projections={}
 for label,a in starts.items():
  p=a.get_actor_location();projections[label]={}
  for e in exts:
   try:q=unreal.NavigationSystemV1.project_point_to_navigation(world,p,None,None,e); projections[label][f'{int(e.x)}_{int(e.z)}']=[q.x,q.y,q.z]
   except Exception as er:projections[label][f'{int(e.x)}_{int(e.z)}']='ERR '+str(er)
 a=starts[labels[0]].get_actor_location();b=starts[labels[1]].get_actor_location();path=unreal.NavigationSystemV1.find_path_to_location_synchronously(world,a,b,None,None)
 valid=bool(path and path.is_valid());partial=bool(path.is_partial()) if path else None
 try:pts=[[v.x,v.y,v.z] for v in path.get_editor_property('path_points')] if path else []
 except:pts=[]
 # expected terrain projections near -101/-151; allow broad ±100cm of floor because Recast elevates by cell/agent conventions
 z1=projections.get('TECH_PlayerStart_1_v64',{}).get('50_250');z2=projections.get('TECH_PlayerStart_2_v64',{}).get('50_250')
 correct=False
 if isinstance(z1,list) and isinstance(z2,list): correct=(-250<z1[2]<100 and -300<z2[2]<50)
 return valid and not partial and correct,{'projections':projections,'path_valid':valid,'path_partial':partial,'path_points':pts,'correct_height':correct}

def tick(dt):
 state['ticks']+=1
 try:
  world=ue.get_editor_world();locked=unreal.NavigationSystemV1.is_navigation_being_built_or_locked(world)
  if state['phase']=='waiting' and state['ticks']>=40 and not locked:
   state['phase']='rebuilding';state['rebuild_tick']=state['ticks'];unreal.SystemLibrary.execute_console_command(world,'RebuildNavigation')
  elif state['phase']=='rebuilding' and state['ticks']>=state['rebuild_tick']+5 and not unreal.NavigationSystemV1.is_navigation_being_built(world):
   state['phase']='validating';ok,extra=validate();extra['saved']=False;finish(ok,extra)
  if state['ticks']>700:finish(False,{'error':'timeout'})
 except Exception as e:state['result']['errors'].append(str(e));state['result']['traceback']=traceback.format_exc();finish(False)
state['handle']=unreal.register_slate_post_tick_callback(tick)
unreal.log('[NAV_NO_NAVCOL_TEST] registered in-memory test; no asset save')
