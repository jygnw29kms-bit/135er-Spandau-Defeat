import unreal, os, json, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
MESH='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v80/SM_RathausSpandau_ROADS_DGM_v80'
MAT_DIR='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v80'; MAT_NAME='M_Rathaus_ROADS_Asphalt_v80'; MAT_PATH=MAT_DIR+'/'+MAT_NAME
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_roads_v80_install.json')
out={'ok':False,'errors':[]}
try:
    mesh=unreal.EditorAssetLibrary.load_asset(MESH)
    if not mesh: raise RuntimeError('v80 roads mesh missing')
    mat=unreal.EditorAssetLibrary.load_asset(MAT_PATH)
    if not mat:
        mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset(MAT_NAME,MAT_DIR,unreal.Material,unreal.MaterialFactoryNew())
        if not mat: raise RuntimeError('road material create failed')
        col=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-400,0)
        col.set_editor_property('constant',unreal.LinearColor(0.055,0.058,0.062,1.0))
        unreal.MaterialEditingLibrary.connect_material_property(col,'',unreal.MaterialProperty.MP_BASE_COLOR)
        rough=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant,-400,120); rough.set_editor_property('r',0.9)
        unreal.MaterialEditingLibrary.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
        spec=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant,-400,220); spec.set_editor_property('r',0.18)
        unreal.MaterialEditingLibrary.connect_material_property(spec,'',unreal.MaterialProperty.MP_SPECULAR)
        unreal.MaterialEditingLibrary.recompile_material(mat); unreal.EditorAssetLibrary.save_loaded_asset(mat,only_if_is_dirty=False)
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('FINAL load failed')
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    a=next((x for x in eas.get_all_level_actors() if x.get_actor_label() in ['Rathaus_ROADS_DATA_v61','Rathaus_ROADS_VISUAL_v80']),None)
    if not a: raise RuntimeError('roads actor missing')
    c=a.static_mesh_component
    old_mesh=c.static_mesh.get_path_name() if c.static_mesh else None
    old_mat=c.get_material(0).get_path_name() if c.get_material(0) else None
    c.set_static_mesh(mesh); c.set_material(0,mat)
    c.set_editor_property('visible',True); c.set_editor_property('hidden_in_game',False)
    c.set_collision_profile_name('NoCollision'); c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); c.set_editor_property('can_ever_affect_navigation',False)
    a.set_actor_hidden_in_game(False); a.set_actor_label('Rathaus_ROADS_VISUAL_v80')
    try: a.set_editor_property('is_spatially_loaded',False)
    except: pass
    save_ok=lvl.save_current_level(); unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    out={'ok':bool(save_ok),'errors':[],'actor':a.get_actor_label(),'old_mesh':old_mesh,'new_mesh':c.static_mesh.get_path_name(),'old_material':old_mat,'new_material':c.get_material(0).get_path_name() if c.get_material(0) else None,'visible':bool(c.get_editor_property('visible')),'hidden_in_game':bool(c.get_editor_property('hidden_in_game')),'collision':str(c.get_collision_enabled()),'profile':str(c.get_collision_profile_name()),'save_current_level':bool(save_ok)}
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
unreal.SystemLibrary.execute_console_command(unreal.EditorLevelLibrary.get_editor_world(),'QUIT_EDITOR')
