import unreal, os, json, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_dgm_vs_proxy_collision_2026-10-12.json')
out={'ok':False,'rows':[],'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); assert lvl.load_level(MAP)
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    dgm=next(a for a in actors if a.get_actor_label()=='Rathaus_DGM1_DOP2025_v61')
    proxy=next(a for a in actors if a.get_actor_label()=='NAV_Rathaus_TerrainProxy_v73')
    starts=sorted([a for a in actors if 'LyraPlayerStart' in a.get_class().get_name()],key=lambda a:a.get_actor_label())
    for s in starts:
        p=s.get_actor_location(); a=unreal.Vector(p.x,p.y,2000); b=unreal.Vector(p.x,p.y,-3000)
        row={'start':str(s.get_actor_label()),'xy':[float(p.x),float(p.y)]}
        for key,actor in [('dgm',dgm),('proxy',proxy)]:
            c=actor.static_mesh_component
            try:
                r=c.line_trace_component(a,b,True,False)
                row[key]={'hit':[float(r[0].x),float(r[0].y),float(r[0].z)],'normal':[float(r[1].x),float(r[1].y),float(r[1].z)],'profile':str(c.get_collision_profile_name()),'enabled':str(c.get_collision_enabled())}
            except Exception as e: row[key]={'error':str(e)}
            sm=c.static_mesh
            bs=sm.get_editor_property('body_setup') if sm else None
            if bs:
                row[key]['trace_flag']=str(bs.get_editor_property('collision_trace_flag'))
                try: row[key]['convex_count']=len(bs.get_editor_property('agg_geom').get_editor_property('convex_elems'))
                except: pass
        out['rows'].append(row)
    out['ok']=True
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
open(REPORT,'w',encoding='utf-8').write(json.dumps(out,indent=2,ensure_ascii=False,default=str))
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
