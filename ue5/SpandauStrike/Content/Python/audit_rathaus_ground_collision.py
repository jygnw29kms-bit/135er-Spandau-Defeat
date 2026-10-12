import unreal,json,os,traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_ground_collision_audit.json')
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
out={'ok':False,'map':MAP,'meshes':[],'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('load failed')
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        c=a.get_component_by_class(unreal.StaticMeshComponent)
        if not c or not c.static_mesh: continue
        m=c.static_mesh
        row={'label':a.get_actor_label(),'mesh':m.get_path_name(),'profile':str(c.get_collision_profile_name()),'enabled':str(c.get_collision_enabled())}
        try:
            bs=m.get_editor_property('body_setup'); row['body_setup']=bool(bs)
            if bs:
                ag=bs.get_editor_property('agg_geom')
                row['trace_flag']=str(bs.get_editor_property('collision_trace_flag'))
                row['simple']={'boxes':len(ag.get_editor_property('box_elems')),'spheres':len(ag.get_editor_property('sphere_elems')),'capsules':len(ag.get_editor_property('sphyl_elems')),'convex':len(ag.get_editor_property('convex_elems'))}
        except Exception as e: row['body_error']=str(e)
        try:
            s=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
            row['vertices']=s.get_number_verts(m,0); row['triangles']=s.get_number_triangles(m,0)
        except Exception as e: row['meshstats_error']=str(e)
        try:
            row['responses']={}
            for ch in [unreal.CollisionChannel.ECC_VISIBILITY,unreal.CollisionChannel.ECC_CAMERA,unreal.CollisionChannel.ECC_PAWN,unreal.CollisionChannel.ECC_WORLD_STATIC,unreal.CollisionChannel.ECC_WORLD_DYNAMIC]:
                row['responses'][str(ch)]=str(c.get_collision_response_to_channel(ch))
        except Exception as e: row['response_error']=str(e)
        out['meshes'].append(row)
    out['ok']=True
except Exception as e:
    out['errors'].append(str(e));out['traceback']=traceback.format_exc()
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,ensure_ascii=False,indent=2)
unreal.log('[RATHAUS_GROUND_COLLISION] '+json.dumps(out))
if not out['ok']: raise RuntimeError('ground audit failed')
