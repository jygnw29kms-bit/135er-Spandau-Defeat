import unreal,json,os,traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_final_playability_audit.json')
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
out={'ok':False,'map':MAP,'actors':[],'summary':{},'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('FINAL load failed')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    counts={'PlayerStart':0,'NavMeshBoundsVolume':0,'RecastNavMesh':0,'StaticMeshActor':0,'Landscape':0,'BlockingVolume':0,'WorldSettings':0}
    collision_rows=[]
    for a in actors:
        cls=a.get_class().get_name(); label=a.get_actor_label()
        row={'label':label,'class':cls,'location':[a.get_actor_location().x,a.get_actor_location().y,a.get_actor_location().z]}
        for k in list(counts):
            if cls==k or k in cls: counts[k]+=1
        c=a.get_component_by_class(unreal.StaticMeshComponent)
        if c and c.static_mesh:
            row['mesh']=c.static_mesh.get_path_name(); row['collision_profile']=str(c.get_collision_profile_name()); row['collision_enabled']=str(c.get_collision_enabled())
            if 'NO_COLLISION' not in str(c.get_collision_enabled()).upper() and 'NoCollision' not in str(c.get_collision_profile_name()):
                collision_rows.append({'label':label,'mesh':row['mesh'],'profile':row['collision_profile'],'enabled':row['collision_enabled']})
        try:
            o,e=a.get_actor_bounds(False); row['bounds_origin']=[o.x,o.y,o.z]; row['bounds_extent']=[e.x,e.y,e.z]
        except: pass
        out['actors'].append(row)
    out['summary']={'actor_count':len(actors),'counts':counts,'collision_actor_count':len(collision_rows),'collision_actors':collision_rows}
    navbounds=[r for r in out['actors'] if 'NavMeshBoundsVolume' in r['class']]
    out['summary']['nav_bounds']=navbounds
    starts=[r for r in out['actors'] if 'PlayerStart' in r['class']]
    out['summary']['player_starts']=starts
    out['ok']=len(actors)>0 and counts['NavMeshBoundsVolume']>0 and len(collision_rows)>0
except Exception as e:
    out['errors'].append(str(e));out['traceback']=traceback.format_exc()
with open(REPORT,'w',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
unreal.log('[RATHAUS_PLAYABILITY] '+json.dumps({'ok':out['ok'],'summary':out.get('summary',{}),'report':REPORT}))
if not out['ok']: raise RuntimeError('FINAL playability audit failed; see '+REPORT)
