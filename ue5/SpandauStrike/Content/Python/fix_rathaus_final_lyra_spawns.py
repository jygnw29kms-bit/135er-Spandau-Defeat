import unreal, json, os, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_final_lyra_spawn_fix.json')
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
out={'ok':False,'map':MAP,'before':[],'after':[],'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('FINAL load failed')
    lyra_cls=unreal.load_class(None,'/Script/LyraGame.LyraPlayerStart')
    if not lyra_cls: raise RuntimeError('LyraPlayerStart class not found')
    old=[]
    for a in eas.get_all_level_actors():
        if a.get_actor_label() in ('TECH_PlayerStart_1_v64','TECH_PlayerStart_2_v64'):
            p=a.get_actor_location(); r=a.get_actor_rotation()
            out['before'].append({'label':a.get_actor_label(),'class':a.get_class().get_name(),'location':[p.x,p.y,p.z],'rotation':[r.pitch,r.yaw,r.roll]})
            old.append((a,a.get_actor_label(),p,r))
    if len(old)!=2: raise RuntimeError('expected 2 existing Rathaus player starts, got '+str(len(old)))
    for a,label,p,r in old:
        eas.destroy_actor(a)
        n=eas.spawn_actor_from_class(lyra_cls,p,r)
        if not n: raise RuntimeError('failed spawning '+label)
        n.set_actor_label(label)
        try: n.set_folder_path('Rathaus/Gameplay')
        except: pass
        try: n.set_editor_property('is_spatially_loaded',False)
        except: pass
        try: n.set_editor_property('tags',['SpandauStrike','RathausFinal','PlaytestSpawn'])
        except: pass
    if not lvl.save_current_level(): raise RuntimeError('save_current_level returned false')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    if not lvl.load_level(MAP): raise RuntimeError('reload failed')
    for a in eas.get_all_level_actors():
        if a.get_actor_label() in ('TECH_PlayerStart_1_v64','TECH_PlayerStart_2_v64'):
            p=a.get_actor_location(); r=a.get_actor_rotation()
            out['after'].append({'label':a.get_actor_label(),'class':a.get_class().get_name(),'location':[p.x,p.y,p.z],'rotation':[r.pitch,r.yaw,r.roll]})
    out['ok']=len(out['after'])==2 and all(x['class']=='LyraPlayerStart' for x in out['after'])
    if not out['ok']: raise RuntimeError('Lyra spawn persistence verification failed')
except Exception as e:
    out['errors'].append(str(e)); out['traceback']=traceback.format_exc()
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,ensure_ascii=False,indent=2)
unreal.log('[RATHAUS_LYRA_SPAWN_FIX] '+json.dumps(out))
if not out['ok']: raise RuntimeError('Lyra spawn fix failed; see '+REPORT)
