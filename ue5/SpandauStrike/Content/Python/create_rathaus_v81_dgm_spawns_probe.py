import json, os, traceback, unreal
SRC='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v80_NOFOG_PROBE'
DST='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v81_DGM_SPAWNS_PROBE'
OBJ=r'C:\Users\anony\Documents\SpandauStrike\SourceData\DGM1\rathaus_dgm_gameplay1000_1000m_513.obj'
REP=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v81_dgm_spawns_probe.json')
CLEARANCE_CM=120.0
out={'ok':False,'errors':[],'spawns':[]}

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
    if len(verts)<250000: raise RuntimeError('DGM vertex count too small: '+str(len(verts)))
    asset=unreal.EditorAssetLibrary
    if asset.does_asset_exist(DST): asset.delete_asset(DST)
    if not asset.duplicate_asset(SRC,DST): raise RuntimeError('duplicate v80 -> v81 failed')
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(DST): raise RuntimeError('load v81 failed')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    front=[a for a in actors if a.get_actor_label().startswith('SS_FRONTSPAWN_')]
    if len(front)!=16: raise RuntimeError('expected 16 front spawns, got '+str(len(front)))
    for a in front:
        loc=a.get_actor_location()
        ground,grid,dist=nearest_height(verts,loc.x,loc.y)
        newz=ground+CLEARANCE_CM
        a.set_actor_location(unreal.Vector(loc.x,loc.y,newz),False,False)
        yaw=180.0 if '_DEFENDER_' in a.get_actor_label() else 0.0
        a.set_actor_rotation(unreal.Rotator(roll=0.0,pitch=0.0,yaw=yaw),False)
        out['spawns'].append({'label':a.get_actor_label(),'x':loc.x,'y':loc.y,'old_z':loc.z,'ground_z':ground,'new_z':newz,'grid':[grid[0],grid[1],grid[2]],'grid_dist_m':dist})
    if not lvl.save_current_level(): raise RuntimeError('save v81 failed')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    out['ok']=True
except Exception as e:
    out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REP),exist_ok=True)
with open(REP,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
print(json.dumps(out,indent=2,ensure_ascii=False))
if not out['ok']: raise RuntimeError('v81 DGM spawn probe failed')
