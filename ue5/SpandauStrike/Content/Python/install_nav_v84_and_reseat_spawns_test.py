import unreal, os, json, traceback, math
MAP='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_DGM_v83_TEST'
NAV='/Game/SpandauStrike/Maps/Rathaus/Navigation/REAL_v84/SM_RathausSpandau_NAV_PROXY_v84'
REP=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nav_v84_spawns_test.json')
# Bilinear raw-DGM sampler from the same four official tiles used for v83
OX=377956.8271307037; OY=5822062.184676066; OZ=33.45
ROOT=r'C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\SourceData\DGM1'
files=[os.path.join(ROOT,'376_5820','dgm1_33_376_5820_2_be.xyz'),os.path.join(ROOT,'376_5822','dgm1_33_376_5822_2_be.xyz'),os.path.join(ROOT,'378_5820','dgm1_33_378_5820_2_be.xyz'),os.path.join(ROOT,'378_5822','dgm1_33_378_5822_2_be.xyz')]
out={'ok':False,'errors':[],'spawns':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('test map load failed')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    proxy=next((a for a in actors if a.get_actor_label()=='NAV_Rathaus_TerrainProxy_v75' or 'TerrainProxy' in a.get_actor_label()),None)
    if not proxy: raise RuntimeError('terrain proxy actor missing')
    nav=unreal.load_asset(NAV)
    if not nav: raise RuntimeError('v84 nav asset missing')
    c=proxy.static_mesh_component; out['old_proxy_mesh']=c.get_editor_property('static_mesh').get_path_name()
    c.set_static_mesh(nav); c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS); c.set_collision_profile_name('BlockAll')
    c.set_editor_property('can_ever_affect_navigation',True); c.set_visibility(False,True); c.set_hidden_in_game(True)
    proxy.set_actor_label('NAV_Rathaus_TerrainProxy_v84_TEST')
    out['new_proxy_mesh']=c.get_editor_property('static_mesh').get_path_name()
    starts=[a for a in actors if a.get_class().get_name()=='LyraPlayerStart']; starts.sort(key=lambda a:a.get_actor_label())
    if not starts: raise RuntimeError('no LyraPlayerStart')
    # Gather only a tight window around starts to avoid loading the full 16M source points.
    es=[]; ns=[]
    for a in starts:
        p=a.get_actor_location(); es.append(OX+p.x/100.0); ns.append(OY-p.y/100.0)
    emin,emax=min(es)-3,max(es)+3; nmin,nmax=min(ns)-3,max(ns)+3
    pts={}
    for fp in files:
        with open(fp,'r',encoding='utf-8',errors='ignore') as f:
            for line in f:
                try: e,n,z=map(float,line.split()[:3])
                except: continue
                if emin<=e<=emax and nmin<=n<=nmax: pts[(round(e*2),round(n*2))]=z
    def sample(e,n):
        e0=math.floor(e-0.5)+0.5; n0=math.floor(n-0.5)+0.5; e1=e0+1; n1=n0+1
        q=[pts.get((round(e0*2),round(n0*2))),pts.get((round(e1*2),round(n0*2))),pts.get((round(e0*2),round(n1*2))),pts.get((round(e1*2),round(n1*2)))]
        if None in q: raise RuntimeError('missing raw DGM sample '+str((e,n,q)))
        tx=e-e0; ty=n-n0
        return (q[0]*(1-tx)+q[1]*tx)*(1-ty)+(q[2]*(1-tx)+q[3]*tx)*ty
    for a in starts:
        p=a.get_actor_location(); e=OX+p.x/100.0; n=OY-p.y/100.0; surface=(sample(e,n)-OZ)*100.0
        new=unreal.Vector(p.x,p.y,surface+120.0); a.set_actor_location(new,False,False)
        out['spawns'].append({'label':a.get_actor_label(),'xy':[p.x,p.y],'old_z':p.z,'surface_z':surface,'new_z':surface+120.0})
    out['save']=bool(lvl.save_current_level()); unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True); out['ok']=bool(out['save'])
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REP),exist_ok=True)
with open(REP,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))