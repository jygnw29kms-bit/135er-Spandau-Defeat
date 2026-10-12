import unreal, os, json, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_spawn_proxy_surface_fix_2026-10-12.json')
out={'ok':False,'errors':[],'starts':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('FINAL load failed')
    actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors=actor_sub.get_all_level_actors()
    proxy=next((a for a in actors if a.get_actor_label()=='NAV_Rathaus_TerrainProxy_v73'),None)
    if not proxy: raise RuntimeError('terrain proxy missing')
    comp=proxy.static_mesh_component
    starts=sorted([a for a in actors if 'LyraPlayerStart' in a.get_class().get_name()],key=lambda a:a.get_actor_label())
    if len(starts)!=2: raise RuntimeError('expected 2 LyraPlayerStarts, got %d'%len(starts))
    for s in starts:
        p=s.get_actor_location()
        a=unreal.Vector(p.x,p.y,p.z+1500.0); b=unreal.Vector(p.x,p.y,p.z-4000.0)
        r=comp.line_trace_component(a,b,True,False)
        hit=r[0]
        hit_z=float(hit.z)
        # Lyra mannequin capsule center needs clearance over surface. 120 cm gives ~30 cm safety above a ~90 cm half-height capsule.
        new_z=hit_z+120.0
        before=[float(p.x),float(p.y),float(p.z)]
        s.set_actor_location(unreal.Vector(p.x,p.y,new_z),False,False)
        out['starts'].append({'label':str(s.get_actor_label()),'surface_z':hit_z,'before':before,'after':[float(p.x),float(p.y),new_z],'clearance_cm':120.0})
    if not lvl.save_current_level(): raise RuntimeError('save_current_level failed')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    out['ok']=True
except Exception as e:
    out['errors'].append(str(e)); out['errors'].append(traceback.format_exc())
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
