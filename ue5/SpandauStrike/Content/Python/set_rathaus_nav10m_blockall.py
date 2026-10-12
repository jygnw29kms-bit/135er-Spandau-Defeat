import unreal,json,os,traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nav10m_blockall.json')
out={'ok':False,'count':0,'errors':[]}
try:
 lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 if not lvl.load_level(MAP): raise RuntimeError('map load failed')
 for a in eas.get_all_level_actors():
  if not a.get_actor_label().startswith('NAV10M_'): continue
  c=a.static_mesh_component
  c.set_collision_profile_name('BlockAll')
  c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
  c.set_collision_response_to_all_channels(unreal.CollisionResponseType.ECR_BLOCK)
  try: c.set_editor_property('can_ever_affect_navigation',True)
  except Exception as e: out['errors'].append(str(e))
  out['count']+=1
 if not lvl.save_current_level(): raise RuntimeError('save failed')
 unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 out['ok']=out['count']>1000
except Exception as e:
 out['errors'].append(str(e)); out['traceback']=traceback.format_exc()
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
unreal.log('[RATHAUS_NAV10M_BLOCKALL] '+json.dumps(out))
if not out['ok']: raise RuntimeError('blockall failed')
