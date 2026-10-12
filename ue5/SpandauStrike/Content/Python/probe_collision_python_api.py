import unreal,json,os
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','collision_python_api_probe.json')
lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); lvl.load_level(MAP)
out=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    c=a.get_component_by_class(unreal.StaticMeshComponent)
    if c and c.static_mesh and ('DGM1_DOP' in c.static_mesh.get_path_name() or 'ROADS_DGM' in c.static_mesh.get_path_name()):
        out.append({'label':a.get_actor_label(),'methods':[x for x in dir(c) if 'trace' in x.lower() or 'collision' in x.lower() or 'closest' in x.lower() or 'overlap' in x.lower()]})
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
unreal.log('[COLLISION_API_PROBE] '+json.dumps(out))
