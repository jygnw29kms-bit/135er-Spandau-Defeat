import unreal,json,os,traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nav10m_deferred_validation.json')
state={'ticks':0,'phase':'waiting','rebuild_tick':0,'done':False,'result':{'ok':False,'errors':[]}}
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem); ue=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
if not lvl.load_level(MAP): raise RuntimeError('FINAL load failed')

def validate():
 world=ue.get_editor_world(); recasts=[a for a in eas.get_all_level_actors() if a.get_class().get_name()=='RecastNavMesh']; nav=recasts[0] if recasts else None
 pts=[]
 for y in [-12000,-6000,0,6000,12000]:
  for x in [-12000,-6000,0,6000,12000]:
   q=unreal.NavigationSystemV1.project_point_to_navigation(world,unreal.Vector(float(x),float(y),500.0),nav,None,unreal.Vector(600,600,2000))
   pts.append({'in':[x,y,500.0],'projected':None if q is None else [q.x,q.y,q.z]})
 starts=sorted([a for a in eas.get_all_level_actors() if 'PlayerStart' in a.get_class().get_name()],key=lambda a:a.get_actor_label())
 path=None
 if len(starts)>=2:
  path=unreal.NavigationSystemV1.find_path_to_location_synchronously(world,starts[0].get_actor_location(),starts[1].get_actor_location(),None,None)
 valid=sum(1 for p in pts if p['projected'] is not None)
 return {'grid':pts,'valid_count':valid,'total':len(pts),'path_valid':bool(path and path.is_valid()),'path_partial':bool(path.is_partial()) if path else None,'nav10m_count':len([a for a in eas.get_all_level_actors() if a.get_actor_label().startswith('NAV10M_')])}

def finish(extra):
 if state['done']: return
 state['done']=True; r=state['result']; r.update(extra); r['ticks']=state['ticks']; r['phase']=state['phase']; r['ok']=r.get('valid_count',0)>0 and r.get('path_valid',False)
 os.makedirs(os.path.dirname(REPORT),exist_ok=True)
 with open(REPORT,'w',encoding='utf-8') as f: json.dump(r,f,indent=2,ensure_ascii=False)
 unreal.log('[RATHAUS_NAV10M_DEFERRED] '+json.dumps(r))
 try: unreal.unregister_slate_post_tick_callback(state['handle'])
 except: pass
 unreal.EditorPythonScripting.set_keep_python_script_alive(False)
 unreal.SystemLibrary.execute_console_command(ue.get_editor_world(),'QUIT_EDITOR')

def tick(dt):
 state['ticks']+=1
 try:
  world=ue.get_editor_world()
  locked=unreal.NavigationSystemV1.is_navigation_being_built_or_locked(world)
  if state['phase']=='waiting' and state['ticks']>=50 and not locked:
   state['phase']='rebuilding'; state['rebuild_tick']=state['ticks']; unreal.log('[RATHAUS_NAV10M_DEFERRED] explicit rebuild'); unreal.SystemLibrary.execute_console_command(world,'RebuildNavigation')
  elif state['phase']=='rebuilding' and state['ticks']>=state['rebuild_tick']+8 and not unreal.NavigationSystemV1.is_navigation_being_built(world):
   state['phase']='validating'; finish(validate())
  if state['ticks']>1200: finish({'timeout':True})
 except Exception as e:
  state['result']['errors'].append(str(e)); state['result']['traceback']=traceback.format_exc(); finish({})
state['handle']=unreal.register_slate_post_tick_callback(tick)
unreal.log('[RATHAUS_NAV10M_DEFERRED] registered')
