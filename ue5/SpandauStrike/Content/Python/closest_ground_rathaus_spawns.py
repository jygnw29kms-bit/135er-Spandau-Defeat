import unreal,json,os,traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_spawn_closest_ground.json')
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
out={'ok':False,'spawns':[],'errors':[]}
try:
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    starts=[a for a in actors if 'PlayerStart' in a.get_class().get_name()]
    comps=[]
    for a in actors:
        c=a.get_component_by_class(unreal.StaticMeshComponent)
        if c and c.static_mesh and ('DGM1_DOP' in c.static_mesh.get_path_name() or 'ROADS_DGM' in c.static_mesh.get_path_name()):
            o,e=a.get_actor_bounds(False)
            comps.append((a,c,{'origin':[o.x,o.y,o.z],'extent':[e.x,e.y,e.z],'min':[o.x-e.x,o.y-e.y,o.z-e.z],'max':[o.x+e.x,o.y+e.y,o.z+e.z]}))
    for s in starts:
        p=s.get_actor_location(); r={'label':s.get_actor_label(),'spawn':[p.x,p.y,p.z],'ground':[]}
        for a,c,bounds in comps:
            item={'label':a.get_actor_label(),'bounds':bounds}
            try:
                d,pt=c.get_closest_point_on_collision(p)
                item['distance_cm']=d; item['closest']=[pt.x,pt.y,pt.z]
                item['delta']=[p.x-pt.x,p.y-pt.y,p.z-pt.z]
            except Exception as e:item['error']=str(e)
            r['ground'].append(item)
        out['spawns'].append(r)
    out['ok']=True
except Exception as e:
    out['errors'].append(str(e));out['traceback']=traceback.format_exc()
with open(REPORT,'w',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
unreal.log('[RATHAUS_CLOSEST_GROUND] '+json.dumps(out))
