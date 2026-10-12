import unreal, os, json, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_visual_ground_audit_2026-10-12.json')
out={'ok':False,'actors':[],'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('FINAL load failed')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    labels=['Rathaus_DGM1_DOP2025_v61','Rathaus_ROADS_DATA_v61','NAV_Rathaus_TerrainProxy_v73','Rathaus_BERLIN3D_REAL_v70']
    for label in labels:
        a=next((x for x in actors if x.get_actor_label()==label),None)
        if not a: out['actors'].append({'label':label,'missing':True}); continue
        c=getattr(a,'static_mesh_component',None)
        row={'label':label,'class':a.get_class().get_name(),'location':list(map(float,[a.get_actor_location().x,a.get_actor_location().y,a.get_actor_location().z])),'rotation':list(map(float,[a.get_actor_rotation().pitch,a.get_actor_rotation().yaw,a.get_actor_rotation().roll])),'scale':list(map(float,[a.get_actor_scale3d().x,a.get_actor_scale3d().y,a.get_actor_scale3d().z])),'hidden':str(c.get_editor_property('hidden_in_game')) if c else None,'visible':str(c.get_editor_property('visible')) if c else None}
        if c:
            sm=c.get_editor_property('static_mesh'); row['mesh']=sm.get_path_name() if sm else None
            row['materials']=[]
            for i,m in enumerate(c.get_materials()):
                mr={'slot':i,'material':m.get_path_name() if m else None}
                if m:
                    try:
                        mr['class']=m.get_class().get_name()
                        mr['texture_params']=[]
                        for pname in m.get_texture_parameter_values():
                            mr['texture_params'].append(str(pname))
                    except Exception as e: mr['mat_error']=str(e)
                row['materials'].append(mr)
            try:
                origin,extent=a.get_actor_bounds(False)
                row['bounds_origin']=[float(origin.x),float(origin.y),float(origin.z)]
                row['bounds_extent']=[float(extent.x),float(extent.y),float(extent.z)]
            except Exception as e: row['bounds_error']=str(e)
        out['actors'].append(row)
    out['ok']=True
except Exception as e:
    out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
