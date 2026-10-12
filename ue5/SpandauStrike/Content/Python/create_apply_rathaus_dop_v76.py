import unreal, os, json, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
MAT_PATH='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v76/M_Rathaus_DOP2025_v76'
TEX_PATH='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v61/RathausSpandau_DOP2025_360m'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_dop_v76_apply_2026-10-12.json')
out={'ok':False,'errors':[]}
try:
    mat=unreal.load_asset(MAT_PATH); tex=unreal.load_asset(TEX_PATH)
    if not mat or not tex: raise RuntimeError('v76 material or DOP texture missing')
    node=unreal.MaterialEditingLibrary.get_material_property_input_node(mat,unreal.MaterialProperty.MP_BASE_COLOR)
    if not node: raise RuntimeError('BaseColor input node missing')
    node_tex=node.get_editor_property('texture') if hasattr(node,'get_editor_property') else None
    out['base_color_node']=node.get_class().get_name()
    out['base_color_texture']=node_tex.get_path_name() if node_tex else None
    out['base_color_output']=str(unreal.MaterialEditingLibrary.get_material_property_input_node_output_name(mat,unreal.MaterialProperty.MP_BASE_COLOR))
    if not out['base_color_texture'] or not out['base_color_texture'].startswith(TEX_PATH): raise RuntimeError('BaseColor not wired to expected DOP texture')
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('FINAL load failed')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    dgm=next((a for a in actors if a.get_actor_label()=='Rathaus_DGM1_DOP2025_v61'),None)
    if not dgm: raise RuntimeError('DGM actor missing')
    comp=dgm.static_mesh_component
    old=comp.get_material(0)
    out['old_material']=old.get_path_name() if old else None
    comp.set_material(0,mat)
    out['new_material']=comp.get_material(0).get_path_name() if comp.get_material(0) else None
    if not out['new_material'] or not out['new_material'].startswith(MAT_PATH): raise RuntimeError('material assignment failed')
    if not lvl.save_current_level(): raise RuntimeError('level save failed')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    out['ok']=True
except Exception as e:
    out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
