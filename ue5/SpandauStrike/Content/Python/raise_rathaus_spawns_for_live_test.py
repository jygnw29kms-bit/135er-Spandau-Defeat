import unreal, json, os, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_live_spawn_raise.json')
out={'ok':False,'starts':[],'pads':[],'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('load failed')
    starts=sorted([a for a in eas.get_all_level_actors() if a.get_class().get_name()=='LyraPlayerStart'],key=lambda a:a.get_actor_label())
    pads=sorted([a for a in eas.get_all_level_actors() if a.get_actor_label().startswith('TECH_SpawnSafetyPad_')],key=lambda a:a.get_actor_label())
    if len(starts)<2 or len(pads)<2: raise RuntimeError(f'need 2 starts and pads, got {len(starts)}/{len(pads)}')
    for i,(s,pad) in enumerate(zip(starts,pads),1):
        pp=pad.get_actor_location()
        ground_top=pp.z+25.0
        pad.set_actor_scale3d(unreal.Vector(10.0,10.0,0.5))
        s.set_actor_location(unreal.Vector(pp.x,pp.y,ground_top+1000.0),False,False)
        out['starts'].append({'label':s.get_actor_label(),'location':[pp.x,pp.y,ground_top+1000.0]})
        out['pads'].append({'label':pad.get_actor_label(),'location':[pp.x,pp.y,pp.z],'scale':[10.0,10.0,0.5]})
    if not lvl.save_current_level(): raise RuntimeError('save failed')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    out['ok']=True
except Exception as e:
    out['errors'].append(str(e)); out['traceback']=traceback.format_exc()
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2)
unreal.log('[RATHAUS_LIVE_SPAWN_RAISE] '+json.dumps(out))
if not out['ok']: raise RuntimeError('live spawn raise failed')
