import unreal, json, os
maps=['/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v72_BERLIN3D','/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL']
out={}
lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actorsub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for m in maps:
    ok=lvl.load_level(m)
    rows=[]
    if ok:
        for a in actorsub.get_all_level_actors():
            c=a.get_component_by_class(unreal.StaticMeshComponent)
            mesh=c.static_mesh.get_path_name() if c and c.static_mesh else None
            if mesh and ('Rathaus' in mesh or 'REAL_v70' in mesh or 'REAL_v32' in mesh):
                rows.append({'label':a.get_actor_label(),'class':a.get_class().get_name(),'mesh':mesh,'loc':[a.get_actor_location().x,a.get_actor_location().y,a.get_actor_location().z]})
    out[m]={'loaded':bool(ok),'actors':rows,'count':len(rows)}
report=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v72_final_compare.json')
os.makedirs(os.path.dirname(report),exist_ok=True)
open(report,'w',encoding='utf-8').write(json.dumps(out,indent=2,ensure_ascii=False))
unreal.log('[RATHAUS_COMPARE] '+json.dumps(out))
