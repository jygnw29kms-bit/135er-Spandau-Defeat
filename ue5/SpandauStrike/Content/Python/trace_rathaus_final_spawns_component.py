import unreal, json, os, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_final_spawn_component_traces.json')
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
out={'ok':False,'map':MAP,'spawns':[],'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('FINAL load failed')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    starts=[a for a in actors if 'PlayerStart' in a.get_class().get_name()]
    ground=[]
    for a in actors:
        c=a.get_component_by_class(unreal.StaticMeshComponent)
        if c and c.static_mesh:
            p=c.static_mesh.get_path_name()
            if 'DGM1_DOP' in p or 'ROADS_DGM' in p:
                ground.append((a,c))
    for s in starts:
        p=s.get_actor_location()
        row={'label':s.get_actor_label(),'spawn':[p.x,p.y,p.z],'components':[]}
        begin=unreal.Vector(p.x,p.y,p.z+2000.0)
        end=unreal.Vector(p.x,p.y,p.z-10000.0)
        best=None
        for ga,c in ground:
            cr={'label':ga.get_actor_label(),'mesh':c.static_mesh.get_path_name()}
            try:
                hit=c.line_trace_component(begin,end,True,False,False)
                cr['line_hit']=bool(hit)
                if hit:
                    loc=hit[0]; normal=hit[1]
                    cr['line_location']=[loc.x,loc.y,loc.z]
                    cr['line_normal']=[normal.x,normal.y,normal.z]
                    cr['drop_from_spawn_cm']=p.z-loc.z
                    if best is None or loc.z>best['z']:
                        best={'actor':ga.get_actor_label(),'z':loc.z,'drop_cm':p.z-loc.z,'method':'line'}
            except Exception as e: cr['line_error']=str(e)
            try:
                shit=c.sphere_trace_component(begin,end,34.0,True,False,False)
                cr['sphere_hit']=bool(shit)
                if shit:
                    sloc=shit[0]; sn=shit[1]
                    cr['sphere_location']=[sloc.x,sloc.y,sloc.z]
                    cr['sphere_normal']=[sn.x,sn.y,sn.z]
                    cr['sphere_drop_from_spawn_cm']=p.z-sloc.z
            except Exception as e: cr['sphere_error']=str(e)
            row['components'].append(cr)
        row['best_ground']=best
        row['safe_ground_below']=bool(best and best['drop_cm']>=-100.0 and best['drop_cm']<=2000.0)
        out['spawns'].append(row)
    out['spawn_count']=len(starts)
    out['ground_component_count']=len(ground)
    out['safe_spawn_count']=sum(1 for r in out['spawns'] if r['safe_ground_below'])
    out['ok']=len(starts)>0 and out['safe_spawn_count']==len(starts)
except Exception as e:
    out['errors'].append(str(e));out['traceback']=traceback.format_exc()
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,ensure_ascii=False,indent=2)
unreal.log('[RATHAUS_COMPONENT_SPAWN_TRACE] '+json.dumps({'ok':out['ok'],'spawn_count':out.get('spawn_count'),'safe_spawn_count':out.get('safe_spawn_count'),'spawns':out.get('spawns'),'report':REPORT}))
if not out['ok']: raise RuntimeError('Component spawn trace failed; see '+REPORT)
