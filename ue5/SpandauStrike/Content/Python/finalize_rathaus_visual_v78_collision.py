import unreal, os, json, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_visual_v78_collision_finalize.json')
out={'ok':False,'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); assert lvl.load_level(MAP)
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    a=next((x for x in eas.get_all_level_actors() if x.get_actor_label()=='A_Rathaus_DGM1_DOP_v78'),None)
    if not a: raise RuntimeError('v78 actor missing')
    c=a.static_mesh_component
    c.set_collision_profile_name('NoCollision')
    c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    c.set_editor_property('can_ever_affect_navigation',False)
    save_ok=lvl.save_current_level()
    out={'ok':bool(save_ok),'profile':str(c.get_collision_profile_name()),'collision_enabled':str(c.get_collision_enabled()),'can_affect_navigation':False,'save_current_level':bool(save_ok),'errors':[]}
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
unreal.SystemLibrary.execute_console_command(unreal.EditorLevelLibrary.get_editor_world(),'QUIT_EDITOR')
