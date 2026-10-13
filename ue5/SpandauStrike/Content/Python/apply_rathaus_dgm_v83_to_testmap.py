import unreal, os, json, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_DGM_v83_TEST'
MESH='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v83/SM_RathausSpandau_DGM1_DOP_v83_RAWDGM'
REP=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_dgm_v83_apply_testmap.json')
out={'ok':False,'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('test map load failed')
    mesh=unreal.load_asset(MESH)
    if not mesh: raise RuntimeError('v83 mesh missing')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    dgm=None
    for a in actors:
        label=a.get_actor_label()
        if label=='A_Rathaus_DGM1_DOP_v79' or 'DGM1_DOP' in label:
            try:
                sm=a.static_mesh_component.get_editor_property('static_mesh')
                if sm and 'DGM1_DOP_v79' in sm.get_path_name(): dgm=a; break
            except: pass
    if not dgm: raise RuntimeError('visible v79 DGM actor not found')
    comp=dgm.static_mesh_component
    old=comp.get_editor_property('static_mesh')
    mat=comp.get_material(0)
    out['old_mesh']=old.get_path_name() if old else None
    out['material']=mat.get_path_name() if mat else None
    comp.set_static_mesh(mesh)
    dgm.set_actor_label('A_Rathaus_DGM1_DOP_v83_TEST')
    out['new_mesh']=comp.get_editor_property('static_mesh').get_path_name()
    out['save']=bool(lvl.save_current_level())
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    out['ok']=bool(out['save'])
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REP),exist_ok=True)
with open(REP,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))