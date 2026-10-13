import unreal, json, os
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
out={'ok':False,'actors':[]}
lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if lvl.load_level(MAP):
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        label=a.get_actor_label()
        if 'DGM' in label or 'TerrainProxy' in label:
            loc=a.get_actor_location(); rot=a.get_actor_rotation(); sc=a.get_actor_scale3d()
            mesh=None
            try:
                m=a.static_mesh_component.get_editor_property('static_mesh')
                mesh=m.get_path_name() if m else None
            except: pass
            out['actors'].append({'label':label,'location':[loc.x,loc.y,loc.z],'rotation':[rot.pitch,rot.yaw,rot.roll],'scale':[sc.x,sc.y,sc.z],'mesh':mesh})
    out['ok']=True
p=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v79_actor_transform.json')
with open(p,'w',encoding='utf-8') as f: json.dump(out,f,indent=2)
print(json.dumps(out,indent=2))