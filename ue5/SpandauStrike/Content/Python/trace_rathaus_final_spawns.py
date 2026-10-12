import unreal,json,os,traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_final_spawn_traces.json')
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
out={'ok':False,'map':MAP,'spawns':[],'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('FINAL load failed')
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    starts=[a for a in actors if 'PlayerStart' in a.get_class().get_name()]
    for a in starts:
        p=a.get_actor_location(); begin=unreal.Vector(p.x,p.y,p.z+2000.0); end=unreal.Vector(p.x,p.y,p.z-10000.0)
        row={'label':a.get_actor_label(),'spawn':[p.x,p.y,p.z],'trace_start':[begin.x,begin.y,begin.z],'trace_end':[end.x,end.y,end.z]}
        try:
            hit=unreal.SystemLibrary.line_trace_single(world,begin,end,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[a],unreal.DrawDebugTrace.NONE,True)
            row['raw_type']=str(type(hit)); row['raw']=str(hit)
            if isinstance(hit,tuple) and len(hit)>=2:
                row['hit']=bool(hit[0]); hr=hit[1]
                if row['hit']:
                    loc=hr.impact_point if hasattr(hr,'impact_point') else hr.location
                    row['impact']=[loc.x,loc.y,loc.z]
                    row['drop_cm']=p.z-loc.z
                    try: row['actor']=hr.hit_actor.get_actor_label() if hr.hit_actor else None
                    except: pass
            else: row['hit']=False
        except Exception as e:
            row['trace_error']=str(e)
        out['spawns'].append(row)
    good=[r for r in out['spawns'] if r.get('hit') and r.get('drop_cm',999999)<500.0 and r.get('drop_cm',-999999)>-2500.0]
    out['ok']=len(starts)>0 and len(good)==len(starts)
    out['good_spawn_count']=len(good); out['spawn_count']=len(starts)
except Exception as e:
    out['errors'].append(str(e));out['traceback']=traceback.format_exc()
with open(REPORT,'w',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
unreal.log('[RATHAUS_SPAWN_TRACE] '+json.dumps(out))
if not out['ok']: raise RuntimeError('Spawn trace audit failed; see '+REPORT)
