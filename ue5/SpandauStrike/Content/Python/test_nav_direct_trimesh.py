import unreal,json,os,traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL';DGM='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v61/SM_RathausSpandau_DGM1_DOP_v60.SM_RathausSpandau_DGM1_DOP_v60';ROADS='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v55/SM_RathausSpandau_ROADS_DGM_v54.SM_RathausSpandau_ROADS_DGM_v54';REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nav_direct_trimesh_test.json')
state={'ticks':0,'phase':'waiting','rebuild_tick':0,'done':False,'result':{'ok':False,'errors':[]}}
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); actorsub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem); ue=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem); smes=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
if not lvl.load_level(MAP): raise RuntimeError('map load failed')
dgm=unreal.load_asset(DGM); nav=dgm.get_editor_property('nav_collision')
state['result']['convex_before']=smes.get_convex_collision_count(dgm); state['result']['gather_before']=str(nav.get_editor_property('gather_convex_geometry'))
smes.remove_collisions(dgm); nav.set_editor_property('gather_convex_geometry',False)
# Force NavCollision cache invalidation via a property whose PostEditChangeProperty explicitly invalidates it, then restore immediately.
try:
 old=nav.get_editor_property('use_surface_area'); nav.set_editor_property('use_surface_area',not bool(old)); nav.set_editor_property('use_surface_area',bool(old)); state['result']['cache_invalidation_toggle']='ok'
except Exception as e: state['result']['cache_invalidation_toggle']='ERR '+str(e)
state['result']['convex_after']=smes.get_convex_collision_count(dgm); state['result']['gather_after']=str(nav.get_editor_property('gather_convex_geometry'))
for a in actorsub.get_all_level_actors():
 c=a.get_component_by_class(unreal.StaticMeshComponent)
 if c and c.static_mesh and c.static_mesh.get_path_name()==ROADS:
  state['result']['roads_label']=a.get_actor_label(); state['result']['roads_nav_before']=str(c.get_editor_property('can_ever_affect_navigation')); c.set_editor_property('can_ever_affect_navigation',False); state['result']['roads_nav_after']=str(c.get_editor_property('can_ever_affect_navigation'))

def finish(ok,extra=None):
 if state['done']:return
 state['done']=True;r=state['result'];r['ok']=bool(ok);r['ticks']=state['ticks'];r['phase']=state['phase'];
 if extra:r.update(extra)
 open(REPORT,'w',encoding='utf-8').write(json.dumps(r,indent=2,ensure_ascii=False));unreal.log('[NAV_DIRECT_TRIMESH_TEST] '+json.dumps(r))
 try:unreal.unregister_slate_post_tick_callback(state['handle'])
 except:pass
 unreal.EditorPythonScripting.set_keep_python_script_alive(False)

def validate():
 world=ue.get_editor_world();starts={a.get_actor_label():a for a in actorsub.get_all_level_actors() if 'PlayerStart' in a.get_class().get_name()};labels=sorted(starts);pro={}
 for label,a in starts.items():
  p=a.get_actor_location();q=unreal.NavigationSystemV1.project_point_to_navigation(world,p,None,None,unreal.Vector(100,100,300));pro[label]=None if q is None else [q.x,q.y,q.z]
 a=starts[labels[0]].get_actor_location();b=starts[labels[1]].get_actor_location();path=unreal.NavigationSystemV1.find_path_to_location_synchronously(world,a,b,None,None);valid=bool(path and path.is_valid());partial=bool(path.is_partial()) if path else None
 try:pts=[[v.x,v.y,v.z] for v in path.get_editor_property('path_points')] if path else []
 except:pts=[]
 z1=pro.get('TECH_PlayerStart_1_v64');z2=pro.get('TECH_PlayerStart_2_v64');correct=bool(z1 and z2 and -250<z1[2]<100 and -300<z2[2]<50)
 return valid and not partial and correct,{'projections':pro,'path_valid':valid,'path_partial':partial,'path_points':pts,'correct_height':correct,'saved':False}

def tick(dt):
 state['ticks']+=1
 try:
  world=ue.get_editor_world();locked=unreal.NavigationSystemV1.is_navigation_being_built_or_locked(world)
  if state['phase']=='waiting' and state['ticks']>=40 and not locked:
   state['phase']='rebuilding';state['rebuild_tick']=state['ticks'];unreal.SystemLibrary.execute_console_command(world,'RebuildNavigation')
  elif state['phase']=='rebuilding' and state['ticks']>=state['rebuild_tick']+5 and not unreal.NavigationSystemV1.is_navigation_being_built(world):
   state['phase']='validating';ok,extra=validate();finish(ok,extra)
  if state['ticks']>700:finish(False,{'error':'timeout'})
 except Exception as e:state['result']['errors'].append(str(e));state['result']['traceback']=traceback.format_exc();finish(False)
state['handle']=unreal.register_slate_post_tick_callback(tick);unreal.log('[NAV_DIRECT_TRIMESH_TEST] registered; transient only')
