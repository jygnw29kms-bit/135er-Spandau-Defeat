import unreal, json, os, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_runtime_nav_v73_config.json')
out={'ok':False,'recasts':[],'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('map load failed')
    recasts=[a for a in eas.get_all_level_actors() if a.get_class().get_name()=='RecastNavMesh']
    if not recasts: raise RuntimeError('no RecastNavMesh')
    for r in recasts:
        item={'label':r.get_actor_label()}
        for prop,val in [('runtime_generation',unreal.RuntimeGenerationType.DYNAMIC),('force_rebuild_on_load',True),('can_be_main_nav_data',True)]:
            try:
                old=r.get_editor_property(prop); r.set_editor_property(prop,val); item[prop]={'old':str(old),'new':str(r.get_editor_property(prop))}
            except Exception as e: item[prop]={'error':str(e)}
        try: r.set_editor_property('is_spatially_loaded',False)
        except: pass
        out['recasts'].append(item)
    if not lvl.save_current_level(): raise RuntimeError('save failed')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True); out['ok']=True
except Exception as e:
    out['errors'].append(str(e)); out['traceback']=traceback.format_exc()
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
unreal.log('[RATHAUS_RUNTIME_NAV_V73] '+json.dumps(out))
if not out['ok']: raise RuntimeError('runtime nav config failed')
