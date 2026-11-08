import json, os, unreal
MAP=os.environ.get('SPANDAU_INSPECT_MAP','/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v78_GAMEPLAY_DGM1000_QA')
OUT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_visual_runtime_inspect.json')
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actorsub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not level.load_level(MAP): raise RuntimeError('failed to load '+MAP)
actors=actorsub.get_all_level_actors()
def v3(v): return [round(v.x,2),round(v.y,2),round(v.z,2)]
def rot(r): return [round(r.pitch,2),round(r.yaw,2),round(r.roll,2)]
starts=[]
for a in actors:
    if 'PlayerStart' in a.get_class().get_name():
        starts.append({'label':a.get_actor_label(),'loc':v3(a.get_actor_location()),'rot':rot(a.get_actor_rotation()),'tags':[str(x) for x in a.get_editor_property('tags')]})
meshes=[]
fogs=[]
for a in actors:
    cn=a.get_class().get_name()
    if cn=='StaticMeshActor' and ('Rathaus' in a.get_actor_label() or 'DGM' in a.get_actor_label()):
        b=a.get_actor_bounds(False,False)
        meshes.append({'label':a.get_actor_label(),'loc':v3(a.get_actor_location()),'rot':rot(a.get_actor_rotation()),'scale':v3(a.get_actor_scale3d()),'bounds_origin':v3(b[0]),'bounds_extent':v3(b[1])})
    if 'Fog' in cn or 'Fog' in a.get_actor_label():
        rec={'class':cn,'label':a.get_actor_label(),'loc':v3(a.get_actor_location())}
        try:
            c=a.get_component_by_class(unreal.ExponentialHeightFogComponent)
            if c:
                for p in ('fog_density','fog_height_falloff','start_distance','fog_max_opacity'):
                    try: rec[p]=c.get_editor_property(p)
                    except: pass
        except: pass
        fogs.append(rec)
report={'map':MAP,'actor_count':len(actors),'starts':starts,'meshes':meshes,'fogs':fogs}
os.makedirs(os.path.dirname(OUT),exist_ok=True)
with open(OUT,'w',encoding='utf-8') as f: json.dump(report,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(report,indent=2,ensure_ascii=False,default=str))
