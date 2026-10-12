import unreal, json, os, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
MESH='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v70/SM_RathausSpandau_BERLIN3D_REAL_v70.SM_RathausSpandau_BERLIN3D_REAL_v70'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_final_v70_mesh_audit.json')
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
r={'ok':False,'map':MAP,'mesh':MESH,'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('FINAL load failed')
    mesh=unreal.load_asset(MESH)
    if not mesh: raise RuntimeError('v70 mesh load failed')
    actors=[]
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        c=a.get_component_by_class(unreal.StaticMeshComponent)
        if c and c.static_mesh and c.static_mesh.get_path_name()==MESH:
            o,e=a.get_actor_bounds(False)
            actors.append({'label':a.get_actor_label(),'origin':[o.x,o.y,o.z],'extent':[e.x,e.y,e.z],'size_cm':[e.x*2,e.y*2,e.z*2],'collision_profile':str(c.get_collision_profile_name()),'collision_enabled':str(c.get_collision_enabled()),'materials':[m.get_path_name() if m else None for m in c.get_materials()]})
    r['actors']=actors
    r['material_slots']=[str(x.material_slot_name) for x in mesh.get_editor_property('static_materials')]
    bb=mesh.get_bounding_box(); r['mesh_bounds']={'min':[bb.min.x,bb.min.y,bb.min.z],'max':[bb.max.x,bb.max.y,bb.max.z],'size_cm':[bb.max.x-bb.min.x,bb.max.y-bb.min.y,bb.max.z-bb.min.z]}
    try:
        bs=mesh.get_editor_property('body_setup')
        if bs:
            agg=bs.get_editor_property('agg_geom')
            r['collision']={'trace_flag':str(bs.get_editor_property('collision_trace_flag')),'boxes':len(agg.get_editor_property('box_elems')),'spheres':len(agg.get_editor_property('sphere_elems')),'capsules':len(agg.get_editor_property('sphyl_elems')),'convex':len(agg.get_editor_property('convex_elems'))}
        else: r['collision']={'body_setup':None}
    except Exception as e:r['collision_error']=str(e)
    try:
        r['nanite_settings']=str(mesh.get_editor_property('nanite_settings'))
    except Exception as e:r['nanite_error']=str(e)
    try:r['lod_count']=mesh.get_num_lods()
    except Exception as e:r['lod_error']=str(e)
    r['ok']=len(actors)==1
except Exception as e:
    r['errors'].append(str(e));r['traceback']=traceback.format_exc()
with open(REPORT,'w',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2)
unreal.log('[RATHAUS_V70_AUDIT] '+json.dumps({'ok':r['ok'],'actors':len(r.get('actors',[])),'collision':r.get('collision'),'lod_count':r.get('lod_count'),'report':REPORT}))
if not r['ok']:raise RuntimeError('v70 audit failed')
