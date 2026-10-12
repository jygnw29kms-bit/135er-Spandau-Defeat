import unreal,json,os,traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
TILES=r'C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\Reports\rathaus_nav_tiles_10m.json'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nav_tiles_10m_install.json')
out={'ok':False,'spawned':0,'errors':[]}
try:
 lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 if not lvl.load_level(MAP): raise RuntimeError('map load failed')
 data=json.load(open(TILES,'r',encoding='utf-8')); cube=unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Cube.Cube')
 if not cube: raise RuntimeError('cube missing')
 for a in list(eas.get_all_level_actors()):
  if a.get_actor_label()=='NAV_Rathaus_TerrainProxy_v73' or a.get_actor_label().startswith('NAV10M_'): eas.destroy_actor(a)
 for i,t in enumerate(data['tiles']):
  loc=unreal.Vector(float(t['x']),float(t['y']),float(t['z'])-32.0)
  rot=unreal.Rotator(float(t.get('pitch',0.0)),0.0,float(t.get('roll',0.0)))
  a=eas.spawn_actor_from_class(unreal.StaticMeshActor,loc,rot,False)
  if not a: continue
  a.set_actor_label('NAV10M_%04d'%i,mark_dirty=False); a.set_folder_path('Rathaus/NAV/Terrain10m')
  a.set_actor_scale3d(unreal.Vector(10.8,10.8,0.4))
  c=a.static_mesh_component; c.set_static_mesh(cube); c.set_collision_profile_name('BlockAll'); c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
  c.set_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN,unreal.CollisionResponseType.ECR_IGNORE)
  try: c.set_editor_property('can_ever_affect_navigation',True)
  except Exception as e: out['errors'].append('navflag '+str(e))
  try: c.set_hidden_in_game(True); c.set_visibility(False,True)
  except: pass
  try: a.set_editor_property('is_spatially_loaded',False)
  except: pass
  out['spawned']+=1
 if not lvl.save_current_level(): raise RuntimeError('save failed')
 unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True); out['ok']=out['spawned']>1000
except Exception as e:
 out['errors'].append(str(e)); out['traceback']=traceback.format_exc()
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
unreal.log('[RATHAUS_NAV10M] '+json.dumps(out))
if not out['ok']: raise RuntimeError('nav tile install failed')
