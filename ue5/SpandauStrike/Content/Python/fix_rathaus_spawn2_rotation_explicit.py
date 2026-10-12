import unreal, os, json
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_spawn2_rotation_explicit_2026-10-12.json')
lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert lvl.load_level(MAP)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
starts=sorted([a for a in actors if 'LyraPlayerStart' in a.get_class().get_name()],key=lambda a:a.get_actor_label())
s=starts[1]
b=s.get_actor_rotation()
r=unreal.Rotator()
r.pitch=0.0; r.yaw=180.0; r.roll=0.0
s.set_actor_rotation(r,False)
a=s.get_actor_rotation()
out={'before':[float(b.pitch),float(b.yaw),float(b.roll)],'requested':[float(r.pitch),float(r.yaw),float(r.roll)],'after':[float(a.pitch),float(a.yaw),float(a.roll)]}
assert lvl.save_current_level()
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
open(REPORT,'w',encoding='utf-8').write(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
