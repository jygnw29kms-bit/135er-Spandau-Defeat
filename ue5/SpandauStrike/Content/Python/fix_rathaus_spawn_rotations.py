import unreal, os, json, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_spawn_rotation_fix_2026-10-12.json')
out={'ok':False,'errors':[],'starts':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('FINAL load failed')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    starts=sorted([a for a in actors if 'LyraPlayerStart' in a.get_class().get_name()], key=lambda a:a.get_actor_label())
    if len(starts)!=2: raise RuntimeError('expected 2 LyraPlayerStarts, got %d'%len(starts))
    for i,s in enumerate(starts):
        before=s.get_actor_rotation(); yaw=0.0 if i==0 else 180.0
        s.set_actor_rotation(unreal.Rotator(0.0,yaw,0.0),False)
        after=s.get_actor_rotation()
        out['starts'].append({'label':str(s.get_actor_label()),'before':[float(before.pitch),float(before.yaw),float(before.roll)],'after':[float(after.pitch),float(after.yaw),float(after.roll)]})
    if not lvl.save_current_level(): raise RuntimeError('save_current_level failed')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    out['ok']=True
except Exception as e:
    out['errors']+=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
