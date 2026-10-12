import unreal,json,os,traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_projected_spawn_path.json')
state={'ticks':0,'phase':'waiting','rebuild_tick':0,'done':False,'result':{'ok':False,'errors':[]}}
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem); ue=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
if not lvl.load_level(MAP): raise RuntimeError('load failed')

def validate():
 world=ue.get_editor_world(); starts=sorted([a for a in eas.get_all_level_actors() if 'PlayerStart' in a.get_class().get_name()],key=lambda a:a.get_actor_label())
 recasts=[a for a in eas.get_all_level_actors() if a.get_class().get_name()=='RecastNavMesh']; nav=recasts[0] if recasts else None
 r={'starts':[]}
 proj=[]
 for s in starts[:2]:
  p=s.get_actor_location(); q=unreal.NavigationSystemV1.project_point_to_navigation(world,p,nav,None,unreal.Vector(1000,1000,3000))
  r['starts'].append({'label':s.get_actor_label(),'raw':[p.x,p.y,p.z],'projected':None if q is None else [q.x,q.y,q.z]}); proj.append(q)
 if len(proj)==2 and all(q is not None for q in proj):
  path=unreal.NavigationSystemV1.find_path_to_location_synchronously(world,proj[0],proj[1],None,None)
  r['projected_path_valid']=bool(path and path.is_valid()); r['projected_path_partial']=bool(path.is_partial()) if path else None
  try: r['path_points']=[[v.x,v.y,v.z] for v in path.get_editor_property('path_points')] if path else []
  except: r['path_points']=[]
  try: r['path_length']=unreal.NavigationSystemV1.get_path_length(world,proj[0],proj[1],None,None)
  except Exception as e: r['path_length_error']=str(e)
 return r

def finish(extra):
 if state['done']: return
 state['done']=True; r=state['result']; r.update(extra); r['ticks']=state['ticks']; r['phase']=state['phase']; r['ok']=bool(r.get('projected_path_valid')) and not bool(r.get('projected_path_partial'))
 os.makedirs(os.path.dirname(REPORT),exist_ok=True); open(REPORT,'w',encoding='utf-8').write(json.dumps(r,indent=2,ensure_ascii=False)); unreal.log('[RATHAUS_PROJECTED_PATH] '+json.dumps(r))
 try: unreal.unregister_slate_post_tick_callback(state['handle'])
 except: pass
 unreal.EditorPythonScripting.set_keep_python_script_alive(False); unreal.SystemLibrary.execute_console_command(ue.get_editor_world(),'QUIT_EDITOR')

def tick(dt):
 state['ticks']+=1
 try:
  world=ue.get_editor_world()
  if state['phase']=='waiting' and state['ticks']>=50 and not unreal.NavigationSystemV1.is_navigation_being_built_or_locked(world):
   state['phase']='rebuilding'; state['rebuild_tick']=state['ticks']; unreal.SystemLibrary.execute_console_command(world,'RebuildNavigation')
  elif state['phase']=='rebuilding' and state['ticks']>=state['rebuild_tick']+8 and not unreal.NavigationSystemV1.is_navigation_being_built(world): state['phase']='validating'; finish(validate())
  if state['ticks']>1200: finish({'timeout':True})
 except Exception as e: state['result']['errors'].append(str(e)); state['result']['traceback']=traceback.format_exc(); finish({})
state['handle']=unreal.register_slate_post_tick_callback(tick)
unreal.log('[RATHAUS_PROJECTED_PATH] registered')
