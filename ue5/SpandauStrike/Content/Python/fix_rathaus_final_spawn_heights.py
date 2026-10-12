import unreal, json, os, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
TARGETS={'TECH_PlayerStart_1_v64':18.95898914265142,'TECH_PlayerStart_2_v64':-31.282046017651453}
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_final_spawn_height_fix.json')
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
out={'ok':False,'map':MAP,'targets':TARGETS,'before':{},'after':{},'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actorsub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('FINAL load failed')
    found={}
    for a in actorsub.get_all_level_actors():
        if a.get_actor_label() in TARGETS:
            found[a.get_actor_label()]=a
    if set(found)!=set(TARGETS): raise RuntimeError('PlayerStart labels mismatch: '+str(list(found)))
    for label,a in found.items():
        p=a.get_actor_location(); out['before'][label]=[p.x,p.y,p.z]
        a.set_actor_location(unreal.Vector(p.x,p.y,TARGETS[label]),False,False)
    if not lvl.save_current_level(): raise RuntimeError('save_current_level returned false')
    if not lvl.load_level(MAP): raise RuntimeError('reload failed')
    for a in actorsub.get_all_level_actors():
        label=a.get_actor_label()
        if label in TARGETS:
            p=a.get_actor_location(); out['after'][label]=[p.x,p.y,p.z]
    out['ok']=all(label in out['after'] and abs(out['after'][label][2]-z)<0.01 for label,z in TARGETS.items())
    if not out['ok']: raise RuntimeError('persisted spawn verification failed')
except Exception as e:
    out['errors'].append(str(e)); out['traceback']=traceback.format_exc()
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
unreal.log('[RATHAUS_SPAWN_FIX] '+json.dumps(out))
if not out['ok']: raise RuntimeError('spawn height fix failed; see '+REPORT)
