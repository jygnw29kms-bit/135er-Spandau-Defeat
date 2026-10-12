import unreal,json,os
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','collision_method_docs.json')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
out={}
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    c=a.get_component_by_class(unreal.StaticMeshComponent)
    if c and c.static_mesh and 'DGM1_DOP' in c.static_mesh.get_path_name():
        for n in ['line_trace_component','sphere_trace_component','get_closest_point_on_collision']:
            try: out[n]=getattr(c,n).__doc__
            except Exception as e: out[n]=str(e)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
unreal.log('[COLLISION_METHOD_DOCS] '+json.dumps(out))
