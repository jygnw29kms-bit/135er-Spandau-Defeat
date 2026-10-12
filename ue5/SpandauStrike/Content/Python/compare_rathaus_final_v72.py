import unreal, json, os
MAPS = {
 'v72':'/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v72_BERLIN3D',
 'final':'/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
}
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_final_vs_v72.json')
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
out={}
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actorsub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for key,path in MAPS.items():
    if not sub.load_level(path): raise RuntimeError('load failed '+path)
    rows=[]
    for a in actorsub.get_all_level_actors():
        sm=''
        try:
            c=a.get_component_by_class(unreal.StaticMeshComponent)
            if c and c.static_mesh: sm=c.static_mesh.get_path_name()
        except: pass
        if ('RathausSpandau' in sm or 'BUILDING_v32' in sm or 'BERLIN3D_REAL_v70' in sm or 'Rathaus' in a.get_actor_label()):
            t=a.get_actor_transform()
            loc=a.get_actor_location(); rot=a.get_actor_rotation(); sc=a.get_actor_scale3d()
            rows.append({'label':a.get_actor_label(),'class':a.get_class().get_name(),'mesh':sm,'location':[loc.x,loc.y,loc.z],'rotation':[rot.pitch,rot.yaw,rot.roll],'scale':[sc.x,sc.y,sc.z]})
    out[key]=rows
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
unreal.log('[RATHAUS_COMPARE] '+json.dumps({'report':REPORT,'v72':out['v72'],'final':out['final']}))
