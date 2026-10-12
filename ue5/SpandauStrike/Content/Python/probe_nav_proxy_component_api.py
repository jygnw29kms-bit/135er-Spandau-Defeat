import unreal,json,os
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lvl.load_level(MAP)
a=next((x for x in eas.get_all_level_actors() if x.get_actor_label()=='NAV_Rathaus_TerrainProxy_v73'),None)
out={'found':bool(a)}
if a:
 c=a.static_mesh_component
 out['methods']=[n for n in dir(c) if any(k in n.lower() for k in ['nav','affect','collision'])]
 out['actor_methods']=[n for n in dir(a) if any(k in n.lower() for k in ['nav','affect'])]
 for p in ['can_ever_affect_navigation','b_can_ever_affect_navigation','navigation_relevant','is_navigation_relevant','collision_enabled','collision_profile_name']:
  try: out[p]=str(c.get_editor_property(p))
  except Exception as e: out[p+'_error']=str(e)
p=os.path.join(unreal.Paths.project_saved_dir(),'Reports','nav_proxy_component_api.json'); os.makedirs(os.path.dirname(p),exist_ok=True)
open(p,'w',encoding='utf-8').write(json.dumps(out,indent=2)); unreal.log('[NAV_PROXY_API] '+json.dumps(out))
