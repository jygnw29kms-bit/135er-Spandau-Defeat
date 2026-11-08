import json, os, traceback, unreal
SRC='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v79_VISUAL_PLAYABLE_QA'
DST='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v84_GROUND_LOCK_QA'
OBJ=r'C:\Users\anony\Documents\SpandauStrike\SourceData\DGM1\rathaus_dgm_gameplay1000_1000m_513.obj'
REP=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v84_ground_lock_qa.json')
CLEARANCE_CM=120.0
DGM_LABEL='Rathaus_DGM1_GAMEPLAY1000_v86_EXT'
out={'ok':False,'errors':[],'spawns':[],'dgm':{}}

def load_vertices(path):
    v=[]
    with open(path,'r',encoding='utf-8',errors='ignore') as f:
        for line in f:
            if line.startswith('v '):
                p=line.split()
                v.append((float(p[1]),float(p[2]),float(p[3])))
    return v

def nearest_height(vertices,x_cm,y_cm):
    tx=x_cm/100.0; ty=y_cm/100.0
    best=None; bd=1e30
    for x,y,z in vertices:
        d=(x-tx)*(x-tx)+(y-ty)*(y-ty)
        if d<bd:
            bd=d; best=(x,y,z)
    return best[2]*100.0,best,bd**0.5

try:
    verts=load_vertices(OBJ)
    if len(verts)<250000:
        raise RuntimeError('DGM vertex count too small: '+str(len(verts)))
    asset=unreal.EditorAssetLibrary
    if asset.does_asset_exist(DST): asset.delete_asset(DST)
    if not asset.duplicate_asset(SRC,DST):
        raise RuntimeError('duplicate v79 -> v84 failed')
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(DST): raise RuntimeError('load v84 failed')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()

    dgm=None
    spawn_actors=[]
    for a in actors:
        label=a.get_actor_label()
        if label==DGM_LABEL:
            dgm=a
        if label.startswith('SS_FRONTSPAWN_') or label.startswith('SS_SM_SPAWN_'):
            spawn_actors.append(a)

    if len(spawn_actors)!=24:
        raise RuntimeError('expected 24 gameplay spawns, got '+str(len(spawn_actors)))
    if not dgm:
        raise RuntimeError('DGM actor missing: '+DGM_LABEL)

    comp=dgm.get_component_by_class(unreal.StaticMeshComponent)
    if not comp:
        raise RuntimeError('DGM StaticMeshComponent missing')
    comp.set_visibility(True, True)
    comp.set_editor_property('hidden_in_game', False)
    comp.set_collision_profile_name('BlockAll')
    try:
        comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    except Exception as e:
        out['dgm']['collision_enabled_warning']=str(e)
    mesh=comp.get_editor_property('static_mesh')
    if not mesh:
        raise RuntimeError('DGM mesh missing on actor')
    body=mesh.get_editor_property('body_setup')
    if not body:
        raise RuntimeError('DGM body_setup missing')
    body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    asset.save_loaded_asset(mesh,False)
    out['dgm'].update({'label':DGM_LABEL,'profile':'BlockAll','trace':'complex_as_simple','visible':True})

    for a in spawn_actors:
        label=a.get_actor_label()
        loc=a.get_actor_location()
        ground,grid,dist=nearest_height(verts,loc.x,loc.y)
        newz=ground+CLEARANCE_CM
        a.set_actor_location(unreal.Vector(loc.x,loc.y,newz),False,False)
        if label.startswith('SS_FRONTSPAWN_'):
            yaw=180.0 if '_DEFENDER_' in label else 0.0
            a.set_actor_rotation(unreal.Rotator(roll=0.0,pitch=0.0,yaw=yaw),False)
        out['spawns'].append({'label':label,'x':loc.x,'y':loc.y,'old_z':loc.z,'ground_z':ground,'new_z':newz,'grid_dist_m':dist})

    if not lvl.save_current_level(): raise RuntimeError('save v84 failed')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    out['ok']=True
except Exception as e:
    out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REP),exist_ok=True)
with open(REP,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
print(json.dumps(out,indent=2,ensure_ascii=False))
if not out['ok']: raise RuntimeError('v84 ground-lock QA failed')
