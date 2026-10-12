import unreal,json,os,traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_all_nav_sources.json')
out={'ok':False,'actors':[],'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('load failed')
    for a in eas.get_all_level_actors():
        comps=a.get_components_by_class(unreal.StaticMeshComponent)
        for c in comps:
            sm=c.get_editor_property('static_mesh')
            if not sm: continue
            row={'label':a.get_actor_label(),'class':a.get_class().get_name(),'mesh':sm.get_path_name(),'has_navigation_data':str(sm.get_editor_property('has_navigation_data'))}
            try: row['collision_enabled']=str(c.get_collision_enabled())
            except: pass
            try: row['profile']=str(c.get_collision_profile_name())
            except: pass
            try: row['hidden_in_game']=str(c.get_editor_property('hidden_in_game'))
            except: pass
            try:
                o,e=a.get_actor_bounds(False,False); row['bounds_min']=[o.x-e.x,o.y-e.y,o.z-e.z];row['bounds_max']=[o.x+e.x,o.y+e.y,o.z+e.z]
            except: pass
            for name in ['can_ever_affect_navigation','is_navigation_relevant','can_affect_navigation_generation']:
                try:
                    attr=getattr(c,name); row[name]=str(attr() if callable(attr) else attr)
                except Exception as ex: row[name+'_error']=str(ex)
            out['actors'].append(row)
    out['ok']=True
except Exception as e:
    out['errors'].append(str(e));out['traceback']=traceback.format_exc()
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
open(REPORT,'w',encoding='utf-8').write(json.dumps(out,indent=2,ensure_ascii=False))
unreal.log('[RATHAUS_ALL_NAV_SOURCES] '+json.dumps({'ok':out['ok'],'count':len(out['actors']),'errors':out['errors']}))
