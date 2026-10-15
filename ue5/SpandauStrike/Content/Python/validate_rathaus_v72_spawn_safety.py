import unreal, os, json, math
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v72_FIRST_PLAY'
out=os.path.join(unreal.Paths.project_saved_dir(),'Reports','v72_spawn_safety_validation.json')
lev=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not lev.load_level(MAP): raise RuntimeError('load failed')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
starts=[a for a in actors if 'PlayerStart' in a.get_class().get_name()]
pads=[a for a in actors if a.get_actor_label().startswith('SS_FIRSTPLAY_SPAWN_SAFETY_PAD_')]
rows=[]; used=set()
for s in starts:
    sl=s.get_actor_location(); candidates=[]
    for p in pads:
        if p in used: continue
        pl=p.get_actor_location(); candidates.append((math.hypot(sl.x-pl.x,sl.y-pl.y),p))
    dxy,p=min(candidates,key=lambda t:t[0]); used.add(p)
    pl=p.get_actor_location(); sc=p.get_actor_scale3d(); prof=str(p.static_mesh_component.get_collision_profile_name())
    rows.append({'start':s.get_actor_label(),'pad':p.get_actor_label(),'dxy':dxy,'dz':sl.z-pl.z,'scale':[sc.x,sc.y,sc.z],'profile':prof})
valid=len(starts)==8 and len(pads)==8 and all(r['dxy']<1.0 and abs(r['dz']-100.0)<0.1 and r['scale']==[6.0,6.0,0.2] and r['profile']=='BlockAll' for r in rows)
os.makedirs(os.path.dirname(out),exist_ok=True); json.dump({'valid':valid,'rows':rows},open(out,'w'),indent=2)
print('V72_SPAWN_SAFETY='+json.dumps({'valid':valid,'starts':len(starts),'pads':len(pads)}))
if not valid: raise RuntimeError('spawn safety validation failed')
