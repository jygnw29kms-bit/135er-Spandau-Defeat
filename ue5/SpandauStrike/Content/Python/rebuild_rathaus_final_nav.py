import unreal, json, os, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_final_nav_rebuild.json')
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
out={'ok':False,'map':MAP,'recasts':0,'bounds':0,'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('map load failed')
    world=unreal.EditorLevelLibrary.get_editor_world()
    recasts=[a for a in eas.get_all_level_actors() if a.get_class().get_name()=='RecastNavMesh']
    bounds=[a for a in eas.get_all_level_actors() if a.get_class().get_name()=='NavMeshBoundsVolume']
    out['recasts']=len(recasts); out['bounds']=len(bounds)
    if not recasts: raise RuntimeError('RecastNavMesh missing')
    if not bounds: raise RuntimeError('NavMeshBoundsVolume missing')
    for nav in recasts:
        try: nav.set_editor_property('runtime_generation',unreal.RuntimeGenerationType.STATIC)
        except Exception as e: out.setdefault('notes',[]).append(str(e))
        try: nav.set_editor_property('is_spatially_loaded',False)
        except: pass
    unreal.SystemLibrary.execute_console_command(world,'RebuildNavigation')
    unreal.SystemLibrary.execute_console_command(world,'navmesh')
    if not lvl.save_current_level(): raise RuntimeError('save failed')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    out['ok']=True
except Exception as e:
    out['errors'].append(str(e)); out['traceback']=traceback.format_exc()
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
unreal.log('[RATHAUS_NAV_REBUILD] '+json.dumps(out))
if not out['ok']: raise RuntimeError('nav rebuild failed')
