import unreal, os, json, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_proxy_runtime_collision_2026-10-12.json')
out={'ok':False,'errors':[],'starts':[],'proxy':{},'trace_methods':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('FINAL load failed')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    proxy=next((a for a in actors if 'TerrainProxy' in a.get_actor_label() or 'NAV_PROXY' in a.get_actor_label()),None)
    if not proxy: raise RuntimeError('terrain proxy actor missing')
    comp=proxy.static_mesh_component
    out['proxy']={'label':str(proxy.get_actor_label()),'location':[float(proxy.get_actor_location().x),float(proxy.get_actor_location().y),float(proxy.get_actor_location().z)],'profile':str(comp.get_collision_profile_name()),'enabled':str(comp.get_collision_enabled()),'pawn':str(comp.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN)),'hidden':str(comp.get_editor_property('hidden_in_game'))}
    out['trace_methods']=[str(n) for n in dir(comp) if 'trace' in n.lower() or 'overlap' in n.lower() or 'collision' in n.lower()]
    starts=sorted([a for a in actors if 'LyraPlayerStart' in a.get_class().get_name()],key=lambda a:a.get_actor_label())
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    for s in starts:
        p=s.get_actor_location(); row={'label':str(s.get_actor_label()),'start':[float(p.x),float(p.y),float(p.z)]}
        a=unreal.Vector(p.x,p.y,p.z+1000); b=unreal.Vector(p.x,p.y,p.z-3000)
        attempts=[]
        for name,args in [('component_line_trace',(a,b,True,False)),('line_trace_component',(a,b,True,False)),('line_trace_component_short',(a,b,True))]:
            fn=getattr(comp,name.split('_short')[0],None)
            if not fn: continue
            try:
                r=fn(*args); attempts.append({'name':name,'repr':repr(r),'type':str(type(r))})
            except Exception as e: attempts.append({'name':name,'error':str(e)})
        try:
            r=unreal.SystemLibrary.line_trace_single(world,a,b,unreal.TraceTypeQuery.ECC_VISIBILITY,True,[],unreal.DrawDebugTrace.NONE,True)
            attempts.append({'name':'system_visibility_complex','repr':repr(r),'type':str(type(r))})
        except Exception as e: attempts.append({'name':'system_visibility_complex','error':str(e)})
        row['attempts']=attempts; out['starts'].append(row)
    out['ok']=True
except Exception as e:
    out['errors'].append(str(e)); out['errors'].append(traceback.format_exc())
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print('REPORT='+REPORT)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
