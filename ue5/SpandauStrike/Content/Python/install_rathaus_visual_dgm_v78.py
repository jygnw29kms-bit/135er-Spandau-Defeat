import unreal, os, json, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
MESH='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v78/SM_RathausSpandau_DGM1_DOP_v78'
MAT='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v76/M_Rathaus_DOP2025_v76'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_visual_dgm_v78_install.json')
out={'ok':False,'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); assert lvl.load_level(MAP)
    mesh=unreal.EditorAssetLibrary.load_asset(MESH); mat=unreal.EditorAssetLibrary.load_asset(MAT)
    if not mesh or not mat: raise RuntimeError('mesh or material missing')
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors=eas.get_all_level_actors()
    target=None
    for a in actors:
        try:
            if a.get_actor_label()=='A_Rathaus_DGM1_DOP_v61': target=a; break
            if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()=='SM_RathausSpandau_DGM1_DOP_v60': target=a; break
        except: pass
    if not target: raise RuntimeError('visible DGM actor not found')
    c=target.static_mesh_component
    old_mesh=c.static_mesh.get_path_name() if c.static_mesh else None
    old_mat=(c.get_material(0).get_path_name() if c.get_material(0) else None)
    c.set_static_mesh(mesh)
    c.set_material(0,mat)
    c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    c.set_editor_property('can_ever_affect_navigation',False)
    try: target.set_actor_label('A_Rathaus_DGM1_DOP_v78')
    except: pass
    target.set_actor_hidden_in_game(False)
    try: target.set_editor_property('is_spatially_loaded',False)
    except: pass
    tags=list(target.tags)
    for t in ['SpandauStrike','RathausFinal','VisualDGM','DOP2025','v78']:
        nt=unreal.Name(t)
        if nt not in tags: tags.append(nt)
    target.tags=tags
    save_ok=lvl.save_current_level()
    out.update({'ok':bool(save_ok),'actor':target.get_actor_label(),'old_mesh':old_mesh,'new_mesh':c.static_mesh.get_path_name(),'old_material':old_mat,'new_material':c.get_material(0).get_path_name() if c.get_material(0) else None,'collision_enabled':str(c.get_collision_enabled()),'can_affect_navigation':False,'save_current_level':bool(save_ok)})
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
unreal.SystemLibrary.execute_console_command(unreal.EditorLevelLibrary.get_editor_world(),'QUIT_EDITOR')


