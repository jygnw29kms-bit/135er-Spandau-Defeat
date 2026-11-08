import json, os, unreal
MAP='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v81_DGM_SPAWNS_PROBE'
OUT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v81_all_meshes.json')
lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actorsub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not lvl.load_level(MAP): raise RuntimeError('load failed')
rows=[]
for a in actorsub.get_all_level_actors():
    if a.get_class().get_name()!='StaticMeshActor': continue
    b=a.get_actor_bounds(False,False)
    comp=a.static_mesh_component
    mesh=comp.get_editor_property('static_mesh')
    mats=[]
    try:
        for i in range(comp.get_num_materials()):
            m=comp.get_material(i); mats.append(m.get_path_name() if m else None)
    except: pass
    o=b[0]; e=b[1]
    rows.append({'label':a.get_actor_label(),'mesh':mesh.get_path_name() if mesh else None,'loc':[a.get_actor_location().x,a.get_actor_location().y,a.get_actor_location().z],'rot':[a.get_actor_rotation().pitch,a.get_actor_rotation().yaw,a.get_actor_rotation().roll],'scale':[a.get_actor_scale3d().x,a.get_actor_scale3d().y,a.get_actor_scale3d().z],'bounds_origin':[o.x,o.y,o.z],'bounds_extent':[e.x,e.y,e.z],'zmin':o.z-e.z,'zmax':o.z+e.z,'hidden_editor':a.is_hidden_ed(),'materials':mats})
rows.sort(key=lambda r:(-r['bounds_extent'][2],r['label']))
os.makedirs(os.path.dirname(OUT),exist_ok=True)
with open(OUT,'w',encoding='utf-8') as f: json.dump({'map':MAP,'count':len(rows),'meshes':rows},f,indent=2,ensure_ascii=False)
print('COUNT',len(rows)); print('\n'.join(f"{r['label']} z=[{r['zmin']:.1f},{r['zmax']:.1f}] ext=({r['bounds_extent'][0]:.1f},{r['bounds_extent'][1]:.1f},{r['bounds_extent'][2]:.1f}) mats={r['materials']}" for r in rows))
