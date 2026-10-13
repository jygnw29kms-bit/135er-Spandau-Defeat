import unreal, os, json, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
MESH='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v79/SM_RathausSpandau_DGM1_DOP_v79_SMOOTH'
MAT='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v76/M_Rathaus_DOP2025_v76'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_visual_dgm_v79_install.json')
out={'ok':False,'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); assert lvl.load_level(MAP)
    mesh=unreal.EditorAssetLibrary.load_asset(MESH); mat=unreal.EditorAssetLibrary.load_asset(MAT)
    if not mesh or not mat: raise RuntimeError('v79 mesh/material missing')
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    target=next((a for a in eas.get_all_level_actors() if a.get_actor_label() in ['A_Rathaus_DGM1_DOP_v78','A_Rathaus_DGM1_DOP_v61']),None)
    if not target: raise RuntimeError('visible DGM actor not found')
    c=target.static_mesh_component
    old_mesh=c.static_mesh.get_path_name() if c.static_mesh else None
    c.set_static_mesh(mesh); c.set_material(0,mat)
    c.set_collision_profile_name('NoCollision'); c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    c.set_editor_property('can_ever_affect_navigation',False)
    target.set_actor_hidden_in_game(False); target.set_actor_label('A_Rathaus_DGM1_DOP_v79')
    try: target.set_editor_property('is_spatially_loaded',False)
    except: pass
    save_ok=lvl.save_current_level()
    out={'ok':bool(save_ok),'errors':[],'actor':target.get_actor_label(),'old_mesh':old_mesh,'new_mesh':c.static_mesh.get_path_name(),'material':c.get_material(0).get_path_name() if c.get_material(0) else None,'profile':str(c.get_collision_profile_name()),'collision_enabled':str(c.get_collision_enabled()),'can_affect_navigation':False,'save_current_level':bool(save_ok)}
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
unreal.SystemLibrary.execute_console_command(unreal.EditorLevelLibrary.get_editor_world(),'QUIT_EDITOR')
