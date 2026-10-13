import unreal, os, json, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
R=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_roads_current_audit.json')
out={'ok':False,'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); assert lvl.load_level(MAP)
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    a=next((x for x in eas.get_all_level_actors() if x.get_actor_label()=='Rathaus_ROADS_DATA_v61'),None)
    if not a: raise RuntimeError('roads actor missing')
    c=a.static_mesh_component; m=c.static_mesh
    out['actor']=a.get_actor_label(); out['visible']=bool(c.get_editor_property('visible')); out['hidden_in_game']=bool(c.get_editor_property('hidden_in_game'))
    out['mesh']=m.get_path_name() if m else None; out['location']=[float(v) for v in [a.get_actor_location().x,a.get_actor_location().y,a.get_actor_location().z]]
    o,e=a.get_actor_bounds(False); out['bounds']={'origin':[float(o.x),float(o.y),float(o.z)],'extent':[float(e.x),float(e.y),float(e.z)]}
    out['collision_profile']=str(c.get_collision_profile_name()); out['collision_enabled']=str(c.get_collision_enabled())
    out['materials']=[]
    for i in range(c.get_num_materials()):
        mat=c.get_material(i); row={'slot':i,'material':mat.get_path_name() if mat else None,'textures':[]}
        if mat:
            try: row['textures']=[t.get_path_name() for t in mat.get_used_textures()]
            except: pass
        out['materials'].append(row)
    try:
        sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem); out['uv_channels']=int(sub.get_num_uv_channels(m,0))
    except Exception as e: out['uv_error']=str(e)
    try:
        idata=m.get_editor_property('asset_import_data'); out['import_source']=idata.get_first_filename() if idata else None
    except Exception as e: out['import_source_error']=str(e)
    out['ok']=True
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(R),exist_ok=True)
with open(R,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
unreal.SystemLibrary.execute_console_command(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),'QUIT_EDITOR')
