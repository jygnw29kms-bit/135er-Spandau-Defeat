import json, os, unreal
MAP='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v83_BUILDING_ONLY_VISUAL_PROBE'
OUT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v83_render_flags.json')
TARGETS={'Rathaus_BUILDING_v51_MATREF','Rathaus_DGM1_GAMEPLAY1000_v86_EXT','Rathaus_DGM1_DOP2025_v61','Rathaus_ROADS_VISUAL_v85_GAMEPLAY'}
lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not lvl.load_level(MAP): raise RuntimeError('load failed')
rows=[]
for a in sub.get_all_level_actors():
    if a.get_actor_label() not in TARGETS: continue
    c=a.get_component_by_class(unreal.StaticMeshComponent)
    r={'label':a.get_actor_label(),'actor_class':a.get_class().get_name()}
    for prop in ('hidden','initial_life_span'):
        try:r['actor_'+prop]=a.get_editor_property(prop)
        except Exception as e:r['actor_'+prop+'_err']=str(e)
    if c:
        for prop in ('visible','hidden_in_game','min_draw_distance','cached_max_draw_distance','ld_max_draw_distance','allow_cull_distance_volume','forced_lod_model','cast_shadow','cast_hidden_shadow','render_in_main_pass','render_in_depth_pass','owner_no_see','only_owner_see','bounds_scale'):
            try:r[prop]=c.get_editor_property(prop)
            except Exception as e:r[prop+'_err']=str(e)
        try:r['mesh']=c.get_editor_property('static_mesh').get_path_name()
        except:pass
    rows.append(r)
os.makedirs(os.path.dirname(OUT),exist_ok=True)
with open(OUT,'w',encoding='utf-8') as f:json.dump(rows,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(rows,indent=2,ensure_ascii=False,default=str))
